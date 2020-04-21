import abc


class DataReader(object):
    """
    Basically just an interface, but keeping as a class in case we need to add anything later
    """
    @abc.abstractmethod
    def reset(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def read_temp(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def read_water_height(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def cold_tap_on(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def cold_tap_off(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def hot_tap_on(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def hot_tap_off(self):
        raise NotImplementedError()
