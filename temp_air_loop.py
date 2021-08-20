import bme280
import smbus2
import sds011 #ikalchev
import time

#bme280 - init
port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

#sds011 - init
sensor = sds011.SDS011("/dev/ttyUSB0", use_query_mode=True)


###
#TODO
#-add humidity correction //
#-add work mode check to library //always in sleep so no need
#-convert data to JSON
#-send to remote
#-catch exception //
###
#server side - verify user with api key

try:

 while True:

  sensor.sleep(sleep=False)
  time.sleep(30)
 
  #read data bme280
  bme_data = bme280.sample(bus, address, calibration_params)
  print(bme_data)
  
  sds011_data=sensor.query()
  sensor.sleep()
  
  pm2_5,pm10=sds011_data
  print("pm2.5: "+str(pm2_5))
  print("pm10: "+str(pm10))
  print("sds011 pm2.5 corrected")
  pm2_5_corrected=pm2_5 * 2.8 * pow((100 - bme_data.humidity), -0.3745)
  print("pm2.5 corrected :"+str(pm2_5_corrected))
  print("Waiting 1 hour for next measure...")
  time.sleep(60)

except KeyboardInterrupt:
	sensor.sleep()