#  ESP32 Search and Rescue Rover

An all-terrain, semi-autonomous **search and rescue rover** powered by the **ESP32 microcontroller**. Built to assist in post-disaster recovery missions, this rover streams **live video over Wi-Fi**, communicates sensor and control data via **LoRa**, and supports **autonomous navigation** and **remote operation**. It is designed to **identify hazardous areas** and **locate survivors** in dangerous environments without risking human lives.

---

##  Hardware Components

- **ESP32 Dev Board** (for control)
- **ESP32-CAM Module** (live video streaming)
- **LoRa RA-02 Module** (long-range communication)
- **3x Ultrasonic Sensors** (obstacle detection)
- **GPS Module** (real-time tracking)
- **3x L298N Motor Drivers** (movement control)
- **Gas Sensor** (flammable/toxic gas detection)
- **DHT11** (temperature and humidity monitoring)
- **6x Lithium-ion Batteries** (power supply)

---

##  Features

###  Control & Navigation
- **Manual control** using a custom-built **Python GUI**.
- **Autonomous navigation** with obstacle avoidance.

### 📹 Live Streaming
- Real-time video feed over Wi-Fi using **ESP32-CAM**.

### 📡 Communication
- **Wi-Fi**: Live video stream.
- **LoRa (RA-02)**: Sensor data and control commands.

###  Location & Environment Sensing
- **GPS tracking**: Share live rover location.
- **Gas detection**: Identifies potentially hazardous gases.
- **Temperature & humidity**: Helps assess environmental conditions.

---

##  Software & Development

- **Development Platform**: Arduino IDE
- **GUI**: Python desktop application for control and data display
- **Communication Strategy**:
  - Wi-Fi for real-time video
  - LoRa for long-range telemetry and command
- **Technical Challenge**: Managing various modules and handling multiple data streams using the **limited I/O pins of the ESP32** was a major challenge. We implemented efficient pin multiplexing and asynchronous communication techniques to make this possible.

---

## Purpose

This rover was built to:
- Assist **search and rescue teams** in locating individuals in disaster-affected areas.
- Detect **hazardous gases and unsafe conditions** before human entry.
- Share **real-time GPS coordinates** to guide emergency responders.
- Operate in **rough terrain** and high-heat zones.
