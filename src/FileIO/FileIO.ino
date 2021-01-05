#include <SPIFFS.h>
#include <iostream>
#include <sstream>
#include <iomanip>

bool beaconFileExists;
const char* beaconFile = "/beacons.txt";

void setup() {
  Serial.begin(115200);
  delay(5000);
  if (!SPIFFS.begin(false)) {
    Serial.println("Error while initializing SPIFFS!");
    while (true){}
  }
  
  beaconFileExists = SPIFFS.exists(beaconFile);
  if (beaconFileExists) {
    Serial.println("Beacons file exists in flash memory.");
  } else {
    Serial.println("No file with beacons found.");
  }
  Serial.println("Waiting for input: Possible Commands: read, delete, create, clear, usedBytes, totalBytes.");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if(input.equals("read")) {
      if (beaconFileExists) {
        Serial.println("Reading beacons from file:");
        File file = SPIFFS.open(beaconFile, FILE_READ);
        while(file.available()){
          uint8_t beacon[20];
          uint8_t timeArray[3];
          file.read(beacon, sizeof(beacon));
          file.read(timeArray, sizeof(timeArray));
          
          std::stringstream stream;
          stream << std::hex << std::setfill('0');
          for (size_t i = 0; i < sizeof(beacon); i++) {
            stream << std::hex << std::setw(2) << (unsigned int) beacon[i];
          }
          uint32_t currentTime = (uint32_t) timeArray[0] << 16 | (uint16_t) timeArray[1] << 8 | timeArray[2];
          std::cout << stream.str() << ";" << currentTime << std::endl;
        }
        file.close();
        Serial.println("All beacons displayed.");
      } else {
        Serial.println("Beacon file does not exist.");
      }

    // only use if write function only included beacons, no timestamps
    } else if (input.equals("readv1")) {
      if (beaconFileExists) {
        Serial.println("Reading beacons from file with version 1 (beacons only):");
        File file = SPIFFS.open(beaconFile, FILE_READ);
        while(file.available()){
          Serial.write(file.read());
        }
        file.close();
        Serial.println("All beacons displayed with read v1 (beacons only).");
      }
    } else if (input.equals("delete")) {
      Serial.println("Deleting beacon file:");
      Serial.printf("Deletion of beacons file successful == %s\n", SPIFFS.remove(beaconFile) ? "true" : "false");
      
    } else if (input.equals("create")) {
      if (!beaconFileExists) {
        File file = SPIFFS.open(beaconFile, FILE_WRITE);
        file.close();
        Serial.println("Empty beacon file created.");
      } else {
        Serial.println("Beacon file already exists. Use command \'delete\' to delete file or \'clear\' to clear the file\'s content.");
      }
      
    } else if (input.equals("clear")) {
      if (beaconFileExists) {
        File file = SPIFFS.open(beaconFile, FILE_WRITE);
        file.close();
        Serial.println("Cleared current beacons from file.");
      } else {
        Serial.println("File to clear does not exist.");
      }
      
    } else if (input.equals("deleteAll")) {
      Serial.println("Deleting all files:");
      Serial.printf("Formatting successful == %s\n", SPIFFS.format() ? "true" : "false");
    } else if (input.equals("usedBytes")) {
      Serial.printf("Used SPIFFS bytes: %d\n", SPIFFS.usedBytes());
    } else if (input.equals("totalBytes")) {
      Serial.printf("Total SPIFFS bytes: %d\n", SPIFFS.totalBytes());
    } else {
      Serial.println("Invalid command.");
    }
    beaconFileExists = SPIFFS.exists(beaconFile);
  }
  delay(2000);
}
