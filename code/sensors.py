import smbus2
import pigpio
import RPi.GPIO as GPIO
from collections import deque
import time



class IMU:
    def __init__(self, address=0x68):
        self.kalibrasyon_flag = False
        self.address = address
        self.bus = smbus2.SMBus(1)
        self.bus.write_byte_data(self.address, 0x6B, 0)
        time.sleep(0.1)

        self.gyro_bias = [0.0, 0.0, 0.0]
        self.accel_bias = [0.0, 0.0, 0.0]
        self._calibrate()

        self.last_time = time.time()
        self.yaw = 0.0

        self.ax_history = deque(maxlen=10)
        self.ay_history = deque(maxlen=10)

    def _calibrate(self, n=200):
        gx_list, gy_list, gz_list = [], [], []
        ax_list, ay_list, az_list = [], [], []

        print("IMU kalibrasyonu yapılıyor... Cihazı sabit tutun.")
        for _ in range(n):
            ax, ay, az = self.get_acceleration(raw=True)
            gx, gy, gz = self.get_gyro_raw()
            ax_list.append(ax)
            ay_list.append(ay)
            az_list.append(az)
            gx_list.append(gx)
            gy_list.append(gy)
            gz_list.append(gz)
            time.sleep(0.005)

        self.accel_bias = [
            sum(ax_list) / n,
            sum(ay_list) / n,
            (sum(az_list) / n) - 1.0
        ]
        self.gyro_bias = [
            sum(gx_list) / n,
            sum(gy_list) / n,
            sum(gz_list) / n
        ]
        print("Kalibrasyon tamamlandı.")

        self.kalibrasyon_flag = True

    def read_word(self, reg):
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            val = -((65535 - val) + 1)
        return val

    def get_acceleration(self, raw=False):
        ax = self.read_word(0x3B) / 16384.0
        ay = self.read_word(0x3D) / 16384.0
        az = self.read_word(0x3F) / 16384.0
        if raw:
            return ax, ay, az
        return (
            ax - self.accel_bias[0],
            ay - self.accel_bias[1],
            az - self.accel_bias[2]
        )

    def get_gyro_raw(self):
        gx = self.read_word(0x43) / 131.0
        gy = self.read_word(0x45) / 131.0
        gz = self.read_word(0x47) / 131.0
        return gx, gy, gz

    def get_gyro_z(self):
        _, _, gz = self.get_gyro_raw()
        return gz - self.gyro_bias[2]

    def get_yaw(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        gz = self.get_gyro_z()
        if abs(gz) < 0.5:
            gz = 0
        self.yaw += gz * dt
        return self.yaw

    def get_linear_accel_x(self):
        ax, _, _ = self.get_acceleration()
        ax_cm_s2 = ax * 981
        self.ax_history.append(ax_cm_s2)
        return sum(self.ax_history) / len(self.ax_history)

    def get_linear_accel_y(self):
        _, ay, _ = self.get_acceleration()
        ay_cm_s2 = ay * 981
        self.ay_history.append(ay_cm_s2)
        return sum(self.ay_history) / len(self.ay_history)

    def reset_yaw(self):
        self.yaw = 0.0
        self.last_time = time.time()


    def cleanup(self):
        self.bus.close()


class Encoder:
    def __init__(self, left_pin, right_pin):
        self.pi = pigpio.pi()
        self.left_pin = left_pin
        self.right_pin = right_pin
        self.left_count = 0
        self.right_count = 0
        self.last_time = time.time()
        self.last_left_count = 0
        self.last_right_count = 0

        self.pi.set_mode(self.left_pin, pigpio.INPUT)
        self.pi.set_mode(self.right_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.left_pin, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.right_pin, pigpio.PUD_UP)

        self.pi.callback(self.left_pin, pigpio.FALLING_EDGE, self._left_callback)
        self.pi.callback(self.right_pin, pigpio.FALLING_EDGE, self._right_callback)

    def _left_callback(self, gpio, level, tick):
        self.left_count += 1

    def _right_callback(self, gpio, level, tick):
        self.right_count += 1

    def get_speed(self):
        now = time.time()
        dt = now - self.last_time
        if dt == 0:
            return 0.0

        dl = self.left_count - self.last_left_count
        dr = self.right_count - self.last_right_count

        self.last_time = now
        self.last_left_count = self.left_count
        self.last_right_count = self.right_count

        pulses = (dl + dr) / 2
        cm_per_pulse = 20.42 / 20
        speed_cm_per_s = (pulses * cm_per_pulse) / dt
        return speed_cm_per_s

    def reset_counts(self):
        self.left_count = 0
        self.right_count = 0
        self.last_left_count = 0
        self.last_right_count = 0
        self.last_time = time.time()

    def cleanup(self):
        self.pi.stop()


class Ultrasonik:
    def __init__(self, trig_pin, echo_pin):
        self.trig = trig_pin
        self.echo = echo_pin
        self.history = deque(maxlen=7)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trig, False)
        time.sleep(0.1)

    def measure_distance(self):
        GPIO.output(self.trig, False)
        time.sleep(0.002)

        GPIO.output(self.trig, True)
        time.sleep(0.000015)
        GPIO.output(self.trig, False)

        timeout = 0.03

        t0 = time.time()
        while GPIO.input(self.echo) == 0:
            if time.time() - t0 > timeout:
                print("⛔ ECHO başlamadı")
                return -1
        pulse_start = time.time()

        while GPIO.input(self.echo) == 1:
            if time.time() - pulse_start > timeout:
                print("⛔ ECHO çok uzun sürdü")
                return -1
        pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2

        if distance < 1.5 or distance > 400:
            print(f"⚠️ Geçersiz mesafe: {distance:.2f} cm")
            self.history.clear()
            return -1

        self.history.append(distance)
        return round(sum(self.history) / len(self.history), 2)

    def cleanup(self):
        GPIO.cleanup([self.trig, self.echo])
