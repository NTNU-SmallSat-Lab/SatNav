from config_reader import read_config
from satellite import get_satellite
from distances import *
from satellite_orientation import get_quaternion
from logger import logger as log
from skyfield.api import load
from datetime import timedelta
from pyfiglet import Figlet
import json

config_path = 'src/data/config/config.json'

def main():
    ts = load.timescale()
    t_now = ts.now()
    
    config = read_config(config_path)
    if not config:
        log.error('Error reading config file. Exiting.')
        return   
    
    f = Figlet(font='slant')
    print(f.renderText('SatNav'))
    
    print('\033[34m' + '\033[1m' + '--------Satellite Targeting Tool--------\n' + '\033[0m', end='')
    print('Enter the following information to configure the tool. Press enter to use default value.\n', end='')
    
    config['catnr'] = int(input('Enter satellite catalog number (default is ' + '\033[34m' + '51053' + '\033[0m' + '): ') or config['catnr'])
    start_time_delta = float(input('Enter hours in the future for start time of search (default is ' + '\033[34m' + '0' + '\033[0m' + ' (now)): ') or 0)
    end_time_delta = float(input('Enter hours in the future for end time of search (default is ' + '\033[34m' + '24' + '\033[0m' + ' (1 day from now)): ') or 24)
    tol = float(input('Enter tolerance for minimum distance search (default is + ' + '\033[34m' + '1/24/60' + '\033[0m' + '(1 minute)): ') or 1/24/60)
    force = input('Enter ' + '\033[34m' + 'true' + '\033[0m' + ' to force update TLE data, or press Enter to skip: ').lower() == 'true'
    
    print('\033[0m')
    
    t_start = t_now + timedelta(hours=start_time_delta)
    t_end = t_now + timedelta(hours=end_time_delta)
    
    log.info('Using satellite catalog number: ' + str(config['catnr']))
    log.info('Using start time: {} UTC'.format(t_start.tt_strftime('%Y-%m-%d %H:%M:%S')))
    log.info('Using end time: {} UTC'.format(t_end.tt_strftime('%Y-%m-%d %H:%M:%S')))
    
    sat = get_satellite(config, force)
    log.info('Config: ' + json.dumps(config, indent=4))
    log.info('Epoch: ' + str(sat))

    _, min_distance_time_datetime = get_minimum_distance(t_start, t_end, sat, tolerance=tol)
    min_distance_time_ts = ts.from_datetime(min_distance_time_datetime)

    get_quaternion(min_distance_time_ts, earth, moon, sat)
    
if __name__ == '__main__':
    main()