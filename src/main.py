from config_reader import read_config
from celestial_bodies import *
from distances import *
from quaternions import get_quaternion
from logger import logger as log
from logger import set_log_level
import planner
from skyfield.api import load
from datetime import timedelta
from pyfiglet import Figlet
import json

config_path = 'src/data/config/config.json'

planets = load('de421.bsp')
earth = planets['earth']

def single_planner(t_start, t_end, sat, target, observer, search_interval, ts):
    log.info('Single planner')
    min_distance_time_ts, q_ob, off_nadir = planner.single_planner(t_start, t_end, sat, target, observer, search_interval, ts)
    
    log.info('----------------------------------------------------')
    log.info('Time = {}'.format(min_distance_time_ts))
    log.info('Qx = {:.10f}'.format(q_ob[1]))
    log.info('Qy = {:.10f}'.format(q_ob[2]))
    log.info('Qz = {:.10f}'.format(q_ob[3]))
    log.info('Qs = {:.10f}'.format(q_ob[0]))
    log.info('Off-nadir angle = {:.10f} degrees'.format(off_nadir))
    log.info('----------------------------------------------------')
    
def multi_planner(t_start, t_end, sat, target, intervals, earth, search_interval, ts):
    log.info('Multi planner')
    plan = planner.multi_planner(t_start, t_end, sat, target, earth, intervals, search_interval, ts)
    
    log.info('----------------------------------------------------')
    count = 1
    for time, quaternion, off_nadir in plan:
        log.info('Capture nr. {}'.format(count))
        log.info('Time = {}'.format(time))
        log.info('Qx = {:.10f}'.format(quaternion[1]))
        log.info('Qy = {:.10f}'.format(quaternion[2]))
        log.info('Qz = {:.10f}'.format(quaternion[3]))
        log.info('Qs = {:.10f}'.format(quaternion[0]))
        log.info('Off-nadir angle = {:.10f} degrees\n'.format(off_nadir))
        count += 1
    
    log.info('----------------------------------------------------')
    
    # Save plan to txt file
    with open('plan.txt', 'w') as f:
        f.write('Capture nr. | Time | Qx | Qy | Qz | Qs | Off-nadir angle\n')
        count = 1
        for time, quaternion, off_nadir in plan:
            f.write('{} | {} | {:.10f} | {:.10f} | {:.10f} | {:.10f} | {:.10f}\n'.format(count, time, quaternion[1], quaternion[2], quaternion[3], quaternion[0], off_nadir))
            count += 1
    
if __name__ == '__main__':
    ts = load.timescale()
    t_now = ts.now()
    
    config = read_config(config_path)
    if not config:
        log.error('Error reading config file. Exiting.')
        exit
        
    set_log_level(config['log_level'])
    
    f = Figlet(font='slant')
    print(f.renderText('SatNav'))
    print('\033[34m' + '\033[1m' + '--------Satellite Targeting Tool--------\n' + '\033[0m', end='')
    print('Enter the following information to configure the tool. Press enter to use default value.\n', end='')
    
    mode = input('Enter ' + '\033[34m' + '1' + '\033[0m' + ' to run in single planner mode, or ' + '\033[34m' + '2' + '\033[0m' + ' to run in multi planner mode (default is ' + '\033[34m' + '1' + '\033[0m' + '): ') or '1'
    config['catnr'] = int(input('Enter satellite catalog number (default is ' + '\033[34m' + '51053' + '\033[0m' + ' (HYPSO-1)): ') or 51053)
    target = int(input('Enter target segment number (default is ' + '\033[34m' + '301' + '\033[0m' + ' (the moon). See README for supported bodies): ') or 301)
    start_time_delta = float(input('Enter hours in the future for start time of search (default is ' + '\033[34m' + '0' + '\033[0m' + ' (now)): ') or 0)
    end_time_delta = float(input('Enter hours in the future for end time of search (default is ' + '\033[34m' + '24' + '\033[0m' + ' (1 day from now)): ') or 24)
    if mode == '2':
        intervals = int(input('Enter number of intervals to search (default is ' + '\033[34m' + 'end_time_delta/24' + '\033[0m' + ' (one capture per day)): ') or round((end_time_delta-start_time_delta)/24))
        
    search_interval = float(input('Enter search_interval for minimum distance search (default is 1 (1 minute)): ') or 1)
    force = input('Enter ' + '\033[34m' + 'true' + '\033[0m' + ' to force update TLE data, or press Enter to skip: ').lower() == 'true'
    
    t_start = t_now + timedelta(hours=start_time_delta)
    t_end = t_now + timedelta(hours=end_time_delta)
    
    log.info('Using satellite catalog number: ' + str(config['catnr']))
    log.info('Using start time: {} UTC'.format(t_start.tt_strftime('%Y-%m-%d %H:%M:%S')))
    log.info('Using end time: {} UTC'.format(t_end.tt_strftime('%Y-%m-%d %H:%M:%S')))
    
    sat = get_satellite(config, force)
    target = get_target(target)
    log.info('Config: ' + json.dumps(config, indent=4))
    log.info('Epoch: ' + str(sat))
    
    if mode == '1':
        single_planner(t_start, t_end, sat, target, earth, search_interval, ts)
    elif mode == '2':
        multi_planner(t_start, t_end, sat, target, intervals, earth, search_interval, ts)