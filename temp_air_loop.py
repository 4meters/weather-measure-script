import bme280
import smbus2
import sds011  # ikalchev
import time
import datetime

import requests
import json
import csv

import os

# Configuration
#apikey moved to file
#SERVER_URL = 'https://example-server321.herokuapp.com/api/new-measure'
SERVER_URL = 'http://127.0.0.1:8080/api/measure/new-measure'
SERVER_URL_PCKG = 'http://127.0.0.1:8080/api/measure/new-measure-package'
MEASURE_TIME = 60
MEASURE_INTERVAL = 180

def read_stationId():
    os.system("cat /proc/cpuinfo | grep 'Serial' | cut -d ':' -d ' '  -f2 > station_id.txt") #example 00000000e34ec9d1
    station_id=""

    with open('station_id.txt') as stationIdFile:
        station_id = str(stationIdFile.read()).strip("\n")
        print(station_id)
        return station_id

def read_apiKey():
    try:
        api_key = open('apikey.conf', 'r').read()#'DH1_D3JJ9WCWBLIFYBSWN5T68GSM7W_C'
        if len(api_key) != 32:
            raise Exception
        else:
            return api_key

    except Exception as e:
        print(e)
        print('Error reading apiKey file!')
        return False


STATION_ID = read_stationId()
API_KEY = read_apiKey()




# bme280 - init
port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# sds011 - init
sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)




def send_measure(bme_data, sds_data, pm2_5_corr):


    currentTime = datetime.datetime.utcnow().isoformat()
    data = {'apiKey': API_KEY,
            'stationId': STATION_ID,
            'date': str(currentTime)+'Z',
            'temp': round(bme_data.temperature, 2),
            'humidity': round(bme_data.humidity, 2),
            'pressure': round(bme_data.pressure, 2),
            'pm25': (sds_data[0]),
            'pm10': (sds_data[1]),
            'pm25Corr': round(pm2_5_corr, 3)}

    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data)

    try:
        send_local_saved_measures()

    except FileNotFoundError as e:
        pass

    try:
        newRequest = requests.post(SERVER_URL, data=body, headers=headers)
        print(newRequest)
        if newRequest.status_code == 200:
            print("Server response: ok")
        elif newRequest.status_code == 401:
            print("Bad apikey")
            raise requests.exceptions.RequestException
        else:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print('Error sending measure, check internet connection')
        save_measure_to_csv(data)
    except Exception as e:
        print(e)


def save_measure_to_csv(data):

    measure_file = open("measures.csv", "a", newline='')
    csv_writer = csv.writer(measure_file)
    csv_writer.writerow(data.values())
    measure_file.close()


def send_local_saved_measures():
    jsondict = {}
    with open('measures.csv') as measure_file:
        csv_data = csv.DictReader(measure_file, fieldnames=['apiKey','stationId','date','temp',
                                                            'humidity','pressure','pm25','pm25Corr','pm10'])
        jsondict['measureList']=[]
        for rows in csv_data:
            print(rows)#Just for reference
            jsondict['measureList'].append(rows)  #Appending all the csv rows
        try:
            headers = {'Content-Type': 'application/json'}
            body = json.dumps(jsondict)
            newRequest = requests.post(SERVER_URL_PCKG, data=body, headers=headers)
            print("Sending local saved measures result: " + str(newRequest))
            if newRequest.status_code==200:
                measure_file.close()
                os.remove('measures.csv')
            return True
        except requests.exceptions.RequestException as e:
            print("Error when trying to send local saved measures")
            return False


def do_measure():
    try:

        while True:
            sensor.sleep(sleep=False)
            time.sleep(MEASURE_TIME)

            # read data bme280
            bme_data = bme280.sample(bus, address, calibration_params)
            print(bme_data)

            sds011_data = sensor.query()
            sensor.sleep()

            pm2_5, pm10 = sds011_data
            print("pm2.5: " + str(pm2_5))

            print("sds011 pm2.5 corrected")
            if bme_data.humidity > 95.00:
                humidity = 95.00
            else:
                humidity = bme_data.humidity
            pm2_5_corrected = pm2_5 * 2.8 * pow((100 - humidity), -0.3745)
            print("pm2.5 corrected :" + str(pm2_5_corrected))
            print("pm10: " + str(pm10))

            # send measure to remote server
            send_measure(bme_data, sds011_data, pm2_5_corrected)

            print("Waiting for next measure...")
            time.sleep(MEASURE_INTERVAL)

    except KeyboardInterrupt:
        sensor.sleep()


if __name__ == "__main__":
    try:
        do_measure()
    except Exception as ex:
        sensor.sleep()

    except InterruptedError as ie:
        sensor.sleep()


###
# TODO
# -add humidity correction // done
# -add work mode check to library //always in sleep so no need
# -convert data to JSON //done
# -send to remote //done easy way - do refactor
# -catch exception //done - test
###
# server side - verify user with api key //done
# add global variable for api key //done - from file now
# round bme measure //done
# add checking if system time is correct on startup of script
# add logging errors to file
# TODO add error logging to file with time for all exceptions
# TODO split reading configuration to another file also saving local

