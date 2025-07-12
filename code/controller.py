import time
import numpy as np
from sensors import IMU, Ultrasonik
from kalman_filter import Kalman1D
import RPi.GPIO as GPIO

IN1 = 17
IN2 = 27
ENA = 18

IN3 = 23
IN4 = 22
ENB = 13

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)
GPIO.setup([ENA, ENB], GPIO.OUT)

pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)
pwm_left.start(0)
pwm_right.start(0)

imu = IMU()
ultra = Ultrasonik(trig_pin=5, echo_pin=6)  # PIN'leri senin bağlantılarına göre değiştir
kalman = Kalman1D()

def set_motor(left_pwm, right_pwm):
    if left_pwm >= 0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)

    if right_pwm >= 0:
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)

    pwm_left.ChangeDutyCycle(min(abs(left_pwm), 100))
    pwm_right.ChangeDutyCycle(min(abs(right_pwm), 100))

    print(f"[PWM] Sol: {left_pwm:.1f} | Sağ: {right_pwm:.1f}")

def pid_controller(target_value, get_measured_value, control_type="distance", duration_limit=None):
    Kp = 0.08 * 0.6
    Ki = 0.05 * 0.6
    Kd = 0.05 * 0.6

    error = 0
    prev_error = 0
    integral = 0
    derivative = 0

    max_pwm = 20
    min_pwm = 14

    start_time = time.time()
    prev_time = start_time

    while True:
        now = time.time()
        dt = now - prev_time
        prev_time = now

        measured = get_measured_value()

        if measured == -1:
            continue

        if control_type == "distance":
            error = target_value - measured
        elif control_type == "angle":
            error = target_value - measured
        elif control_type == "duration":
            error = 15000
        elif control_type == "obstacle":
            error = measured - target_value
        else:
            raise ValueError("control_type 'distance', 'angle' ya da 'duration' olmalı")

        integral += error * dt
        derivative = (error - prev_error) / dt if dt > 0 else 0
        control = Kp * error + Ki * integral + Kd * derivative
        if control_type == "obstacle":
            control = Kp * error + Ki * integral - Kd * derivative
        prev_error = error

        pwm = np.clip(abs(control), min_pwm, max_pwm)

        if control_type == "distance" or control_type == "duration" or control_type == "obstacle":
            if error > 0:
                set_motor(pwm, pwm)
            else:
                set_motor(0, 0)

        elif control_type == "angle":
            if error > 0:
                set_motor((pwm+15), -(pwm+15))
            else:
                set_motor(-(pwm+15), (pwm+15))

        print(f"[{control_type.upper()}] Hedef: {target_value} | Ölçüm: {measured:.2f} | Hata: {error:.2f} | PWM: {pwm:.2f}")

        if control_type in ["distance", "obstacle"] and error < 5:
            break
        if control_type in ["angle"] and abs(error) < 2:
            break
        if control_type == "duration" and duration_limit and (now - start_time >= duration_limit):
            break

        time.sleep(0.05)

    set_motor(0, 0)
    print(f"[{control_type.upper()}] Görev tamamlandı.")


