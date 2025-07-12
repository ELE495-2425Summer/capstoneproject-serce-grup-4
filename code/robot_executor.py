from speech_io import speak, send_to_ui
import numpy as np
from sensors import Encoder
import controller
from controller import imu, ultra, kalman
import time

encoder = Encoder(left_pin=24, right_pin=25)

distance_cm = [0]
prev_time = time.time()

def get_kalman_distance():
    global prev_time
    now = time.time()
    dt = now - prev_time
    prev_time = now

    measured_speed = encoder.get_speed()  
    accel_x = imu.get_linear_accel_x()    

    z = np.array([[measured_speed], [-accel_x]])

    kalman_output = kalman.execute(dt, z)

    vx = kalman_output[1][0]
    distance_cm[0] += vx * dt

    return distance_cm[0]

def robot_move_forward(distance=None, duration=None):    
    if distance is not None:
        print(f"Robot {distance} metre ({distance * 100:.0f} cm) ileri gidiyor.")
        controller.pid_controller(distance * 100, get_kalman_distance, control_type="distance")
    elif duration is not None:
        print(f"Robot {duration} saniye ileri gidiyor.")
        controller.pid_controller(0, lambda: 0, control_type="duration", duration_limit=duration)

def robot_turn(direction, angle_deg):
    print(f"Robot {direction} yönüne {angle_deg} derece dönüyor.")
    current_yaw = imu.get_yaw()
    if direction == "left":
        target = current_yaw + angle_deg
    elif direction == "right":
        target = current_yaw - angle_deg
    else:
        print("Hatalı yön:", direction)
        return
    controller.pid_controller(target, imu.get_yaw, control_type="angle")

    

def robot_move_until_obstacle():
    print("Robot engel görene kadar ilerliyor.")
    controller.pid_controller(20, ultra.measure_distance, control_type="obstacle")

def robot_wait(duration):
    print(f"Robot {duration} saniye bekliyor.")
    time.sleep(duration)

def robot_stop():
    print("Robot duruyor.")
    controller.set_motor(0, 0)

def execute_command(command):
    if not isinstance(command, dict):
        speak("Üzgünüm, komutu anlayamadım.")
        print("Bilinmeyen komut (dict değil):", command)
        return

    if "error" in command:
        speak(f"Üzgünüm, bir hata oluştu: {command['error']}")
        print(f"Hata komutu: {command['error']}")
        return

    action = command.get("action")

    if action == "move_forward":
        distance = command.get("distance_m")
        duration = command.get("duration_s")
        if distance is not None:
            speak(f"Şimdi {distance} metre ileri gidiyorum, lütfen bekleyin.")
            send_to_ui(f"Aktif Komut: {distance} metre ileri gidiliyor.")
            robot_move_forward(distance=(distance+get_kalman_distance()/100))
            send_to_ui(f"Gecmis Komut: {distance} metre ileri git.")
            send_to_ui(f"Aktif Komut: Araç duruyor.")
            speak("İleri gitme işlemi tamamlandı.")
        elif duration is not None:
            speak(f"{duration} saniye boyunca ileri gidiyorum, lütfen bekleyin.")
            send_to_ui(f"Aktif Komut: {duration} saniye ileri gidiliyor.")
            robot_move_forward(duration=duration)
            send_to_ui(f"Gecmis Komut: {duration} saniye ileri git.")
            send_to_ui(f"Aktif Komut: Araç duruyor.")
            speak("İleri gitme işlemi tamamlandı.")

    elif action == "turn":
        direction = command.get("direction")
        angle_deg = command.get("angle_deg")
        if(direction == "right"):
            speak(f"{angle_deg} derece sağ yönüne dönüyorum, biraz bekleyin.")
            send_to_ui(f"Aktif Komut: {angle_deg} derece sağ yönüne dönülüyor.")
        elif(direction == "left"):
            speak(f"{angle_deg} derece sol yönüne dönüyorum, biraz bekleyin.")
            send_to_ui(f"Aktif Komut: {angle_deg} derece sol yönüne dönülüyor.")
        robot_turn(direction, angle_deg)
        if(direction == "right"):
            send_to_ui(f"Gecmis Komut: {angle_deg} derece sağ yönüne dön.")
            send_to_ui(f"Aktif Komut: Araç duruyor.")
        elif(direction == "left"):
            send_to_ui(f"Gecmis Komut: {angle_deg} derece sol yönüne dön.")
            send_to_ui(f"Aktif Komut: Araç duruyor.")
        speak("Dönme işlemi tamamlandı.")

    elif action == "move_until_obstacle":
        speak("Engel görene kadar ilerleyeceğim, lütfen bekleyin.")
        send_to_ui(f"Aktif Komut: Engel görene kadar ilerleniyor.")
        robot_move_until_obstacle()
        send_to_ui(f"Gecmis Komut: Engel görene kadar ilerle.")
        send_to_ui(f"Aktif Komut: Araç duruyor.")
        speak("Engel algılandı, durdum.")

    elif action == "wait":
        duration = command.get("duration_s")
        speak(f"{duration} saniye kadar bekleyeceğim.")
        send_to_ui(f"Aktif Komut: Bekleniyor.")
        robot_wait(duration)
        send_to_ui(f"Gecmis Komut: Bekle.")
        send_to_ui(f"Aktif Komut: Araç duruyor.")
        speak("Bekleme süresi tamamlandı.")

    elif action == "stop":
        speak("Hemen duruyorum.")
        send_to_ui(f"Aktif Komut: Araç duruyor.")
        robot_stop()
        send_to_ui(f"Gecmis Komut: Dur.")
        send_to_ui(f"Aktif Komut: Araç duruyor.")
        speak("Robot durdu.")

    else:
        speak("Üzgünüm, bu komutu anlayamadım.")
        send_to_ui(f"Aktif Komut: Bilinmeyen komut.")
        print("Bilinmeyen komut:", command)




def execute_command_list(command_list):
    if not isinstance(command_list, list):
        execute_command(command_list)
        return

    for cmd in command_list:
        execute_command(cmd)