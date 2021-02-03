#!/bin/bash

# You can pass the day as an argument

if [[ $# -eq 0 ]]; then
	echo "Getting id of latest day" 

	days=$(curl https://svc90.main.px.t-online.de/version/v1/diagnosis-keys/country/DE/date 2>/dev/null)

	latest_day=$(echo $days| tr -d '"[]' | sed 'y_,_\n_' | tail -n 1)
else
	echo "Using $1 as date"

	latest_day="$1"
fi

echo "Getting zip file of encoded temporary exposure keys data"

wget https://svc90.main.px.t-online.de/version/v1/diagnosis-keys/country/DE/date/$latest_day 2>/dev/null

mv $latest_day "$latest_day"_tmp

echo "Unzipping and moving into right directory"

unzip -d ./exports/$latest_day "$latest_day"_tmp > /dev/null

rm "$latest_day"_tmp

echo "Filtering encoded temporary exposure keys data"

tail +17c ./exports/$latest_day/export.bin > ./exports/$latest_day/tek

echo "Done"

echo ""

echo "Downloading stats"

wget https://svc90.main.px.t-online.de/version/v1/stats 2>/dev/null

echo "Unzipping and moving into right directory"

unzip -d ./export_stats/$latest_day stats > /dev/null

rm stats

echo "Done"
