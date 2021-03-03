#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <SPIFFS.h>

#include <sstream>
#include <iostream>
#include <iomanip>
#include <vector>

using namespace std;

const int scanTime = 5; // scan for 'scanTime' seconds 
const uint64_t sleepTime = 0; // pausing scan for 'sleepTime' seconds
BLEScan* pBLEScan;
bool scan = true;
const char * beaconFile = "/beacons.txt";
vector<uint8_t> beaconBuf;
const int bufSize = 500;


void appendBeaconToBuffer(uint8_t* beacon, size_t beaconLen, uint8_t* metadata, size_t metadataLen);


class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().equals(BLEUUID((uint16_t) 0xfd6f))){

      // payload of BLE frame
      uint8_t* payload = advertisedDevice.getPayload();
      size_t len = advertisedDevice.getPayloadLength();
      
      // metadata
      int rssi = advertisedDevice.getRSSI();
      uint64_t currentTime = esp_timer_get_time() / 1000000;

      // encoding: 01(64) = Android, 10(128) = iOS, 11(192) = header as expected, but payload length differs, 00(0) = unexpected format
      uint8_t formatInfo = 0;
      if ((unsigned int) payload[0] == 3) { // Android (lacks flag section)
        formatInfo = (len == 28) ? 64 : 192;
      } else if ((unsigned int) payload[0] == 2) { // iOS
        formatInfo = (len == 31) ? 128 : 192;
      }
    
      // 22 bits can represent 48 days as seconds, use 2 most significant bits of 3-byte metadata to encode information about BLE frame format
      // least significant byte of rssi can represent [-128,127], transform to (unsigned) byte to store
      uint8_t metadata[] = {(currentTime >> 16) + formatInfo, (currentTime >> 8), currentTime, (uint8_t) rssi};

      /**********
      // print beacon and metadata to serial monitor
      std::stringstream stream;
      stream << std::hex << std::setfill('0');
      for (size_t i = len - 20; i < len; i++) {
        stream << std::hex << std::setw(2) << (unsigned int) payload[i];
      }
      std::string beacon = stream.str();
      cout << "Logged beacon: " << beacon.c_str() << ";" << currentTime << ";" << rssi << endl;
      ***********/

      if (len >= 20) {
        appendBeaconToBuffer(payload + (len - 20), 20, metadata, sizeof(metadata));
      } else {
        uint8_t defaultBeacon[20] = { 0 };
        defaultBeacon[0] = (uint8_t) len;
        appendBeaconToBuffer(defaultBeacon, 20, metadata, sizeof(metadata));
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
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(false);
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

  beaconBuf.reserve(bufSize);
}

void loop() {
  if (scan) {
    BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
    pBLEScan->clearResults();
    cout << "Scan done. Found " << beaconBuf.size() / 24 << " beacons."<< endl; 
    writeBeaconsToFile();
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
  
  delay(sleepTime * 1000);
}

void appendBeaconToBuffer(uint8_t* beacon, size_t beaconLen, uint8_t* metadata, size_t metadataLen) {
  for(size_t i = 0; i < beaconLen; i++) {
    beaconBuf.push_back(beacon[i]);
  }
  for(size_t j = 0; j < metadataLen; j++) {
    beaconBuf.push_back(metadata[j]);
  }
}

void writeBeaconsToFile() {
  // seems to write in pages of 251 bytes length
  if (SPIFFS.totalBytes() - SPIFFS.usedBytes() > 256) {
    File file = SPIFFS.open(beaconFile, FILE_APPEND);
    if (file) {
      for(vector<uint8_t>::iterator it = beaconBuf.begin(); it != beaconBuf.end(); it++) {
        file.write(*it);
      }
    }
    file.close();
    cout << "New beacons written to file." << endl;
    beaconBuf.clear();
    Serial.printf("Used Bytes: %d\n", SPIFFS.usedBytes());
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
          uint8_t beacon[20];
          uint8_t metadata[4];
          file.read(beacon, sizeof(beacon));
          // first 3 bytes correspond to timestamp, 4th byte represents rssi
          file.read(metadata, sizeof(metadata));

          std::stringstream stream;
          stream << std::hex << std::setfill('0');
          for (size_t i = 0; i < sizeof(beacon); i++) {
            stream << std::hex << std::setw(2) << (unsigned int) beacon[i];
          }

          std::string formatInfo = "unexpected";
          if (metadata[0] >= 192) {
            metadata[0] -= 192;
            formatInfo = "length mismatch";
          } else if (metadata[0] >= 128) {
            metadata[0] -= 128;
            formatInfo = "iOS";
          } else if (metadata[0] >= 64) {
            metadata[0] -= 64;
            formatInfo = "Android";
          }
    
          uint32_t currentTime = (uint32_t) metadata[0] << 16 | (uint16_t) metadata[1] << 8 | metadata[2];
          // use + to promote int8_t to a type printable as a number, transform rssi byte back to signed 8-bit integer
          cout << stream.str() << ";" << currentTime << ";" << +int8_t(metadata[3]) << ";" << formatInfo << endl;
        }
        file.close();
 }
