import configparser

presence = open('AstroDiscord/components/presence.txt','r').readlines()

tokens = configparser.ConfigParser()
tokens.read('AstroDiscord/tokens.ini')

text = configparser.ConfigParser()
text.read('AstroDiscord/text.ini')

config = configparser.ConfigParser()
config.read('AstroDiscord/config.ini')