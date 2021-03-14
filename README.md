# cwaid-catcher

## System Requirements
- Linux based system (or terminal). Only needed for getting TEKs. Rest works with Python.
- Python 
- Arduino IDE

## TO EXTEND: Usage of sensors
- To avoid accidental deletion of collected beacons, the deletion/clearing of the beacons file stored in the sensors' flash memory can only be done using the FileIO programm.
- Changing the sensor's program code does not seem to affect the file in flash memory that stores the beacons.
- The sensors' reset button do not format the flash memory, i.e. the beacons in storage are persistent until deletion using FileIO
- FileIO and BLE_catcher both allow to print all stored beacons by typing `read` as SerialMonitor input. Note: BLE_catcher only reads that input every 20 seconds at the moment, so be patient :)
- File management is handled in code, the only thing you have to do is reading and clearing it (see below).
- FileIO comes with the following input commands to SerialMonitor: 
  - `read` (prints all beacons stored in flash mem)
  - `delete` (deletes beacon file)
  - `clear` (flushes all stored beacons from file)
  - `usedBytes` (displays #bytes that are currently used to store beacons)
  - `totalBytes` (displays #bytes that can potentially be used to store beacons)

## Storing IDs
Put your catched ids into the src/analyzer/ids directory and name it location_counter_date_time, where date and time correspond to the time where you started your sensor and counter is counter plus one of the location id file that already exists (if it exists of course). Look into this directory and you see example files.

## Evaluating your collected data
### Getting TEKs
First of all you need TEKs downloaded from the CWA server. You can download these with the puller script (src/puller/puller.sh) each day to get the TEKs of the preceding day. The TEKs are uploaded at 1 am (MET). If you want to download the TEKs for a specific date, you can pass the date as an argument to the puller script in the format YYYY-MM-DD. Note, if you pass a specific date, you should first check which dates are available under https://svc90.main.px.t-online.de/version/v1/diagnosis-keys/country/DE/date. The puller script will then store the TEKs and you have to do nothing else.



## Further Information

### Infos
 Software & Hardware  | Details
------------ | -------------
Sensor | Standard ESP32
Board | Adafruit HUZZAH32
BLE Library | Espressif<br>https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE<br>https://docs.espressif.com/projects/esp-idf/en/release-v4.1/api-reference/index.html
IDE | Arduino IDE
Exposure Notification API Bluetooth Specification | https://www.blog.google/documents/70/Exposure_Notification_-_Bluetooth_Specification_v1.2.2.pdf
Exposure Notification API Cryptography Specification | https://blog.google/documents/69/Exposure_Notification_-_Cryptography_Specification_v1.2.1.pdf
Corona Warn App GitHub | https://github.com/corona-warn-app
Android Exposure Notification API | https://github.com/google/exposure-notifications-android
TEK Backend Server & Access API | https://blog.to.com/corona-warn-app-daten/
Goolge Exposure Notification API Key Scheduling Implementation | https://github.com/google/exposure-notifications-internals/blob/main/exposurenotification/src/main/cpp/matching_helper.cc


### Tutorials
 - Install Arduino from website not from package-manager!!
 - Follow the tutorials. Use this json link for the esp json: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
 - Select ESP Feather from the boards list
 - Use USB cable which is not for charging only if port is greyed out
 - https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-mac-and-linux-instructions/
 - https://randomnerdtutorials.com/getting-started-with-esp32/
