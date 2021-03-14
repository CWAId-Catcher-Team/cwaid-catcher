# CWAid-catcher

## Introduction
CWAid-catcher is a project which tries to analyse the german Corona-Warn-App (CWA) spread and usage among citizens. This project is splitted into two parts. One part is the code for a ESP32 sensor, which catches BLE Beacons from the Exposure Notification Framework that are emitted if a person has an active Corona-Warn-App installed on its smartphone. The other part is the evaluation framework, that matches the collected Beacons (also called IDs in our project) to Temporary Exposure Keys (TEK) uploaded to the CWA server, to determine if one of the collected Beacons corresponds to a TEK, which means that the Beacon belongs to a infected person. Overall, the CWA ecosystem is mimicked with our project, such that you can evaluate the CWA by yourself with ESP32 sensors. Even without access to ESP32 sensors and without collecting Beacons, you can still evaluate some data, like the amount of new warnings uploaded to the CWA server each date.

This project is still under development, but the main functionality is already implemented and works. Mostly setup scripts are missing. If you follow the descriptions in the following, you will be able to exectute everything.

![Evaluation Framwork Logo](/img/ef1.png)

## System Requirements
- Linux based system (or terminal). Only needed for getting TEKs. Rest works with Python3.
- Python3
- Arduino IDE

**Pycryptodome for RPI derivation and AEM decryption**\
`python -m pip install pycryptodome`\
**Protobuf for decoding binary TEK lists downloaded from CWA server**\
`python -m pip install protobuf`\
**Tinydb to store the results of the evaluators**\
`python -m pip install tinydb`\
**Termplotlib to print statistics on the terminal output**<br>
`python -m pip install termplotlib`

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

Using the Arduino IDE, program code can be flashed on the sensor. After connecting an ESP32 sensor via USB and choosing the correct port, the Serial Monitor can be utilized to read the sensor's output and issue commands to the sensor. We utilize several programs that provide different functionalities tailored to particular use cases. To store data in the sensors' non-volatile flash memory, we utilize the SPIFFS library. Flashing new program code to the sensor does not affect the persistent data storage.

### BLE_catcher

### BLE_catcher_observations

### FileIO

## Storing collected IDs
Put your catched ids into the src/analyzer/ids directory and name it location_counter_date_time, where date and time correspond to the time where you started your sensor and counter is counter plus one of the location id file that already exists (if it exists of course). Look into this directory and you see example files.

## Evaluating your collected data
### Getting TEKs
First of all you need TEKs downloaded from the CWA server. You can download these with the puller shell script (src/puller/puller.sh) each day to get the TEKs of the preceding day. The TEKs are uploaded at 1 am (MET). If you want to download the TEKs for a specific date, you can pass the date as an argument to the puller script in the format YYYY-MM-DD. Note, if you pass a specific date, you should first check which dates are available under https://svc90.main.px.t-online.de/version/v1/diagnosis-keys/country/DE/date. The puller script will then store the TEKs and you have to do nothing else.
### Finding collected RPIs that belong to a downloaded TEK
To determine if a collected RPI belongs to a downloaded TEK, which means that a infected person passed by one or more of the sensors, you need to run main.py in src/analyzer/. This script makes use of tek_parser.py to parse the downloaded TEKs, to calculate each RPI that can be derived of the TEK and to store the data in a intermediate format. Since the deriviation of the RPI is time-consuming because of the cryptography operations, we store the TEK data and its RPIs in a intermediate format, such that only one time the RPIs are derived. However, storing the TEKs in a intermediate format takes some space (around 55 MB for TEKs from one date). The main.py script will then load each of the TEKs and its RPIs of the data stored in the intermediate format and tries to match RPIs to RPIs collected with the sensors (stored in src/analyzer/ids/). For each match, the information about the matched RPI like the AEM and and its TEK will be output. Parsing a downloaded TEK file and converting it to the intermediate format takes about 1-2 minutes and is only done one time as described. Analysing the data of the intermediate format and trying to match the RPIs with collected RPIs takes about 10-20 seconds per TEK file stored in intermediate format.
### Evaluating more than matching RPIs
With **evaluator.py** in src/analyzer/, you can evaluate different things like the amount of unique IDs, the distribution of Android/iOS devices in your collected IDs and the amount of new warnings uploaded to the CWA server on a specific date. In src/analyzer/tools are the count_analyzer and group_analyzer, which analyzer IDs if you counted people and want to measure the percentage of CWA users among this people. For this you need to have a sensor, count the people manually, upload the IDs to the src/analyzer/ids folder with the right nameing (see folder for examples) and run the count_analyzer.py. The same can be done for the group_analyzer, but you have to count the groups and store you results in the src/analyzer/groups folder and then run group_analyzer.py. See example group files in the corresponding folder.

The **evaluator_rpi.py** takes the lists of scanned RPIs and returns statistics including:
- Average time CWA users were tracked by the sensor
- Longest and shortest tracked time
- Finding RPIs that exceeded their expected livetime of about 20 minutes
- Distance measurements based on the RSSI 
- Amount of Android and iOS devices (based on our assumption that the BLE Beacon header length indicates the OS)
- Number of RPIs per hour/weekday
- RPI chains: Non-overlapping RPIs that can be used to correlate different RPIs to a TEK 
- above statistics per RPI set or for all sets combined

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
