import bme280
import smbus2
import sds011  # ikalchev
import time
import datetime
import RPi.GPIO as GPIO
import serial
import traceback


from working_mode import get_working_mode
from local_measures import *
from sds011_reset_counter import *


# Configuration

BASE_SERVER_URL= 'http://127.0.0.1:8080'
#BASE_SERVER_URL= 'https://weather-serverapplication.herokuapp.com'
SERVER_URL = BASE_SERVER_URL + '/api/measure/new-measure'
SERVER_URL_PCKG = BASE_SERVER_URL + '/api/measure/new-measure-package'

MEASURE_TIME = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

def read_stationId():
    os.system("cat /proc/cpuinfo | grep 'Serial' | cut -d ':' -d ' '  -f2 > station_id.txt") #example 00000000e34ec9d1
    station_id=""

    with open('station_id.txt') as stationIdFile:
        station_id = str(stationIdFile.read()).strip("\n")
        print(station_id)
        return station_id


STATION_ID = read_stationId()

MODE = "enabled", 180 #default



# bme280 - init
port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)


def send_measure(bme_data, sds_data, pm2_5_corr):


    currentTime = datetime.datetime.utcnow().isoformat()
    data = {'stationId': STATION_ID,
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
    global MODE, MEASURE_INTERVAL, sensor
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
                sensor.sleep(sleep=False)
                time.sleep(MEASURE_TIME)

                # read data bme280
                bme_data = bme280.sample(bus, address, calibration_params)
                print(bme_data)

                sds011_data = sensor.query()
                sensor.sleep()

                #fix when sds011 sensor stop working
                try:
                    pm2_5, pm10 = sds011_data
                    write_sds011_reset_count(0)
                except (TypeError, serial.SerialException) as e:  # when sds011_data = None
                    if not check_sds011_reset_count():
                        print("\nStop - too many failed attempts to read sds011 sensor data.\n"
                              "SDS011 sensor reset count exceeds 3 times.\n"
                              "Check if sensor is connected properly.\n\n"
                              "When problem is fixed, remove reset-sds011.count file to reset counter.")
                        with open("error.log", "a") as errorlog:
                            errorlog.write(datetime.datetime.utcnow().isoformat()+" "+"SDS011 reset count exceeds 3 times.\n")
                        raise Exception
                    with open("error.log", "a") as errorlog:
                        errorlog.write(datetime.datetime.utcnow().isoformat()+" Failed to read sds011 data\n")
                    print("Power cycling sensor due to read error\n")
                    sensor.close_serial()
                    GPIO.output(23, GPIO.HIGH) #poweroff sds011 using irf9540 mosfet connected to gpio
                    time.sleep(2)
                    GPIO.output(23, GPIO.LOW) #poweron sds011
                    time.sleep(1)
                    write_sds011_reset_count(+1)
                    sensor.open_serial()
                    #sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)
                    continue

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
            else:
                print("Waiting for updating configuration...")
                time.sleep(180) #wait 3min and check for new configuration

    except KeyboardInterrupt:
        sensor.sleep()


if __name__ == "__main__":
    global sensor
    try:
        GPIO.output(23, GPIO.HIGH) #powercycle sds011 serial reader in case it disappear from /dev/tty0
        time.sleep(2)
        GPIO.output(23, GPIO.LOW)
        time.sleep(1)
        # sds011 - init
        sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)
        do_measure()

    except Exception as ex:
        sensor.sleep()
        print("Exception: "+type(ex).__name__)
        traceback.print_exc()

    except InterruptedError as ie:
        sensor.sleep()
        print("Interrupted error: "+type(ie).__name__)
        traceback.print_exc()

