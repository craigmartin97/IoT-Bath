import configparser
import json
import logging

#import RPi.GPIO as GPIO
import time

from datetime import datetime

#GPIO Mode (BOARD / BCM)
from aws.aws_iot import DeviceShadowHandler

#GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 22
GPIO_ECHO = 27

#set GPIO direction (IN / OUT)
#GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
#GPIO.setup(GPIO_ECHO, GPIO.IN)

#Testing
last_data_sent = 0
readings = []

conf = configparser.ConfigParser()
conf.read('config.cfg')


def shadow_update_callback(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("payload: " + str(payloadDict["state"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")


# Function called when a shadow is deleted
def shadow_delete_callback(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


def test_receive_callback(client, userdata, message):
    response = {"state": {"reported": {"interrupted": True}}}
    global interrupted
    interrupted = True
    bath_shadow.update_shadow_data(json.dumps(response), shadow_update_callback)


def setup_logging():
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


def distance():
    # set Trigger to HIGH
    #GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    #GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    #while GPIO.input(GPIO_ECHO) == 0:
    #    StartTime = time.time()

    # save time of arrival
    #while GPIO.input(GPIO_ECHO) == 1:
    #    StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance


def send_metrics(data):
    
    print('sending data to api: {}'.format(data))
    bath_shadow.update_shadow_data(json.dumps(data), shadow_update_callback)
    pass 


def check_readings(readings, last):
    
    avg_reading = sum(readings) / len(readings) 
    
    if abs(avg_reading - last) > 30:
        send_metrics({'distance': dist, 'timestamp': str(datetime.utcnow())})
        return avg_reading
            
    return last


if __name__ == '__main__':
    # Setup
    bath_shadow = DeviceShadowHandler(name='SmartBath',
                                      root_ca_path=conf['bath-certs']['root-ca-path'],
                                      private_key_path=conf['bath-certs']['private-key-path'],
                                      cert_path=conf['bath-certs']['cert-path'])
    bath_shadow.connect()
    bath_shadow.delete_shadow_data(shadow_delete_callback)
    bath_shadow.add_mqtt_subscription('my/test/receive', test_receive_callback)
    interrupted = False

    try:
        while True:
            readings = []
            
            for i in range(0, 4):
                dist = distance()
                readings.append(dist)
                print("Measured Distance = %.1f cm" % dist)
                time.sleep(0.1)

            last_data_sent = check_readings(readings, last_data_sent)

    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        #GPIO.cleanup()
