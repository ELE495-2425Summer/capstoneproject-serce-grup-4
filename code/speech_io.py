import speech_recognition as sr
import wave
import openai
import io
from gtts import gTTS
import pygame
import os
import socket
import json

pc_ip = "192.168.0.2"

def send_to_ui(message: str):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((pc_ip, 5050))  
        s.sendall(message.encode())
        s.close()
    except Exception as e:
        print(f"UI bağlantı hatası: {e}")

def send_to_gui(yaw, distance):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((pc_ip, 5051))
        s.sendall(f"{yaw},{distance}\n".encode())
        s.close()
    except Exception as e:
        print("UI bağlantı hatası:", e)

openai.api_key = os.getenv("OPENAI_API_KEY", "sk-XX")

def speak(text: str):
    tts = gTTS(text=text, lang='tr')
    mp3_path = "komut.mp3"
    tts.save(mp3_path)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path) 
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()

    os.remove(mp3_path)

def listen() -> sr.AudioData:
    send_to_ui("Komut Durumu: False")
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = False
    with sr.Microphone(sample_rate=16000) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("KOMUT VER!!!")
        send_to_ui("Komut Durumu: True")
        audio = recognizer.listen(source)
        print("KOMUT ALGILANDI!!!")
        send_to_ui("Komut Durumu: False")

    audio_data = audio.get_raw_data()
    with wave.open("azure_input.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(audio_data)

    return audio

def transcribe(audio: sr.AudioData) -> str:
    wav_io = io.BytesIO(audio.get_wav_data())
    wav_io.name = "audio.wav"
    wav_io.seek(0)
    result = openai.audio.transcriptions.create(
        model="whisper-1",
        file=wav_io,
        language="tr"
    )
    return result.text.strip()

def correct(text: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Kullanıcıdan gelen sesli komutu sadece sade ve düzgün Türkçeye çevir. Eğer bunu yapabildiysen düzeltilmiş şekilde ver promptu."
                    "Komut zaten düzgün de olsa sadece komutu yaz. "
                    "Açıklama, bilgi veya yorum yapma. Sadece net komutu döndür. "
                    "Gelen cümle komut olmasa mesela bilgilendirme olsa dahi ekrana yazdır."
                    "Öngel olarak anladığın zaman onu Engel olarak değiştir."
                )
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip().strip('"')
