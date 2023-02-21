import json
import os
from logger import logger as log

def read_config(config_file):
    # Check if config file exists or if contents are empty
    if not os.path.exists(config_file):
        log.info(f'Config file not found: {config_file}. Reading default config file.')
        
        # Read default config file
        default_config_path = os.path.join(os.path.dirname(config_file), 'defaults', os.path.basename(config_file))    
        config_file = create_config_from_default(default_config_path, save_path=config_file)
    elif os.path.getsize(config_file) == 0:
        log.info(f'Config file is empty: {config_file}. Reading default config file.')
        
        # Read default config file
        default_config_path = os.path.join(os.path.dirname(config_file), 'defaults', os.path.basename(config_file))    
        config_file = create_config_from_default(default_config_path, save_path=config_file)
    
    # Read the config file
    try:
        with open(config_file) as f:
            data = json.load(f)
    except(FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f'Error reading config file: {e}')
        return None
    
    return data
    
def create_config_from_default(default_file, save_path=None):
    # Check if default config file exists
    if not os.path.exists(default_file):
        log.info(f'Default config file not found: {default_file}')
        return None
    
    # Read the default config file
    try: 
        with open(default_file) as f:
            data = json.load(f)
    except(FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f'Error reading default config file: {e}')
        return None
    
    # Create config file
    config_file = os.path.join(os.path.dirname(default_file), os.path.basename(default_file).replace('default_', ''))
    try:
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=4)
            log.info("Created config file from default at path " + config_file)
    except(FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f'Error creating config file: {e}')
        return None
    
    return config_file