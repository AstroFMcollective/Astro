import configparser

service_keys = configparser.ConfigParser()
service_keys.read('AstroAPI/components/keys.ini')

text = configparser.ConfigParser()
text.read('AstroAPI/components/text.ini')