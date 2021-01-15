# If you want to avoid copy pasting from the COM Output Window you must flash the simple.http onto the esp32 then call 
# esp32fs.local/beacons.txt and store it in the DOWNLOAD_FOLDER
# call id_parser.py 'MyName' 'Record_Date as YYYYMMDD' 'Record_Time as HHMMSS' 'DOWNLOAD_FOLDER'
# If DOWNLOAD_FOLDER is unspecified the current working directory is used to find beacons.txt file

import os
import sys

# Length in bytes
RPI_LENGTH = 20
SEP_LENGTH = 0
TIME_LENGTH = 3

# COMMAND LINE ARGS
NAME = sys.argv[1] if sys.argv[1] is not None else 'unknown'
Date = sys.argv[2] if sys.argv[2] is not None else '20201201'
Time = sys.argv[3] if sys.argv[3] is not None else '133000'
DOWNLOAD_FOLDER = sys.argv[4] if sys.argv[4] is not None else os.getcwd()

counter = 1

while os.path.isfile(os.path.join(DOWNLOAD_FOLDER,'{}_ids{}_{}_{}'.format(NAME,counter,Date,Time))):
    counter = counter + 1
  
outfilename = os.path.join(DOWNLOAD_FOLDER,'{}_ids{}_{}_{}'.format(NAME,counter,Date,Time))

with open(os.path.join(DOWNLOAD_FOLDER,'beacons.txt'),'rb') as f, open(outfilename,'x') as o:
    while data := f.read(RPI_LENGTH + SEP_LENGTH + TIME_LENGTH):
        o.write('{};{}\n'.format(data[:RPI_LENGTH].hex(),int.from_bytes(data[RPI_LENGTH+SEP_LENGTH:RPI_LENGTH+SEP_LENGTH+TIME_LENGTH],'big')))