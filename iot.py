#Libraries
import RPi.GPIO as GPIO
from datetime import datetime
import time

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 22
GPIO_ECHO = 27

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#Testing
last_data_sent = 0
readings = []

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def send_metrics(data):
    
    print('sending data to api: {}'.format(data))
    
    pass 

def check_readings(readings, last):
    
    avg_reading = sum(readings) / len(readings) 
    
    if abs(avg_reading - last) > 30:
        send_metrics({'distance': dist, 'timestamp': str(datetime.utcnow())})
        return avg_reading
            
    return last

if __name__ == '__main__':
    try:
        while True:
            
            readings = []
            
            for i in range(0, 4):
                dist = distance()
                readings.append(dist)
                print ("Measured Distance = %.1f cm" % dist)
                time.sleep(0.1)
            
            
            last_data_sent = check_readings(readings, last_data_sent)
            

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
