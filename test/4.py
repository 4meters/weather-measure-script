import json
import os

os.system("cat /proc/cpuinfo | grep 'Serial' | cut -d ':' -d ' '  -f2 > station_id.txt") #example 00000000e34ec9d1
STATION_ID=""

with open('station_id.txt') as stationIdFile:
    STATION_ID = str(stationIdFile.read()).strip("\n")
    print(STATION_ID)



data = {'apiKey': "abcd",
        'stationId': STATION_ID}

headers = {'Content-Type': 'application/json'}
body = json.dumps(data)
print(body)
