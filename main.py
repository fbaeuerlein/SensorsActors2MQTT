import schedule
import time
import logging
import sys
import json
import argparse
import log
import MQTT
import DeviceManager

logger = log.get_logger("main")

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Configuration file to use (JSON)")
args = parser.parse_args()
print(args.config)

config = {}
with open(args.config) as f:
    config = json.load(f)

try: 
    device_id = config["general"]["device_id"]
    mqtt_host = config["mqtt"]["host"]
    mqtt_port = int(config["mqtt"]["port"])
    mqtt_user = config["mqtt"]["user"]
    mqtt_pass = config["mqtt"]["password"]
except Exception as e:
    logger.error("Configuration error! ({})".format(e))
    sys.exit(-1)

logger.info("Setting up ...")
logger.info("  Device ID: {}".format(device_id))
logger.info("  MQTT host: {}:{}".format(mqtt_host, mqtt_port))
logger.info("  MQTT user: {}".format(mqtt_user))

ads_ntc = I2CDevices.ADS1115_NTC()
ads_ntc.run()

dht11 = DHT11(17) # dht11 on gpio 17
dht11.run()

dht11_temperature = PublisherAdapter("/sensors/dht11/01/temperature", dht11.get_temperature)
dht11_humidity = PublisherAdapter("/sensors/dht11/01/humidity", dht11.get_humidity)
rpi_cpu_temp = RPiSensors.CPUTemperature("/sensors/temperature/cpu")
rpi_gpio_pump1 = RPiSensors.GPIO("/devices/pump/air", 27, True, GPIO.OUT, False)
rpi_gpio_pump2 = RPiSensors.GPIO("/devices/pump/circulation", 22, False, GPIO.OUT, True)
temp_tank = I2CDevices.ADS1115_NTC_ChannelAdapter("/sensors/temperature/tank", ads_ntc, 1)
temp_ext = I2CDevices.ADS1115_NTC_ChannelAdapter("/sensors/temperature/ext", ads_ntc, 2)


mqtt_client = MQTT.Client(device_id)
mqtt_client.username_pw_set(mqtt_user, mqtt_pass)

device_manager = DeviceManager.DeviceManager(mqtt_client)
device_manager.add(dht11_temperature, 60)
device_manager.add(dht11_humidity, 60)
device_manager.add(rpi_cpu_temp, 60)
device_manager.add(rpi_gpio_pump1, 60)
device_manager.add(rpi_gpio_pump2, 60)
device_manager.add(temp_tank, 60)
device_manager.add(temp_ext, 60)

# finally connect
connected = False
while not connected:
    try:
        mqtt_client.connect("localhost")
    except: 
        logger.warn("Failed to connect. Retrying in 10 seconds.")
        time.sleep(10)
        continue
    connected = True

# runs forever
device_manager.run()
