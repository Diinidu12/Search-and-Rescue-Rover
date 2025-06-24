#include <SPI.h>
#include <LoRa.h>
#include <DHT.h>
#include <ESP32Servo.h>
#include <TinyGPSPlus.h>

// LoRa module pins
#define ss 5
#define rst 14
#define dio0 2

Servo servo1;
Servo servo2;

// Motor control pins
int a = 27, b = 32, c = 4, d = 0;
int v = 3, h = 1;
bool AUTO = false;

int t, cm, R, L, x;

// Ultrasonic Sensor Pins
int Ltr = 25, Lec = 22;
int Rtr = 26, Rec = 15;
int Ftr = 33, Fec = 21;

// Gas and DHT
#define MQ2_AOUT_PIN 34
#define MQ2_DOUT_PIN 35
#define DHT_PIN 13
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// GPS Module on Serial2 (RX=16, TX=17)
HardwareSerial GPS_Serial(2);
TinyGPSPlus gps;

// Status LED
int y = 12;

unsigned long lastSensorSend = 0;
const unsigned long sensorInterval = 5000;

void setup() {
  Serial.begin(115200);
  Serial.println("Starting System...");

  // LoRa setup
  LoRa.setPins(ss, rst, dio0);
  while (!LoRa.begin(433E6)) {
    Serial.println("LoRa init failed. Retrying...");
    delay(500);
  }
  LoRa.setSyncWord(0xF1);
  Serial.println("LoRa Initialized!");

  // Motor & sensor pins
  pinMode(a, OUTPUT); pinMode(b, OUTPUT);
  pinMode(c, OUTPUT); pinMode(d, OUTPUT);
  pinMode(y, OUTPUT);

  pinMode(Ltr, OUTPUT); pinMode(Lec, INPUT);
  pinMode(Rtr, OUTPUT); pinMode(Rec, INPUT);
  pinMode(Ftr, OUTPUT); pinMode(Fec, INPUT);
  pinMode(MQ2_DOUT_PIN, INPUT);

  dht.begin();
  GPS_Serial.begin(9600, SERIAL_8N1, 16, 17); // GPS RX2
}

void loop() {
  // Non-blocking GPS read
  if (GPS_Serial.available()) {
    gps.encode(GPS_Serial.read());
  }

  unsigned long currentMillis = millis();

  // --- Send sensor+GPS data every 5s ---
  if (currentMillis - lastSensorSend >= sensorInterval) {
    lastSensorSend = currentMillis;

    // Read gas
    int analogValue = analogRead(MQ2_AOUT_PIN);
    float gasPercentage = (analogValue / 1023.0) * 100.0;

    // Read temp & humidity
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    if (isnan(humidity)) humidity = 0.0;
    if (isnan(temperature)) temperature = 0.0;

    // GPS
    float lat = gps.location.isValid() ? gps.location.lat() : 0.0;
    float lng = gps.location.isValid() ? gps.location.lng() : 0.0;

    // Format and send
    String gasData = String(gasPercentage, 2);
    String humidityData = String(humidity, 2);
    String temperatureData = String(temperature, 2);
    String latitudeData = String(lat, 6);
    String longitudeData = String(lng, 6);

    String packet = gasData + " " + humidityData + " " + temperatureData + " " + latitudeData + " " + longitudeData;


    LoRa.beginPacket();
    LoRa.print(packet);
    LoRa.endPacket();
  }

  // --- Receive LoRa commands ---
  if (LoRa.parsePacket()) {
    String LoRaData = "";
    while (LoRa.available()) {
      LoRaData += (char)LoRa.read();
    }

    Serial.println("Received: " + LoRaData);

    if (LoRaData == "Mode") {
      AUTO = !AUTO;
    }

    if (!AUTO) {
      digitalWrite(y, LOW);
      if (LoRaData == "Forward") {
        digitalWrite(a, LOW); digitalWrite(b, HIGH);
        digitalWrite(c, LOW); digitalWrite(d, HIGH);
      } else if (LoRaData == "Backward") {
        digitalWrite(a, HIGH); digitalWrite(b, LOW);
        digitalWrite(c, HIGH); digitalWrite(d, LOW);
      } else if (LoRaData == "Stop") {
        digitalWrite(a, LOW); digitalWrite(b, LOW);
        digitalWrite(c, LOW); digitalWrite(d, LOW);
      } else if (LoRaData == "Right") {
        digitalWrite(a, HIGH); digitalWrite(b, LOW);
        digitalWrite(c, LOW); digitalWrite(d, HIGH);
      } else if (LoRaData == "Left") {
        digitalWrite(a, LOW); digitalWrite(b, HIGH);
        digitalWrite(c, HIGH); digitalWrite(d, LOW);
      }
    }
  }

  // --- Auto mode obstacle avoidance ---
  if (AUTO) {
    digitalWrite(y, HIGH);

    x = distance(Ftr, Fec);
    L = distance(Ltr, Lec);
    R = distance(Rtr, Rec);

    Serial.print("Front: "); Serial.print(x);
    Serial.print(" Left: "); Serial.print(L);
    Serial.print(" Right: "); Serial.println(R);

    delay(200);

    if (x < 50) {
      if (L > R) {
        digitalWrite(a, LOW); digitalWrite(b, HIGH);
        digitalWrite(c, HIGH); digitalWrite(d, LOW);
      } else {
        digitalWrite(a, HIGH); digitalWrite(b, LOW);
        digitalWrite(c, LOW); digitalWrite(d, HIGH);
      }
    } else {
      digitalWrite(a, LOW); digitalWrite(b, HIGH);
      digitalWrite(c, LOW); digitalWrite(d, HIGH);
    }
  }
}

int distance(int tr, int ec) {
  digitalWrite(tr, LOW); delayMicroseconds(2);
  digitalWrite(tr, HIGH); delayMicroseconds(10);
  digitalWrite(tr, LOW);
  t = pulseIn(ec, HIGH, 30000);
  if (t == 0) return 999;
  cm = t * 0.034 / 2;
  return (cm > 400) ? 999 : cm;
}
