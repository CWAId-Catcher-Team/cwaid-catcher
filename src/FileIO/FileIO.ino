#include <SPIFFS.h>
#include <iostream>
#include <sstream>

bool beaconFileExists;

void setup() {
  Serial.begin(115200);

  if (!SPIFFS.begin(false)) {
    Serial.println("Error while initializing SPIFFS!");
    while (true){}
  }

  delay(5000);
  beaconFileExists = SPIFFS.exists("/beacons.txt");
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
        File file = SPIFFS.open("/beacons.txt", "r");
        while(file.available()){
          Serial.write(file.read());
        }
        file.close();
        Serial.println("All beacons displayed.");
      } else {
        Serial.println("Beacon file does not exist.");
      }

    } else if (input.equals("delete")) {
      Serial.println("Deleting beacon file:");
      Serial.printf("Deletion of beacons file successful == %s\n", SPIFFS.remove("/beacons.txt") ? "true" : "false");
      
    } else if (input.equals("create")) {
      if (!beaconFileExists) {
        File file = SPIFFS.open("/beacons.txt", "w");
        file.close();
        Serial.println("Empty beacon file created.");
      } else {
        Serial.println("Beacon file already exists. Use command \'delete\' to delete file or \'clear\' to clear the file\'s content.");
      }
      
    } else if (input.equals("clear")) {
      if (beaconFileExists) {
        File file = SPIFFS.open("/beacons.txt", "w");
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
    beaconFileExists = SPIFFS.exists("/beacons.txt");
  }
  delay(2000);
}
