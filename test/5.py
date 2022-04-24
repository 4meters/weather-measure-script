import json
import os
import requests
import configparser

def read_last_working_mode():
    try:
        with open('example_last_mode.conf') as lastModeFile:
            last_mode = str(lastModeFile.read()).strip("\n")
            if last_mode != "enabled" or last_mode == "disabled":
                print(last_mode)
                return last_mode
            else:
                return "disabled"
    except IOError:
        return "disabled"


def save_last_working_mode(data):
    with open('example_last_mode.conf', 'w') as lastModeFile:
        lastModeFile.write("mode = "+data.get('mode'))
        lastModeFile.write("\n")
        lastModeFile.write("measureInterval = "+data.get('measureInterval'))
        pass


def get_working_mode():
    # exception for no internet, use last mode saved to file
    newRequest = requests.get('http://127.0.0.1:8080/api/station/get-working-mode/00000000e34ec9d1')
    print(newRequest.status_code)

    response_data = json.loads(newRequest.text)
    if newRequest.status_code == 200:
        save_last_working_mode(response_data)
        return response_data.get('measureInterval'), response_data.get('mode')
    else:
        return read_last_working_mode()


MEASURE_INTERVAL, MODE = get_working_mode()
print(MEASURE_INTERVAL)
print(MODE)
