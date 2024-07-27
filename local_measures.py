import requests
import csv
import json
import os

def save_measure_to_csv(data):

    measure_file = open("measures.csv", "a", newline='')
    csv_writer = csv.writer(measure_file)
    csv_writer.writerow(data.values())
    measure_file.close()


def send_local_saved_measures(SERVER_URL_PCKG):
    jsondict = {}
    with open('measures.csv', "r") as measure_file:
        csv_data = csv.DictReader(measure_file, fieldnames=['stationId', 'date', 'temp',
                                                            'humidity', 'pressure', 'pm25', 'pm25Corr', 'pm10'])
        jsondict['measureList'] = []
        try:
            for rows in csv_data:
                print(rows)#Just for reference
                jsondict['measureList'].append(rows)  #Appending all the csv rows
        except csv.Error: #fix for null line at end of file
            pass
        try:
            headers = {'Content-Type': 'application/json'}
            body = json.dumps(jsondict)
            new_request = requests.post(SERVER_URL_PCKG, data=body, headers=headers)
            print("Sending local saved measures result: " + str(new_request))
            if new_request.status_code==200:
                measure_file.close()
                os.remove('measures.csv')
            return True
        except requests.exceptions.RequestException as e:
            print("Error when trying to send local saved measures")
            return False