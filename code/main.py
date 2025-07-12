import os
import io
import time
import json
import threading
import numpy as np
import openai

from speech_io import listen, speak, send_to_ui, send_to_gui
from command_parser import komutu_jsona_cevir, komutu_dogrula
from speaker_verification import verify_speaker
from robot_executor import execute_command_list
from robot_executor import imu, get_kalman_distance

os.chdir("/home/bitirme/Desktop/robot_code")

def update_map():
    while True:
        try:
            yaw = imu.get_yaw()
            loc = get_kalman_distance()
            print(f"[Map] Yaw: {yaw:.2f}, Loc: {loc:.2f}")
            send_to_gui(yaw, loc)
        except Exception as e:
            print(f"[Map] Güncelleme hatası: {e}")
        time.sleep(0.25)


def transcribe_from_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        wav_io = io.BytesIO(f.read())
    wav_io.name = "audio.wav"
    wav_io.seek(0)

    result = openai.audio.transcriptions.create(
        model="whisper-1",
        file=wav_io,
        language="tr"
    )
    return result.text.strip()


def main():
    if imu.kalibrasyon_flag:
        kalman_thread = threading.Thread(target=update_map, daemon=True)
        kalman_thread.start()

        while True:
            try:
                print("İcerdeyim.")
                audio = listen()
                print("İcerdeyim 2.")
                audio_file_path = "son_ses_kaydi.wav"
                with open(audio_file_path, "wb") as f:
                    f.write(audio.get_wav_data())

                speaker = verify_speaker(audio_file_path)
                if speaker == "unknown":
                    print("🚫 Bu ses bir grup üyesine ait değil!")
                    speak("Bu ses bir grup üyesine ait değil. Komut işlenmedi.")
                    send_to_ui("Arac Durum: Komut işlenmedi.")
                    send_to_ui("Komut Veren: unknown")
                    os.remove(audio_file_path)
                    continue

                send_to_ui(f"Komut Veren: {speaker}")
                speak(f"{speaker} komut verdi. İşleniyor.")

                komut_metni = transcribe_from_file(audio_file_path)
                send_to_ui(f"Sesli Komut: {komut_metni}")
                speak(f"Verilen sesli komut: {komut_metni}")
                os.remove(audio_file_path)

                json_komutlar = komutu_jsona_cevir(komut_metni)
                komutu_dogrula(json_komutlar)
                arac_komut = json.dumps(json_komutlar, ensure_ascii=False)
                send_to_ui(f"Arac Komut: {arac_komut}")

                speak("Komutlar uygulanıyor.")
                send_to_ui("Arac Durum: Komutlar uygulanıyor")
                execute_command_list(json_komutlar)
                send_to_ui("Arac Durum: Tüm komutlar tamamlandı.")
                send_to_ui("Aktif Komut: Aktif görev yok. Araç duruyor.")
                send_to_ui("Sesli Komut: Yeni komutlar bekleniyor.")
                send_to_ui("Arac Komut: Yeni komutlar bekleniyor.")
                speak("Tüm komutlar tamamlandı.")

            except Exception as e:
                print(f"⚠️ Hata oluştu: {e}")
                send_to_ui("Arac Durum: Bir hata oluştu.")
                speak("Bir hata oluştu. Lütfen tekrar deneyin.")

            print("\n------------------------------\n")


if __name__ == "__main__":
    main()
