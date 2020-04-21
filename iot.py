import configparser
import json
import time

from datetime import datetime
from aws.aws_iot import DeviceShadowHandler

conf = configparser.ConfigParser()
conf.read('config.cfg')

# Setup global state
debug = True
last_data_sent = 0
readings = []
state = {
    'taps': {
        'duration': 0,
        'hot': False,
        'cold': False,
    },
    'interrupted': False,
}


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


def shadow_delete_callback(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


def stop_callback(client, userdata, message):
    response = {"state": {"interrupted": True}}
    global state
    state['interrupted'] = True
    bath_shadow.update_shadow_data(json.dumps(response), shadow_update_callback)


def tap_state_callback(client, userdata, message):
    # TODO: Look in the message to get how the state needs to be changed
    global state
    state['taps']['duration'] = 10
    data_reader.hot_tap_on()


def send_metrics(data):
    print('Sending data to aws: {}'.format(data))
    payload = {"state": data}

    bath_shadow.update_shadow_data(json.dumps(payload), shadow_update_callback)


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
    bath_shadow.add_mqtt_subscription('BathMsg/stop', stop_callback)
    bath_shadow.add_mqtt_subscription('BathMsg/tap-state', tap_state_callback)

    if debug:
        from data_readers.fake_reader import FakeDataReader
        data_reader = FakeDataReader()
    else:
        from data_readers.pi_reader import PiDataReader
        data_reader = PiDataReader()

    # TODO: Remove later, was set to check that the LED's work correctly
    data_reader.cold_tap_on()

    try:
        delay = 1
        
        while not state['interrupted']:
            readings = []
            
            for i in range(0, 4):
                dist = data_reader.read_water_height()
                readings.append(dist)
                print("Measured water distance = %.1f cm" % dist)
                time.sleep(delay / 5)

            last_data_sent = check_readings(readings, last_data_sent)
            
            state['taps']['duration'] -= 1
            if state['taps']['duration'] <= 0:
                # TODO: Maybe the data reader should access the state object itself?
                state['taps']['hot'] = False
                state['taps']['cold'] = False
                data_reader.cold_tap_off()
                data_reader.hot_tap_off()
                bath_shadow.send_mqtt_msg('BathMsg/request-tap-state', json.dumps({'shadow': 'SmartBath'}))
                # TODO: It looks like its possible to get shadow data of the current thing that triggered the rule
                #       https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-functions.html#iot-sql-function-get-thing-shadow
                #       If during the setup the users pref temp is set in the device shadow, it can be accessed
                #       It is also possible to invoke a lambda, so really anything is possible
                #       Maybe make this call blocking, and wait to read the response?

    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Manual interrupt")
    finally:
        print("Readings stopped")
        data_reader.reset()
