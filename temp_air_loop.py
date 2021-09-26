import bme280
import smbus2
import sds011  # ikalchev
import time
import datetime

import requests
import json

# Configuration
API_KEY = 'DH1_D3JJ9WCWBLIFYBSWN5T68GSM7W_C'
#SERVER_URL = 'https://example-server321.herokuapp.com/api/new-measure'
SERVER_URL = 'http://127.0.0.1:8080/api/new-measure'


# bme280 - init
port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# sds011 - init
sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)


###
# TODO
# -add humidity correction // done
# -add work mode check to library //always in sleep so no need
# -convert data to JSON //done
# -send to remote //done easy way - do refactor
# -catch exception //
###
# server side - verify user with api key
# add global variable for api key
# round bme measure
# add checking if system time is correct

def save_locally(data):
    file = open("local_measure.db", "a")
    file.write(data+";")
    file.close()
    return True


def send_local_saved_measure():
    file = open("local_measure.db")
    file_data = file.read()
    measures = file_data.split(";")

    headers = {'Content-Type': 'application/json'}

    for measure in measures:
        newRequest = requests.post(SERVER_URL, data=measure, headers=headers)
    return True


def send_measure(bme_data, sds_data, pm2_5_corr):
    currentTime = datetime.datetime.utcnow().isoformat()
    data = {'apiKey': API_KEY,
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
        #send_local_saved_measure()
        newRequest = requests.post(SERVER_URL, data=body, headers=headers)
        print(newRequest)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print('Error sending measure, check internet connection')
        #save_locally(data)
    # add exception if error
    # save data locally if no internet


def do_measure():
    try:

        while True:
            sensor.sleep(sleep=False)
            time.sleep(3)  # 30

            # read data bme280
            bme_data = bme280.sample(bus, address, calibration_params)
            print(bme_data)

            sds011_data = sensor.query()
            sensor.sleep()

            pm2_5, pm10 = sds011_data
            print("pm2.5: " + str(pm2_5))
            print("pm10: " + str(pm10))
            print("sds011 pm2.5 corrected")
            pm2_5_corrected = pm2_5 * 2.8 * pow((100 - bme_data.humidity), -0.3745)
            print("pm2.5 corrected :" + str(pm2_5_corrected))

            # send measure to remote server
            send_measure(bme_data, sds011_data, pm2_5_corrected)

            print("Waiting 1 hour for next measure...")
            time.sleep(60)  # 3600

    except KeyboardInterrupt:
        sensor.sleep()


#def printDebug():
#    print(bme_data)
#    print("pm2.5: " + str(pm2_5))
#    print("pm10: " + str(pm10))
#    print("sds011 pm2.5 corrected")
#    print("pm2.5 corrected :" + str(pm2_5_corrected))
#    print("Waiting 1 hour for next measure...")


if __name__ == "__main__":
    do_measure()
