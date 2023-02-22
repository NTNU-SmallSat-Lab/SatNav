from skyfield.api import load
import datetime
from logger import logger as log
import json

tle_path = 'src/data/tle_files/tle-CATNR-'
config_path = 'src/data/config/config.json'
tle_url = 'http://celestrak.org/NORAD/elements/gp.php?CATNR='

def get_satellite(config, force_update=False):
    catnr = config['catnr']

    configured_at = config['configured_at']
    try:
        configured_at = datetime.datetime.strptime(configured_at, '%Y-%m-%d %H:%M:%S.%f')
    except: 
        configured_at = datetime.datetime.strptime(configured_at, '%Y-%m-%d %H:%M:%S')
    
    now = datetime.datetime.now()
    time_diff = (now - configured_at).total_seconds()
    
    # If time is more than 24 hours or force_update = True, reload the TLE file from URL
    if abs(time_diff) > 24*60*60 or force_update:
        log.info('Reloading TLE file from URL...')
        url = tle_url + str(catnr)
        filename = tle_path + str(catnr) + '.txt'
        satellites = load.tle_file(url, filename=filename, reload=True)
        sat = satellites[0]
        
        # Update configured_at
        config['last_pulled_tle'] = str(now)
        
        # Save config file
        with open(config_path, 'w') as f:
            json.dump(config, f)
    else:
        try:
            log.info('Loading TLE file from local file...')
            filename = tle_path + str(catnr) + '.txt'
            satellites = load.tle_file(filename)
            sat = satellites[0]
        except FileNotFoundError:
            log.info('TLE file not found, reloading from URL...')
            url = tle_url + str(catnr)
            filename = tle_path + str(catnr) + '.txt'
            satellites = load.tle_file(url, filename=filename, reload=True)
            sat = satellites[0]
                
    # Update config
    config['configured_at'] = str(now)
    config['name'] = sat.name
    
    # Save config file
    with open(config_path, 'w') as f:
        json.dump(config, f)
        
    return sat 

def get_target(target):
    print(target)
    planets = load('de421.bsp')
    target = planets[target]
    if target is not None:
        return target
    else:
        log.error('Target not supported. Exiting.')
        return

def get_positions(time, target, object, observer):
    target_position = observer.at(time).observe(target).position.km
    obj_position = object.at(time).position.km
    
    positions = [obj_position, target_position]

    return positions

def get_velocity(time,  object):
    obj_velocity = object.at(time).velocity.km_per_s
    
    return obj_velocity
