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
    while (true) {}
  }
  
  beaconFileExists = SPIFFS.exists(beaconFile);
  if (beaconFileExists) {
    Serial.println("Beacons file exists in flash memory.");
  } else {
    Serial.println("No file with beacons found.");
  }
  Serial.println("Waiting for input...");
  listCommands();
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if (input.equals("readv1")) {
      if (beaconFileExists) {
        Serial.println("Output format: beacon;timestamp");
        File file = SPIFFS.open(beaconFile, FILE_READ);
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
          uint32_t currentTime = (uint32_t) metadata[0] << 16 | (uint16_t) metadata[1] << 8 | metadata[2];
          std::cout << stream.str() << ";" << currentTime << std::endl;
        }
        file.close();
        Serial.println("All beacons displayed using format (beacon;timestamp).");
      } else {
        Serial.println("Beacon file does not exist.");
      }

    } else if (input.equals("readv2")) {
      if (beaconFileExists) {
        Serial.println("Output format: beacon;timestamp;OS/frameFormat");
        File file = SPIFFS.open(beaconFile, FILE_READ);
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
          std::cout << stream.str() << ";" << currentTime << ";" << formatInfo << std::endl;
        }
        file.close();
        Serial.println("All beacons displayed using format (beacon;timestamp;OS/frameFormat).");
      }

    } else if (input.equals("readv3")) {
      if (beaconFileExists) {
        Serial.println("Output format: beacon;timestamp;rssi");
        File file = SPIFFS.open(beaconFile, FILE_READ);
        while (file.available()) {
          uint8_t beacon[20];
          uint8_t metadata[4];
          file.read(beacon, sizeof(beacon));
          file.read(metadata, sizeof(metadata));

          std::stringstream stream;
          stream << std::hex << std::setfill('0');
          for (size_t i = 0; i < sizeof(beacon); i++) {
            stream << std::hex << std::setw(2) << (unsigned int) beacon[i];
          }
          uint32_t currentTime = (uint32_t) metadata[0] << 16 | (uint16_t) metadata[1] << 8 | metadata[2];
          std::cout << stream.str() << ";" << currentTime << ";" << +int8_t(metadata[3]) << std::endl;
        }
        file.close();
        Serial.println("All beacons displayed using format (beacon;timestamp;rssi).");
      }

    } else if (input.equals("delete")) {
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
       
    } else if (input.equals("format")) {
      Serial.println("Formatting... This may take a moment, stay calm :)");
      Serial.printf("Formatting successful == %s\n", SPIFFS.format() ? "true" : "false");
    } else if (input.equals("usedMemory") || input.equals("used")) {
      Serial.printf("%d bytes are populated, this is %.1f%% of the sensor's non-volatile memory.\n", SPIFFS.usedBytes(), SPIFFS.usedBytes() * 100.0f / SPIFFS.totalBytes());
    } else if (input.equals("remainingMemory") || input.equals("remaining")) {
      int unused = SPIFFS.totalBytes() - SPIFFS.usedBytes();
      Serial.printf("%d bytes are unused, this is %.1f%% of the sensor's non-volatile memory.\n", unused, unused * 100.0f / SPIFFS.totalBytes());
    } else if (input.equals("memorySize")) {
      Serial.printf("The sensor provides %d bytes of accessible non-volatile memory.\n", SPIFFS.totalBytes());
    } else if (input.equals("commands") || input.equals("man")) {
      listCommands();
    } else {
      Serial.println("Invalid command.");
    }
    beaconFileExists = SPIFFS.exists(beaconFile);
  }
}

void listCommands() {
  Serial.println("--------------------Commands:--------------------");
  Serial.println(" - commands: lists all possible commands that can be input to serial monitor");
  Serial.println(" - memorySize: prints #bytes that are accessible to store data in non-volatile memory");
  Serial.println(" - usedMemory: prints #bytes populated with data");
  Serial.println(" - remainingMemory: prints #bytes that remains to be populated with data\n");

  Serial.println(" - create: creates a file to store recorded beacons, BLE_catcher will do this itself if no file exists yet");
  Serial.println(" - delete: deletes file that is used to store beacons");
  Serial.println(" - format: deletes all files in file system");
  Serial.println(" - clear: removes all recorded beacons stored on the sensor\n");
  
  Serial.println(" - readv1: prints data stored in memory to serial monitor, use if sensor stores (beacon;timestamp)");
  Serial.println(" - readv2: prints data stored in memory to serial monitor, use if sensor stores (beacon;timestamp;OS/frameFormat)");
  Serial.println(" - readv3: prints data stored in memory to serial monitor, use if sensor stores (beacon;timestamp;rssi)");
  Serial.println("-------------------------------------------------");
}
