import os
import sys
import configparser

# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_config():
    configPath = os.path.join(application_path, "settings.txt")

    try:
        with open(configPath) as f:
            print(f"Found configuration at: {str(configPath)}")
    except IOError:
        print("No configuration file found, all values will be defaulted. "
              "Please confirm there's a settings.txt file in the same directory as the executable.")

    config = configparser.ConfigParser()

    config.read(configPath)

    _check_config(config)

    config.add_section("PATHS")
    config.set("PATHS", "application.path", application_path)

    return config


def _check_config(config: configparser.ConfigParser):
    if is_null_or_empty(config.get("CONNECTION", "server.port", fallback=None)):
        print("no server.port setting found, defaulting to port 4455")
        config["CONNECTION"]["server.port"] = "4455"

    if is_null_or_empty(config.get("SCENE", "scene.name", fallback=None)):
        print("no scene.name setting found, defaulting to \"Scene\"")
        config["SCENE"]["scene.name"] = "Scene"

    if is_null_or_empty(config.get("SCENE", "audio.capture.feed", fallback=None)):
        print("no audio.capture.feed setting found, voice will not be captured")


def is_null_or_empty(value: str):
    if value and len(value) > 0:
        return False
    return True
