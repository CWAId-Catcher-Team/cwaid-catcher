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
#include <deque>

using namespace std;

int scanTime = 5; //In seconds
BLEScan* pBLEScan;
bool scan = true;
const char * beaconFile = "/beacons.txt";
deque<String> seenBeacons;
int maxBeacons = 250;

void writeBeaconToFile(String beacon);

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().equals(BLEUUID((uint16_t) 0xfd6f))){
        //Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());

        uint8_t* payload = advertisedDevice.getPayload();
        size_t len = advertisedDevice.getPayloadLength();
        
        std::stringstream stream;
        stream << std::hex << std::setfill('0');
        
        // only last 20 bytes of interest; for 31 bytes frame, skip leading 11 bytes; for 28 bytes frame, skip leading 8 bytes
        for (size_t i = len - 20; i < len; i++) {
          stream << std::hex << std::setw(2) << (unsigned int) payload[i];
        }

        std::string beacon = stream.str();
        cout << "Beacon: " << beacon.c_str() << endl;

        if (std::find(seenBeacons.begin(), seenBeacons.end(), beacon.c_str()) == seenBeacons.end()) {
          writeBeaconToFile(beacon.c_str());
          seenBeacons.push_front(beacon.c_str());
          if(seenBeacons.size() >= maxBeacons) {
            seenBeacons.pop_back();
          }
        }
      }
      
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("---------------Commands:---------------");
  Serial.println("read - reading the catched frames log file.");
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
  // needs to be set to true at the first start
  if (!SPIFFS.begin(false)) {
    Serial.println("Error while initializing SPIFFS!");
    while (true){}
  }

  if (!SPIFFS.exists(beaconFile)) {
     createFile(SPIFFS, beaconFile);
  }
}

void loop() {
  if (scan) {
    BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
    pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory
  }
 
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if(input.equals("read")) {
        readFile(SPIFFS, beaconFile);
        Serial.println("All frames displayed.");
    }    
    else if (input.equals("log")){
      if (scan){
        Serial.println("No longer logging!");
        scan = false;
      }
      else {
        Serial.println("Logging now.");
        scan = true;
      }
    }
  }
  delay(25000);
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
  } else {
    scan = false;
  }
}

void createFile(fs::FS &fs, const char * path){
  File file = SPIFFS.open(path, FILE_WRITE);
  file.close();
  Serial.println("BLE frames log file has been generated.");
}

void readFile(fs::FS &fs, const char * path){
  Serial.println("Reading logged frames:");
      File file = SPIFFS.open(path, FILE_READ);
        while(file.available()){
          Serial.write(file.read());
        }
        file.close();
 }
