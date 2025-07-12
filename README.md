# TOBB ETÜ ELE495 - Capstone Project

# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Acknowledgements](#acknowledgements)

## Introduction
This project focuses on developing an autonomous mini vehicle capable of understanding and executing Turkish voice commands given in natural language. It combines speech recognition, natural language processing, and microcontroller-based motion control to enable the system to interpret user instructions and respond with appropriate movements. The importance of this project lies in its potential applications in voice-controlled robotics, smart mobility systems, and human-machine interaction in Turkish-speaking contexts. As an outcome, it can contribute to advancements in localized AI systems, enhance accessibility, and serve as a foundation for more complex autonomous systems.

Moreover, mini vehicle provides voice during the actions which is called as text-to-speech (TTS) API. Real-time voice feedback is also in natural toned, Turkish language. 
Mini vehicle separates the commands according to it’s capacity and abilities. It responds to convenient commands with proper actions and voice. If command is inconvenient for requirements and abilities, vehicle states that circumstance. Raspberry PI 4 microcontroller is used for web applications, real-time status display, recognized speech, translated commands, and action history. An interface is developed for presentation of these applications. It is equipped with Wi-Fi communication. Therefore, standard communication protocol TCP is used. In addition, GPT AI Service is used for command interpretation. Manufacturing budget is constrained with 20.000 TL.

## Features

### Hardware Components

