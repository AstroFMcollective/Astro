import configparser

tokens = configparser.ConfigParser()
tokens.read('AstroDiscord/tokens.ini')

text = configparser.ConfigParser()
text.read('AstroDiscord/text.ini')

config = configparser.ConfigParser()
config.read('AstroDiscord/config.ini')