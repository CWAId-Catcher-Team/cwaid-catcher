#!/bin/bash

echo "Getting id of latest day" 

days=$(curl https://svc90.main.px.t-online.de/version/v1/diagnosis-keys/country/DE/date 2>/dev/null)

latest_day=$(echo $days| tr -d '"[]' | sed 'y_,_\n_' | tail -n 1)

echo "Getting zip file of encoded temporary exposure keys data"

wget https://svc90.main.px.t-online.de/version/v1/diagnosis-keys/country/DE/date/$latest_day 2>/dev/null

mv $latest_day "$latest_day"_tmp

echo "Unzipping and moving into right directory"

unzip -d ./exports/$latest_day "$latest_day"_tmp > /dev/null

rm "$latest_day"_tmp

echo "Decoding encoded temporary exposure keys data"

tail +17c < ./exports/$latest_day/export.bin | ./protoc/bin/protoc --decode SAP.external.exposurenotification.TemporaryExposureKeyExport --proto_path=./proto/ ./proto/temporary_exposure_key_export.proto > ./exports/$latest_day/tek

echo "Done"
