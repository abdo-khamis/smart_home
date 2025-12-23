#include <Arduino.h>
#include <WiFi.h>
#include <DHT.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <MFRC522v2.h>
#include <MFRC522DriverSPI.h>
//#include <MFRC522DriverI2C.h>
#include <MFRC522DriverPinSimple.h>
#include <MFRC522Debug.h>
#include <ESP32Servo.h>
#include <iostream>
#include <sstream>
#include <Preferences.h>
#include <ArduinoJson.h>
#include <map>
static std::map<int, bool> lightStates;
Preferences preferences;



MFRC522DriverPinSimple ss_pin(5);

MFRC522DriverSPI driver{ss_pin}; // Create SPI driver
//MFRC522DriverI2C driver{};     // Create I2C driver
MFRC522 mfrc522{driver};         // Create MFRC522 instance

unsigned long lastDashboardTime = 0;
unsigned long lastTempTime = 0;
const unsigned long dashboardInterval = 5000; // كل 5 ثواني يبعث dashboard
const unsigned long tempInterval = 60000;     // كل 60 ثانية يبعث temp فقط

int number_of_lights = 0;

unsigned long lastCardTime = 0;
const unsigned long cardInterval = 2000;

bool emergencyManual = false;
bool emergencyAuto = false;

bool waitingForNewCard = false;
bool waitingForAccess = false;

const char *ssid = "SmartHome-Wifi";
const char *password = "12345678";

AsyncWebServer server(80);
AsyncWebSocket wsSmartHome("/SmartHomeServer");

#define dht_pin 21
#define servo_pin 14
#define buzzer_pin 25

DHT dht11(dht_pin, DHT11);

Servo doorServo;

bool doorOpen = false;
unsigned long doorTime = 0;

void handleRoot(AsyncWebServerRequest *request) {
  request->send_P(200, "text/html", "<h1></h1>");
}

void handleNotFound(AsyncWebServerRequest *request) {
  request->send(404, "text/plain", "File Not Found");
}




void sendDashboardData() {
  float temp = dht11.readTemperature();
  float hum = dht11.readHumidity();

  DynamicJsonDocument doc(256);
  doc["type"] = "dashboard";
  JsonObject data = doc.createNestedObject("data");
  data["temp"] = temp;
  data["hum"] = hum;
  data["lights"] = number_of_lights;
  data["security"] = 1;

  String output;
  serializeJson(doc, output);
  wsSmartHome.textAll(output);

  Serial.println(" Sent Dashboard JSON: " + output);
}

void sendTempData() {
  float temp = dht11.readTemperature();

  DynamicJsonDocument doc(128);
  doc["type"] = "temp";
  JsonObject data = doc.createNestedObject("data");
  data["temp"] = temp;

  String output;
  serializeJson(doc, output);
  wsSmartHome.textAll(output);

  Serial.println(" Sent Temp JSON: " + output);
}



void onSmartHomeWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
                               AwsEventType type, void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n",
                    client->id(), client->remoteIP().toString().c_str());
      break;

    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;

    case WS_EVT_DATA: {
      AwsFrameInfo *info = (AwsFrameInfo *)arg;
      if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
        String json = String((char *)data).substring(0, len);
        Serial.println(" Received: " + json);

        DynamicJsonDocument doc(256);
        DeserializationError error = deserializeJson(doc, json);
        if (error) {
          Serial.println(" JSON parse error");
          return;
        }

        String type = doc["type"];
        if (type == "security_control") {
          String dataType = doc["data"]["data_type"];

          if (dataType == "add_request") {
            Serial.println(" Add request received, waiting for new card...");
              waitingForNewCard = true;
          }

          else if (dataType == "access_request") {
            int response = doc["data"]["response"];
            if (response == 200) {
              Serial.println(" Access Granted — open relay");
              doorServo.write(0);
              // digitalWrite(14, HIGH);
              doorOpen = true;
              doorTime = millis();
            } else if (response == 400) {
              Serial.println(" Access Denied");
            }
          }
        }else if (type == "light_control") {

            JsonObject lights = doc["data"];

            for (JsonPair kv : lights) {

                int pin = String(kv.key().c_str()).toInt();
                bool state = kv.value().as<int>();

                bool prev = lightStates[pin];     
                lightStates[pin] = state;         

                digitalWrite(pin, state ? HIGH : LOW);

                if (!prev && state) number_of_lights++;   
                if (prev && !state) number_of_lights--;   

                Serial.printf(" Light %d -> %s | Total: %d\n",
                              pin, state ? "ON" : "OFF", number_of_lights);
            }
        } else if (type== "emergency"){
          int option = doc["data"]["operation"];

          if(option == 1){
            emergencyManual = true;
            EmergencyOn();
          }else{
            emergencyManual = false;
            if(!emergencyAuto){
              EmergencyOff();
            }
          }
        }
      }
    } break;

    default:
      break;
  }
}




void EmergencyOn(){
  doorServo.write(0);
  digitalWrite(25, HIGH);

  digitalWrite(4, HIGH);
  digitalWrite(22, HIGH);
  digitalWrite(13, HIGH);
  digitalWrite(12, HIGH);
}
void EmergencyOff(){
  doorServo.write(80);
  digitalWrite(25, LOW);

  digitalWrite(4, LOW);
  digitalWrite(22, LOW);
  digitalWrite(13, LOW);
  digitalWrite(12, LOW);
}





void setup(void) {

  Serial.begin(115200);
  dht11.begin();

  mfrc522.PCD_Init();    // Init MFRC522 board.
  MFRC522Debug::PCD_DumpVersionToSerial(mfrc522, Serial);	
	Serial.println(F("Scan PICC to see UID"));


  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.on("/", HTTP_GET, handleRoot);
  server.onNotFound(handleNotFound);

  wsSmartHome.onEvent(onSmartHomeWebSocketEvent);
  server.addHandler(&wsSmartHome);

  server.begin();
  Serial.println("HTTP server started");

  doorServo.attach(servo_pin);
  doorServo.write(80);
  pinMode(4, OUTPUT);
  pinMode(22, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(25, OUTPUT);

}


void loop() {


  wsSmartHome.cleanupClients();


  unsigned long currentMillis = millis();


   float temp = dht11.readTemperature();

if (temp > 60 && !emergencyAuto) {
  emergencyAuto = true;
  EmergencyOn();
}

if (temp <= 40 && emergencyAuto) {
  emergencyAuto = false;
  if(!emergencyManual){
    EmergencyOff();
  }
}




  if (currentMillis - lastDashboardTime >= dashboardInterval) {
    lastDashboardTime = currentMillis;
    sendDashboardData();
  }


  if (currentMillis - lastTempTime >= tempInterval) {
    lastTempTime = currentMillis;
    sendTempData();
  }

if (currentMillis - lastCardTime >= cardInterval) {

  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {

  String cardID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    cardID += String(mfrc522.uid.uidByte[i], HEX);
  }
  cardID.toUpperCase();

  DynamicJsonDocument doc(256);
  doc["type"] = "security";
  JsonObject data = doc.createNestedObject("data");

  if (waitingForNewCard) {
    data["data_type"] = "new_nfc";
  } else {
    data["data_type"] = "access";
  }

  data["nfc_number"] = cardID;

  String output;
  serializeJson(doc, output);
  wsSmartHome.textAll(output);

  waitingForNewCard = false;


  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  lastCardTime = millis();
}
}

if (doorOpen && millis() - doorTime >= 5000) {
  doorServo.write(80);
  doorOpen = false;
}



}



