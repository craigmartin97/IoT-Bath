import configparser

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

conf = configparser.ConfigParser()
conf.read('config.cfg')

class DeviceShadowHandler(object):
    shadow_handler = None
    mqtt_client = None

    def __init__(self, name, root_ca_path, private_key_path, cert_path):
        self.name = name
        self.cert_paths = {
            'root-ca-path': root_ca_path,
            'private-key-path': private_key_path,
            'cert-path': cert_path
        }

    def connect(self):
        client = AWSIoTMQTTShadowClient(self.name)
        client.configureEndpoint(conf['shadow-endpoint']['endpoint'], int(conf['shadow-endpoint']['port']))
        client.configureCredentials(self.cert_paths['root-ca-path'],
                                    self.cert_paths['private-key-path'],
                                    self.cert_paths['cert-path'])
        client.configureAutoReconnectBackoffTime(1, 32, 20)
        client.configureConnectDisconnectTimeout(10)
        client.configureMQTTOperationTimeout(5)

        client.connect()

        self.shadow_handler = client.createShadowHandlerWithName('SmartBath', True)
        self.mqtt_client = client.getMQTTConnection()

    def delete_shadow_data(self, callback, timeout=5):
        if self.shadow_handler:
            return self.shadow_handler.shadowDelete(callback, timeout)
        else:
            raise Exception('No connection setup to shadow endpoint')

    def update_shadow_data(self, data, callback,timeout=5):
        if self.shadow_handler:
            return self.shadow_handler.shadowUpdate(data, callback, timeout)
        else:
            raise Exception('No connection setup to shadow endpoint')

    def add_mqtt_subscription(self, event, callback, qos=0):
        if self.mqtt_client:
            return self.mqtt_client.subscribe(event, qos, callback)
        else:
            raise Exception('No connection setup to mqtt endpoint')
