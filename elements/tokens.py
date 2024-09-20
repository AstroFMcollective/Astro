import configparser

service_keys = configparser.ConfigParser()
service_keys.read('service_keys.ini')

tokens = configparser.ConfigParser()
tokens.read('tokens.ini')