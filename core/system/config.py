import configparser
import os

def load_config(app_name):
    config_path = _get_config_path(app_name)
    config = configparser.ConfigParser()
    config.read(config_path)
    config.save = lambda: _save(config, config_path)
    config.setvalue = lambda s, o, v: _setvalue(config, s, o, v)
    config.setdefault = lambda s, o, v: _setdefault(config, s, o, v)
    return config

def _get_config_path(app_name):
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, '.config', app_name)
    os.makedirs(config_dir, exist_ok=True)  # Create the directory if it doesn't exist
    config_file = os.path.join(config_dir, 'config.ini')
    return config_file

def _save(config, config_path):
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def _setvalue(config, section, option, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)
    config.save()

def _setdefault(config, section, option, value):
    if not config.has_section(section):
        config.add_section(section)
    if config.get(section, option, fallback=None) is None:
        config.set(section, option, value)
    config.save()
