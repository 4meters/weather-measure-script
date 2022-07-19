# Weather App - Raspberry Pi measure script
Part of weather monitoring app project.

Client app: https://github.com/4meters/weather-app

Measure script: https://github.com/4meters/weather-measure-script
## Main features
- measuring weather conditions using BME280 and SDS011 sensors
- sending measure result to remote server
- local saving measure results in case of connection failure
- configuration of measure interval and working mode (enabled/disabled) from remote
- correction of PM2.5 measure based on air humidity

## Technologies used for implementing project
### Database:
- MongoDB

### Server:
- Java
- Maven
- Spring Boot
- Spring Boot MongoDB

### Client:
- React
- JS
- HTML

### Weather Station
- Python
- bme280 & sds011 python library

## Additional Python libraries used:
- csv, csvwriter
- configparser
- os
- time, datetime
- smbus2
- requests, json


## How to run:
Run `main.py` on Raspberry Pi with sensors connected