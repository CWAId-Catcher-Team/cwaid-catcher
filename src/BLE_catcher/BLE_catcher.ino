/*
   Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleScan.cpp
   Ported to Arduino ESP32 by Evandro Copercini
*/

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <SPIFFS.h>

#include <sstream>
#include <iostream>
#include <iomanip>

using namespace std;

int scanTime = 5; //In seconds
BLEScan* pBLEScan;

void writeBeaconToFile(String beacon);

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().toString() == "0000fd6f-0000-1000-8000-00805f9b34fb"){
        Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());

        uint8_t* payload = advertisedDevice.getPayload();
        size_t len = advertisedDevice.getPayloadLength();
        
        std::stringstream stream;
        stream << std::hex << std::setfill('0');
        
        // only last 20 bytes of interest; for 31 bytes frame, skip leading 11 bytes; for 28 bytes frame, skip leading 8 bytes
        for (size_t i = len - 20; i < len; i++) {
          stream << std::hex << std::setw(2) << (unsigned int) payload[i];
        }

        // TODO: implement duplicate detection
        String beacon = stream.str().c_str();
        //Serial.print("Relevant payload: ");
        Serial.println(beacon);
        //writeBeaconToFile(beacon);

        // for testing purposes, can be deleted
        /*std::stringstream stream2;
        stream2 << std::hex << std::setfill('0');
        for (size_t i = 0; i < advertisedDevice.getPayloadLength(); i++) {
          stream2 << std::hex << std::setw(2) << (unsigned int) payload[i];
        }
        String s2 = stream2.str().c_str();
        Serial.printf("Full payload: ");
        Serial.println(s2);*/
      }
      
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Scanning...");

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);  // less or equal setInterval value

  // setup flash memory and a file to store collected beacons
  if (!SPIFFS.begin(false)) {
    Serial.println("Error while initializing SPIFFS!");
    while (true){}
  }

  if (!SPIFFS.exists("/beacons.txt")) {
    File file = SPIFFS.open("/beacons.txt", "w");
    file.close();
    Serial.println("File for beacons has been generated.");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
  Serial.print("Devices found: ");
  Serial.println(foundDevices.getCount());
  Serial.println("Scan done!");
  pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory
  delay(20000);
}

void writeBeaconToFile(String beacon) {
  File file = SPIFFS.open("/beacons.txt", "a");
  if (file) {
    Serial.println("Writing to file: ");
    Serial.println(beacon);
    file.println(beacon);
  }
  file.close();
}
