# Search-and-Rescue-Rover

ESP32 Search and Rescue Rover
An all-terrain, semi-autonomous search and rescue rover built using the ESP32 microcontroller. Designed for post-disaster environments, this rover streams live video over Wi-Fi, communicates sensor and control data via LoRa, and supports autonomous navigation and remote operation. Ideal for identifying hazardous conditions and locating survivors without risking human lives.

Features
Remote Control & Autonomous Navigation

Manual control via a custom Python GUI.

Autonomous mode with obstacle avoidance using ultrasonic sensors.

Live Video Streaming

Real-time camera feed over Wi-Fi using the ESP32-CAM module.

Environmental Monitoring

GPS Tracking – Live location sharing via LoRa.

Gas Detection – Identifies potentially hazardous gases in the environment.

Temperature & Humidity – DHT11 module for weather condition assessment.

Terrain Capability

Durable and powered by six lithium-ion batteries.

Supports mobility in rough or unstable terrain using L298N motor drivers.

Communication

Wi-Fi: Live video stream.

LoRa (RA-02): Long-range control commands and telemetry (sensor data, GPS, status).

Hardware Components
ESP32 Dev Board (x2 for main control and camera)

ESP32-CAM Module

LoRa RA-02 Module

3x Ultrasonic Sensors (Obstacle avoidance)

GPS Module (Position tracking)

3x L298N Motor Drivers

Gas Sensor (Flammable/toxic gas detection)

DHT11 (Temperature & humidity)

6x Lithium-ion Batteries (Power supply)
