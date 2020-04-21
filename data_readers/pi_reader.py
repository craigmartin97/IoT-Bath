import RPi.GPIO as GPIO
import time

from data_readers.common import DataReader


class PiDataReader(DataReader):
    def __init__(self):
        # GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # set GPIO Pins
        self.GPIO_TRIGGER = 22
        self.GPIO_ECHO = 27
        self.GPIO_Blue = 23
        self.GPIO_Red = 24

        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)
        GPIO.setup(self.GPIO_Blue, GPIO.OUT)
        GPIO.setup(self.GPIO_Red, GPIO.OUT)

        self.reset()

    def reset(self):
        GPIO.cleanup()

    def read_temp(self):
        raise NotImplementedError('TODO: Temperature sensor')

    def read_water_height(self):
        # set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)

        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(self.GPIO_ECHO) == 0:
            StartTime = time.time()

        # save time of arrival
        while GPIO.input(self.GPIO_ECHO) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2

        return distance

    def cold_tap_on(self):
        GPIO.output(self.GPIO_Blue, True)

    def cold_tap_off(self):
        GPIO.output(self.GPIO_Blue, False)

    def hot_tap_on(self):
        GPIO.output(self.GPIO_Red, True)

    def hot_tap_off(self):
        GPIO.output(self.GPIO_Red, False)

