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
bool scan = true;
const char * beaconFile = "/beacons.txt";

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
        std::string beacon = stream.str();
        cout << "Beacon: " << beacon.c_str() << endl;

        if (scan){
          if (true/*change to: queue does not contain beacon already*/) {
            // if you want to test writing to file, remove comment in front of writeBeaconToFile
            writeBeaconToFile(beacon.c_str());
          }
        }

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
  Serial.println("---------------Commands:---------------");
  Serial.println("read - reading the catched frames log file.");
  Serial.println("clean - remove and recreate catched frames log file.");
  Serial.println("log - stop/start logging of catched frames. Started on default.");
  Serial.println("---------------------------------------");
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

  if (!SPIFFS.exists(beaconFile)) {
     createFile(SPIFFS, beaconFile);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
  pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if(input.equals("read")) {
        readFile(SPIFFS, beaconFile);
        Serial.println("All frames displayed.");
    }
    else if (input.equals("clean")){
      deleteFile(SPIFFS, beaconFile);
      createFile(SPIFFS, beaconFile);
    }
    else if (input.equals("log")){
      if (scan){
        Serial.println("No longer logging!");
        scan = false;
      }
      else {
        Serial.println("Loggin now.");
        scan = true;
      }
    }
  }
  delay(20000);
}

void writeBeaconToFile(String beacon) {
  // seems to write in pages of 251 bytes length
  if (SPIFFS.totalBytes() - SPIFFS.usedBytes() > 256) {
    Serial.printf("Used Bytes: %d\n", SPIFFS.usedBytes());
    File file = SPIFFS.open(beaconFile, FILE_APPEND);
    if (file) {
      Serial.print("Writing to file: ");
      Serial.println(beacon);
      file.println(beacon);
    }
    file.close();
  }
  // else: maybe stop scanning / send sensor to sleep mode?
}

void deleteFile(fs::FS &fs, const char * path){
    scan = false;
    if(fs.remove(path)){
        Serial.println("- file deleted");
    } else {
        Serial.println("- delete failed");
    }
    scan = true;
}

void createFile(fs::FS &fs, const char * path){
  File file = SPIFFS.open(path, FILE_WRITE);
  file.close();
  Serial.println("BLE frames log file has been re-generated.");
}

void readFile(fs::FS &fs, const char * path){
  Serial.println("Reading logged frames:");
      File file = SPIFFS.open(path, FILE_READ);
        while(file.available()){
          Serial.write(file.read());
        }
        file.close();}
