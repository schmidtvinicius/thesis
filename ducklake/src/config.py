from configparser import ConfigParser, ExtendedInterpolation

CONFIG = ConfigParser(interpolation=ExtendedInterpolation())
CONFIG.read('config.ini')