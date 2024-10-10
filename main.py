import bme280
import smbus2
import sds011  # ikalchev
import time
import datetime
import traceback

import py_AHTx0


from working_mode import get_working_mode
from local_measures import *


# Configuration

BASE_SERVER_URL = 'http://127.0.0.1:8080'

SERVER_URL = BASE_SERVER_URL + '/api/measure/new-measure'
SERVER_URL_PCKG = BASE_SERVER_URL + '/api/measure/new-measure-package'

MEASURE_TIME = 60


def read_stationId():
    os.system("cat /proc/cpuinfo | grep 'Serial' | cut -d ':' -d ' '  -f2 > station_id.txt") #example 00000000e34ec9d1
    station_id = ""

    with open('station_id.txt') as stationIdFile:
        station_id = str(stationIdFile.read()).strip("\n")
        print(station_id)
        return station_id


STATION_ID = read_stationId()

MODE = "enabled", 180 #default

#smbus i2c port
port = 1

# bme280 - init
bme280_address = 0x77
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, bme280_address)

# aht10 - init
aht10_address = 0x38
aht10_sensor = py_AHTx0.AHTx0(port, aht10_address)


def send_measure(bme_data, aht10_humidity, sds_data, pm2_5_corr):


    currentTime = datetime.datetime.utcnow().isoformat()
    data = {'stationId': STATION_ID,
            'date': str(currentTime)+'Z',
            'temp': round(bme_data.temperature, 2),
            'humidity': round(aht10_humidity, 2),
            'pressure': round(bme_data.pressure, 2),
            'pm25': (sds_data[0]),
            'pm10': (sds_data[1]),
            'pm25Corr': round(pm2_5_corr, 3)}

    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data)


    try:
        newRequest = requests.post(SERVER_URL, data=body, headers=headers)
        print(newRequest)
        if newRequest.status_code == 200:
            print("Server response: ok")
        elif newRequest.status_code == 400:
            print("Bad request")
            raise requests.exceptions.RequestException
        else:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print('Error sending measure, check internet connection')
        save_measure_to_csv(data)
    except Exception as e:
        print(e)



def do_measure():
    global MODE, MEASURE_INTERVAL, sds011_sensor
    try:
        while True:
            MODE, MEASURE_INTERVAL = get_working_mode(STATION_ID) #before each measure get configuration from remote
            print("Measure interval: " + str(MEASURE_INTERVAL))
            print("Mode: " + MODE)

            try:
                send_local_saved_measures(SERVER_URL_PCKG)
            except FileNotFoundError as e:
                pass

            if MODE == "enabled":
                sds011_sensor.sleep(sleep=False)
                time.sleep(MEASURE_TIME)

                # read data bme280
                bme_data = bme280.sample(bus, bme280_address, calibration_params)
                print(bme_data)

                sds011_data = sds011_sensor.query()
                sds011_sensor.sleep()
                #sds011_data = None #test exception

                #fix when sds011 sensor stop working
                try:
                    pm2_5, pm10 = sds011_data
                except TypeError:
                    with open("error.log", "a") as errorlog:
                        errorlog.write(datetime.datetime.utcnow().isoformat()+" Failed to read sds011 data\n")
                        print(datetime.datetime.utcnow().isoformat()+" Failed to read sds011 data\n")
                    raise Exception

                print("pm2.5: " + str(pm2_5))

                print("sds011 pm2.5 corrected")

                aht10_humidity = aht10_sensor.relative_humidity

                print("aht10 humidity: "+str(aht10_humidity))

                humidity_for_pm2_5 = aht10_humidity

                if aht10_humidity > 95.00:
                    humidity_for_pm2_5 = 95.00

                pm2_5_corrected = pm2_5 * 2.8 * pow((100 - humidity_for_pm2_5), -0.3745)
                print("pm2.5 corrected :" + str(pm2_5_corrected))
                print("pm10: " + str(pm10))

                # send measure to remote server
                send_measure(bme_data, aht10_humidity, sds011_data, pm2_5_corrected)

                print("Waiting for next measure...")
                time.sleep(MEASURE_INTERVAL)
            else:
                print("Waiting for updating configuration...")
                time.sleep(180) #wait 3min and check for new configuration

    except KeyboardInterrupt:
        sds011_sensor.sleep()


if __name__ == "__main__":
    try:
        # sds011 - init
        sds011_sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)
        do_measure()

    except Exception as ex:
        sds011_sensor.sleep()
        print("Exception: "+type(ex).__name__)
        traceback.print_exc()

    except InterruptedError as ie:
        sds011_sensor.sleep()
        print("Interrupted error: "+type(ie).__name__)
        traceback.print_exc()

