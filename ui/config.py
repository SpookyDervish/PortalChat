import os
from configparser import ConfigParser, NoOptionError, NoSectionError

DEFAULT_CONFIG = {
    "MyAccount": {
        "username": "user",
        "icon_path": os.path.abspath("assets/images/default_user.png")
    },
    "Appearance": {
        "theme_index": 0,
        "theme": "textual-dark"
    }
}

def conf_get(config: ConfigParser, section: str, option: str):
    try: return config.get(section, option)
    except (NoOptionError, NoSectionError): return DEFAULT_CONFIG[section][option]

def conf_set(config: ConfigParser, section: str, option: str, value: str):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)