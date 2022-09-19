import os
import sys
import configparser

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


def readConfig():
    configFolder = os.path.dirname(application_path)
    configPath = os.path.join(configFolder, "settings.txt")

    print("Found configuration at: " + str(configPath))

    config = configparser.ConfigParser()

    config.read(configPath)

    checkConfig(config)

    return config


def checkConfig(config):
    if config['DEFAULT'].get('server.port') is None:
        print("no server.port setting found, defaulting to port 4444")
        config['DEFAULT'] = {
            'server.port': '4444'
        }