import configparser

config = configparser.ConfigParser()
config.read('AstroAPI/config.ini')

keys = configparser.ConfigParser()
keys.read('AstroAPI/keys.ini')

text = configparser.ConfigParser()
text.read('AstroAPI/text.ini')