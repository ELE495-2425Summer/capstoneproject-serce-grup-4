from sensors import IMU, Encoder, Ultrasonik
import time

imu = IMU()
encoder = Encoder(left_pin=17, right_pin=18)
ultra = Ultrasonik(trig_pin=5, echo_pin=6)


try:
    while True:
        speed = encoder.get_speed()
        accel_x = imu.get_linear_accel_x()
        accel_y = imu.get_linear_accel_y()
        distance = ultra.measure_distance()
        yaw_deg = imu.get_yaw()

        print(f"Speed: {speed:.2f} cm/s")
        if distance == -1:
            print("Distance: [ölçülemedi]")
        else:
            print(f"Distance: {distance:.2f} cm")
        print(f"Accel X: {accel_x:.2f} cm/s²")
        print(f"Accel Y: {accel_y:.2f} cm/s²\n")
        print(f"Yaw: {yaw_deg:.2f}°")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program durduruldu.")
finally:
    imu.cleanup()
    encoder.cleanup()
    ultra.cleanup()
