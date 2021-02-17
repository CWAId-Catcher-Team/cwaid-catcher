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

const int scanTime = 60; // scan for 'scanTime' seconds
const uint64_t sleepTime = 0; // pausing scan for 'sleepTime'+1 seconds
BLEScan* pBLEScan;
bool scan = true;
const char * beaconFile = "/beacons.txt";
vector<uint8_t> beaconBuf;
const int bufSize = 920; // 920 bytes of space for 40 beacons (+3 bytes of metadata each) within one scan interval


void appendBeaconToBuffer(uint8_t* beacon, size_t beaconLen, uint8_t* metadata, size_t metadataLen);


class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().equals(BLEUUID((uint16_t) 0xfd6f))) {

      // payload of BLE frame
      uint8_t* payload = advertisedDevice.getPayload();
      size_t len = advertisedDevice.getPayloadLength();       

      // metadata
      uint64_t currentTime = esp_timer_get_time() / 1000000;

      // encoding: 01(64) = Android, 10(128) = iOS, 11(192) = header as expected, but payload length differs, 00(0) = unexpected format
      uint8_t formatInfo = 0;
      if ((unsigned int) payload[0] == 3) { // Android (lacks flag section)
        formatInfo = (len == 28) ? 64 : 192;
      } else if ((unsigned int) payload[0] == 2) { // iOS
        formatInfo = (len == 31) ? 128 : 192;
      }

      // 22 bits can represent 48 days as seconds, use 2 most significant bits of 3-byte metadata to encode information about BLE frame format
      uint8_t metadata[] = {(currentTime >> 16) + formatInfo, (currentTime >> 8), currentTime};

      appendBeaconToBuffer(payload + (len - 20), 20, metadata, sizeof(metadata));
      
      /**********
      // enable to print information on the recorded beacon to serial monitor
      std::stringstream stream;
      stream << std::hex << std::setfill('0');
      for (size_t i = len - 20; i < len; i++) {
        stream << std::hex << std::setw(2) << (unsigned int) payload[i];
      }
      std::string beacon = stream.str();
      cout << "Logged beacon: " << beacon.c_str() << ";" << currentTime << ";" << +os << endl;
      **********/
    }
  }
};

void setup() {
  Serial.begin(115200);
  Serial.println("---------------Commands:---------------");
  Serial.println("read - reading the catched frames log file.");
  Serial.println("log - stop/start logging of catched frames. Started on default.");
  Serial.println("---------------------------------------");

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(false);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);  // less or equal setInterval value

  // setup flash memory and a file to store collected beacons
  // needs to be set to true when first running this code on the sensor
  if (!SPIFFS.begin(false)) {
    Serial.println("Error while initializing SPIFFS!");
    while (true) {}
  }

  if (!SPIFFS.exists(beaconFile)) {
     createFile(SPIFFS, beaconFile);
  }

  beaconBuf.reserve(bufSize);
}

void loop() {
  if (scan) {
    // sleep before scanning, to avoid potential faults while storing, press reset button before disconnecting from USB
    esp_sleep_enable_timer_wakeup(sleepTime * 1000000ULL);
    esp_light_sleep_start();
    
    cout << "Scan start. One may issue commands to sensor via serial monitor now until scan complete." << endl;
    BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
    pBLEScan->clearResults();
    
    cout << "Scan done. Found " << beaconBuf.size() / 23 << " beacons."<< endl;
    writeBeaconsToFile();
  }
 
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if (input.equals("read")) {
        Serial.println("Output format: beacon;timestamp;OS/frame format");
        readFile(SPIFFS, beaconFile);
        Serial.println("All frames displayed.");
    }    
    else if (input.equals("log")){
      if (scan) {
        Serial.println("No longer logging!");
        scan = false;
      }
      else {
        Serial.println("Logging now.");
        scan = true;
      }
    }
  }
  delay(1000);
}

void appendBeaconToBuffer(uint8_t* beacon, size_t beaconLen, uint8_t* metadata, size_t metadataLen) {
  for (size_t i = 0; i < beaconLen; i++) {
    beaconBuf.push_back(beacon[i]);
  }
  for (size_t j = 0; j < metadataLen; j++) {
    beaconBuf.push_back(metadata[j]);
  }
}

void writeBeaconsToFile() {
  // SPIFFS seems to write in pages of 251 bytes length
  if (SPIFFS.totalBytes() - SPIFFS.usedBytes() > beaconBuf.size()) {
    File file = SPIFFS.open(beaconFile, FILE_APPEND);
    if (file) {
      for (vector<uint8_t>::iterator it = beaconBuf.begin(); it != beaconBuf.end(); it++) {
        file.write(*it);
      }
    }
    file.close();
    beaconBuf.clear();
    cout << "Flash memory populated with data: " << SPIFFS.usedBytes() << " bytes" << endl;
  } else {
    scan = false;
  }
}

void createFile(fs::FS &fs, const char * path) {
  File file = SPIFFS.open(path, FILE_WRITE);
  file.close();
  Serial.println("BLE frames log file has been generated.");
}

void readFile(fs::FS &fs, const char * path) {
  File file = SPIFFS.open(path, FILE_READ);
  while (file.available()) {
    uint8_t beacon[20];
    uint8_t metadata[3];
    file.read(beacon, sizeof(beacon));
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
    cout << stream.str() << ";" << currentTime << ";" << formatInfo << endl;
  }
  file.close();
}