- [Raspberry Pi 4 Model B - 4GB](https://robolinkmarket.com/raspberry-pi-4-model-b-4gb)
- [L298N Motor Driver](https://robolinkmarket.com/l298n-motor-surucu-karti)
- 4x [DC Motors with Wheels](https://robolinkmarket.com/motor-ve-tekerlek-seti)
- [MPU6050 IMU Sensor](https://robolinkmarket.com/mpu6050-ivme-ve-gyro-sensor-karti)
- [HC-SR04 Ultrasonic Sensors](https://robolinkmarket.com/hc-sr04-arduino-ultrasonic-mesafe-sensoru)
- [USB Microphone](https://www.trendyol.com/torima/2-adet-kablosuz-yaka-mikrofonu-typ-c-2-li-mini-mikrofon-k9-p-341885980?boutiqueId=61)
- [USB Speaker](https://www.trendyol.com/odseven/raspberry-pi-icin-mini-harici-usb-stereo-hoparlor-p-353442163)
- [Wi-Fi Router](https://www.vatanbilgisayar.com/tenda-mf3-150mbps-4g-lte-tasinabilir-kablosuz-n-router.html)
- 4x [Lithium-Ion 21700 cells](https://robolinkmarket.com/tenpower-inr21700-50me-37v-5000-mah-li-ion-sarjli-pil-147a)
- [Powerbank](https://www.vatanbilgisayar.com/anker-321-maggo-5-000mah-manyetik-powerbank-beyaz.html)
- [Micro SD Card for Raspberry](https://www.vatanbilgisayar.com/samsung-evo-plus-64-gb-adaptorlu-hafiza-karti-160mb-s.html)
- 4x [IR Speed Sensor](https://www.ubuy.com.tr/tr/product/5H92RF6-daoki-5pcs-speed-measuring-sensor-ir-infrared-slotted-optical-optocoupler-module-photo-interrupter-sensor-for-motor-speed-detection-or-arduino-with-en?ref=hm-google-redirect)
- [4S BMS](http://robolinkmarket.com/4wd-cok-amacli-mobil-robot-platformu-seffaf)
- 2x [Mobile Vehicle Platform](https://robolinkmarket.com/4wd-cok-amacli-mobil-robot-platformu-seffaf)
  
### Operating System & Software Stack
- **OS:** [Raspbian OS (Lite)](https://www.raspberrypi.com/software/) 
- **Language:** Python 3.10
- **Core Libraries:**
  - `resemblyzer`, `gTTS`, `pygame`
  - `openai`, `requests`, `pydantic`
  - `numpy`, `RPi.GPIO`, `pigpio`, `smbus2`
  - Optional: `Flask` for UI integration

### System Modules
- `main.py` – Main orchestrator for the control flow
- `speech_io.py` – Voice input, Whisper transcription, GPT-4 text correction, and audio feedback
- `speaker_verification.py` – Uses Resemblyzer for speaker embedding extraction and cosine similarity to verify if the speaker matches any of the registered users
- `command_parser.py` – Converts speech text to structured JSON commands via GPT-4
- `robot_executor.py` – Executes structured commands (e.g., move, turn, wait)
- `controller.py` – GPIO motor control and PID regulation
- `sensors.py` – Manages IMU, ultrasonic sensors, and wheel encoders
- `kalman_filter.py` – 1D Kalman filter for position and velocity estimation

### Services
- **[Azure Cognitive Services](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices):**  
  - Speaker verification to restrict access to authorized users
- **[OpenAI Whisper & GPT-4](https://openai.com/tr-TR/index/whisper/):**  
  - Whisper transcribes speech to Turkish text  
  - GPT-4 parses commands into structured JSON actions
- **Socket-Based UI Communication:**  
  - Real-time status logs and command updates sent to a UI over TCP
- **[Voice Feedback System](https://cloud.google.com/text-to-speech):**  
  - gTTS and speaker output for interactive Turkish responses


## Installation
### Assembly Instructions

1. **Chassis Setup:**
   - Mount the 4 DC motors onto the two-layer mobile vehicle platform using the provided brackets and screws.
   - Attach the wheels securely to the motors.
   - Fix the L298N motor driver onto the chassis using double-sided tape or screws.

2. **Motor Wiring:**
   - Connect each motor’s wires to the L298N output terminals. Connections of keft and right motor's wires are in the same terminal. (OUT1–OUT4).
   - Connect ENA, ENB, IN1–IN4 pins of L298N to Raspberry Pi GPIOs (refer to `controller.py` for the specific pins).

3. **Battery and Power Management:**
   - Connect 4x 21700 Lithium-Ion cells to the 4S BMS circuit.
   - Use a step-down voltage regulator (optional) to safely power the L298N and motors.
   - Power the Raspberry Pi using the Powerbank via USB-C.

4. **Sensor Installation:**
   - **MPU6050 IMU**: Connect via I2C (SDA/SCL) pins to Raspberry Pi (usually GPIO 2 and 3).
   - **HC-SR04**: Mount on the front of the vehicle, and connect TRIG and ECHO pins to GPIO (e.g., 5 and 6).
   - **IR Speed Sensors**: Position each sensor near a motor's wheel encoder for speed measurement. Connect signal pins to GPIO (e.g., 17 and 18).

5. **Audio Interface:**
   - Plug in the USB microphone and USB speaker into Raspberry Pi’s USB ports.
   - Ensure the microphone is configured as the default audio input device.

6. **Wi-Fi & Connectivity:**
   - Set up the portable Wi-Fi router and connect the Raspberry Pi to its network.
   - This allows remote access to the logging interface and command control.

7. **Final Touches:**
   - Insert the microSD card into the Raspberry Pi with the pre-installed OS and project files.
   - Secure all wiring using zip ties and ensure no loose connections.
   - Power on the system and verify all components are functional (motors spin, audio works, sensors respond).

> Tip: Before final deployment, test each module (motors, IMU, ultrasonic, encoder) individually using provided test scripts to ensure proper wiring and functionality.

## 🗣️ Resemblyzer Speaker Embedding Setup

To ensure that only authorized users can control the vehicle, this project uses **Resemblyzer**, an open-source speaker embedding library. Each group member is registered by computing an average embedding from multiple audio samples.

### 🧭 Steps to Create Speaker Embeddings

1. **Install Resemblyzer**:
```bash
pip install resemblyzer
 ```
2. **Prepare your dataset**:
   Create a folder structure like below:
  ```
kayitli_sesler_mono/
    ├── eda/
    │   ├── eda1.wav
    │   ├── eda2.wav
    ├── emre/
    │   ├── emre1.wav
    │   ├── emre2.wav
    ...

  ``` 
3. **Run the following script to compute average embeddings per speaker**:

```pythonfrom resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import pickle

# Load the encoder model
encoder = VoiceEncoder()

# Directory containing subfolders for each speaker
DATA_DIR = Path("kayitli_sesler_mono")
speaker_embeddings = {}

# Calculate average embedding per speaker
for speaker_dir in DATA_DIR.iterdir():
    if speaker_dir.is_dir():
        embeddings = []
        for wav_file in speaker_dir.glob("*.wav"):
            wav = preprocess_wav(wav_file)
            emb = encoder.embed_utterance(wav)
            embeddings.append(emb)
        if embeddings:
            speaker_embeddings[speaker_dir.name] = np.mean(embeddings, axis=0)

# Save embeddings
with open("saved_embeddings.pkl", "wb") as f:
    pickle.dump(speaker_embeddings, f)

print("✅ Average embeddings saved for each speaker.")

 ```


Describe the steps required to install and set up the project. Include any prerequisites, dependencies, and commands needed to get the project running.

```bash
# Example commands
git clone https://github.com/username/project-name.git
cd project-name
```

## Usage
Provide instructions and examples on how to use the project. Include code snippets or screenshots where applicable.

## Screenshots
Include screenshots of the project in action to give a visual representation of its functionality. You can also add videos of running project to YouTube and give a reference to it here. 

## Acknowledgements
Give credit to those who have contributed to the project or provided inspiration. Include links to any resources or tools used in the project.

[Contributor 1](https://github.com/user1)
[Resource or Tool](https://www.nvidia.com)
