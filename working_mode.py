import json
import requests
from configparser import ConfigParser

AVAILABLE_MEASURE_INTERVALS = {"3min": 180, "5min": 300, "10min": 600, "15min": 900}


def read_last_working_mode():
    try:
        config_object = ConfigParser()
        config_object.read("last_mode.conf")

        if config_object.has_section("config"):
            pass
        else:
            raise IOError

        mode = config_object["config"]["mode"]
        measureInterval = config_object["config"]["measureInterval"]

        if mode == "enabled" or mode == "disabled":

            if config_object["config"]["measureInterval"] in AVAILABLE_MEASURE_INTERVALS:
                return mode, AVAILABLE_MEASURE_INTERVALS[measureInterval]
            else:
                return mode, 180

        else:

            if config_object["config"]["measureInterval"] in AVAILABLE_MEASURE_INTERVALS:
                return "disabled", AVAILABLE_MEASURE_INTERVALS[measureInterval]
            else:
                return "disabled", 180

    except IOError:
        return "disabled", 180


def save_last_working_mode(data):
    config_object = ConfigParser()
    config_object["config"] = {
        "mode": data.get('mode'),
        "measureInterval": data.get('measureInterval')
    }

    with open('last_mode.conf', 'w') as lastModeFile:
        config_object.write(lastModeFile)


def get_working_mode(station_id):
    # exception for no internet, use last mode saved to file
    try:
        new_request = requests.get('http://127.0.0.1:8080/api/station/get-working-mode/'+station_id)
        print(new_request.status_code)

        response_data = json.loads(new_request.text)
        if new_request.status_code == 200:
            save_last_working_mode(response_data)
            return read_last_working_mode()
        else:
            return read_last_working_mode()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print('Error getting configuration from remote')
        return read_last_working_mode()
