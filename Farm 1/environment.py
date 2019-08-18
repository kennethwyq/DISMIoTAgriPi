import sys
import Adafruit_DHT
from time import sleep
from gpiozero import MCP3008, Buzzer
import RPi.GPIO as GPIO 
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#initializes
bz = Buzzer(21)
pin = 4
update = True
mcp3008 = MCP3008(channel=0)

#host
host = "a3f69y8dukmi8a-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

#mqtt client
my_rpi = AWSIoTMQTTClient("farm1-environment")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec
my_rpi.connect()

def printvalue():
    print('Temp: {:.1f} C'.format(temperature))
    print('Humidity: {:.1f}'.format(humidity))
    print('Light value:', light)

def buzzer():
    if temperature < 20 or humidity > 60:
        #if too cold or too humid
        bz.on()
        sleep(2)
        bz.toggle()
    else:
        bz.off()
        sleep(1)
        
def publisher():
    message = {}
    message["deviceid"] = "farm1"
    import datetime as datetime
    now = datetime.datetime.now()
    message["datetime_value"] = now.strftime("%d/%m/%Y, %H:%M:%S")
    message["temperature_value"] = temperature
    message["humidity_value"] = humidity
    message["light_value"] = light
    import json
    my_rpi.publish("sensors/environment/farm", json.dumps(message), 1)

try:
    while update:
        try:
            humidity, temperature = Adafruit_DHT.read_retry(11, pin)
            light = (1024*(1.0-mcp3008.value))
            light = round(light)
            printvalue()
            buzzer()
            print("Publishing environment values to farm database")
            publisher()
            print("Wait a few seconds before getting next temperature and humidity values..")
            sleep(2)
        except KeyboardInterrupt:
            update=False
        except:
            print("Error while inserting data...")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
except:
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])
