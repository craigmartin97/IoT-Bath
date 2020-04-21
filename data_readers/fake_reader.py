from random import randint

from data_readers.common import DataReader


class FakeDataReader(DataReader):
    def reset(self):
        print('Reset reader')

    def read_temp(self):
        raise NotImplementedError('TODO: Temperature sensor')

    def read_water_height(self):
        return randint(0, 1000)

    def cold_tap_on(self):
        print('Cold tap is ON')

    def cold_tap_off(self):
        print('Cold tap is OFF')

    def hot_tap_on(self):
        print('Hot tap is ON')

    def hot_tap_off(self):
        print('Hot tap is OFF')

