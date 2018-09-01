import configparser
import os
import warnings

DEFAULT_CONFIG_FILE = "timestore_config.ini"
_POSTGRES_DB = "POSTGRES_DB"
_POSTGRES_DEFAULTS = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'ts',
    'host': 'localhost',
    'port': '5432'
}


def get_config(config_file=DEFAULT_CONFIG_FILE, create_default=True):
    if create_default and not os.path.isfile(config_file):
        warnings.warn("No config file found. Creating default config file...")
        create_default_config(config_file)

    config = configparser.ConfigParser()
    config.read(config_file)

    return config


def create_default_config(config_file=DEFAULT_CONFIG_FILE):
    with open(config_file, 'w') as configfile:
        config = configparser.ConfigParser()
        config[_POSTGRES_DB] = _POSTGRES_DEFAULTS
        config.write(configfile)


def postgres_db(config_file=DEFAULT_CONFIG_FILE):
    config = get_config(config_file)
    return config[_POSTGRES_DB]
