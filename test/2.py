import datetime
import json
import csv

def save_locally():
    #example data
    currentTime = datetime.datetime.utcnow().isoformat()
    data = {'apiKey': "exampleKEY",
            'stationId': "abcdef123",
            'date': str(currentTime)+'Z',
            'temp': 20.5,
            'humidity': 60.4,
            'pressure': 1020.5,
            'pm25': 100.0,
            'pm25Corr': 90.0,
            'pm10': 150.0,
            }

    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data)


    #
    csv_file = open('example-measures.csv','a',newline='')
    #csv_file.write(str(data.values())+'\n')
    write = csv.writer(csv_file)
    write.writerow(data.values())
    csv_file.close()


def load_local_data(jsonFile):
    jsondict={}
    with open('example-measures.csv', 'rw', newline='') as csv_file:
        csv_data = csv.DictReader(csv_file)
        jsondict["data"]=[]

        for rows in csv_data:
            print(rows)
            jsondict["data"].append(rows)
        print(jsondict)


def test_converter():
    def csv_to_json(csvFile, jsonFile):
        jsondict = {}
        with open(csvFile) as csvfile:
            csv_data = csv.DictReader(csvfile, fieldnames=['apiKey','stationId','date','temp',
                                                           'humidity','pressure','pm25','pm25Corr','pm10'])
            jsondict['measureList']=[]
            for rows in csv_data:
                print(rows)#Just for reference
                jsondict['measureList'].append(rows)  #Appending all the csv rows

        with open(jsonFile, 'w') as jsonfile:
            #Dumping the data into jsonfile.json
            jsonfile.write(json.dumps(jsondict, indent = 4))  #indent is used for pretty printing

    csvfile = 'example-measures.csv'
    jsonfile = 'example-jsonfile.json'
    csv_to_json(csvfile, jsonfile)#Calling the function

if __name__ == "__main__":
    #save_locally()
    #load_local_data()
    test_converter()