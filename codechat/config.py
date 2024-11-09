import os
import json
from pathlib import Path
from .user_interface import UserInterface

def get_config_path():
    """Return the appropriate config path based on the operating system."""
    home = Path.home()
    return home / ".codechat" / "config.json"

CONFIG_DIR = os.path.join(Path.home(), ".codechat")
CONFIG_FILE = get_config_path()

DEFAULT_CONFIG = {
    "model": "4o",  # Default model
    "exclude": [
        '**/.git/',
        '**/.gitignore',
        '**/.gptignore',
        '.gpt',
        'poetry.lock',
        "**/*.pyc",
        "**/*__pycache__",
        "**/*.pyo",
        "**/*.pyd",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/*.egg-info/",
        "**/dist/",
        "**/build/",
        "**/*.egg",
        "**/node_modules/",
        "**/npm-debug.log",
        "**/yarn-error.log",
        '**/.DS_Store',
        "**/.idea/",
        "**/.vscode/",
        "**/*.iml",
        "**/*.ipr",
        "**/*.iws",
        "**/*.suo",
        "**/*.user",
        "**/*.userosscache",
        "**/*.sln.docstates",
        "**/*.sln.ide/",
        "**/.DS_Store",
    ]
}

ALLOWED_CONFIG_OPTIONS = {
    "model": str,
    # Add other configuration options and their expected types here
}

ui = UserInterface()

def ensure_config_exists():
    """Ensure that the configuration directory and file exist."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        ui.print_info(f"Created default configuration file at {CONFIG_FILE}")

def load_config(app_name='codechat'):
    """Load the configuration from the config file."""
    ensure_config_exists()
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
    except json.JSONDecodeError:
        ui.print_error(f"Error: Configuration file {CONFIG_FILE} is not valid JSON.")
        config_data = DEFAULT_CONFIG.copy()
    except Exception as e:
        ui.print_error(f"Error loading configuration: {e}")
        config_data = DEFAULT_CONFIG.copy()
    return config_data

def save_config(config_data):
    """Save the configuration to the config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        ui.print_info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        ui.print_error(f"Error saving configuration: {e}")

def update_config(option, value):
    """Update configuration if the option is allowed and the value is of correct type."""
    expected_type = ALLOWED_CONFIG_OPTIONS.get(option)
    if not expected_type:
        raise ValueError(f"Unknown configuration option: '{option}'.")

    # Type checking
    if not isinstance(value, expected_type):
        raise TypeError(f"Invalid type for '{option}'. Expected {expected_type.__name__}.")

    config[option] = value
    save_config(config)

# Load the config at import time
config = load_config()
