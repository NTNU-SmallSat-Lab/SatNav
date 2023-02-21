from config_reader import read_config
from satellite import get_satellite
from distances import *
from satellite_orientation import get_quaternion
from logger import logger as log
from skyfield.api import load
import argparse
from datetime import timedelta

config_path = 'src/data/config/config.json'

def main():
    ts = load.timescale()
    
    log.info('\n--------Starting main.py--------\n')

    config = read_config(config_path)

    if not config:
        log.error('Error reading config file. Exiting.')
        return   
    
    t_now = ts.now()
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--catnr', help='Satellite catalog number (default is Hypso-1, 51053)', default=51053, type=int)
    ap.add_argument('-s', '--start_time_delta', help='Hours in the future for start time of search (default is 0 (now))', default=0, type=float)
    ap.add_argument('-e', '--end_time_delta', help='Hours in the future for end time of search (default is 24 (1 day from now))', default=24, type=float)
    ap.add_argument('-t', '--tolerance', help='Tolerance for minimum distance search (default is 1/24/60 (1 minute)) IMPORTANT: Too low tolerance can result in the earth being between the satellite and the target. No lower than 1/24/30 is recommended.', default=1/24/60, type=float)
    ap.add_argument('-f', '--force_update', help='Force update of TLE data', type=bool, default=False)
    
    args = ap.parse_args()
    
    config['catnr'] = args.catnr
    t_start = t_now + timedelta(hours=args.start_time_delta)
    t_end = t_now + timedelta(hours=args.end_time_delta)
    force = args.force_update
    tol = args.tolerance

    log.info('Using satellite catalog number: ' + str(config['catnr']))
    log.info('Using start time: {} UTC'.format(t_start.tt_strftime('%Y-%m-%d %H:%M:%S')))
    log.info('Using end time: {} UTC'.format(t_end.tt_strftime('%Y-%m-%d %H:%M:%S')))
    
    sat = get_satellite(config, force)
    log.info('Config: ' + str(config))
    log.info('Epoch: ' + str(sat))

    _, min_distance_time_datetime = get_minimum_distance(t_start, t_end, sat, tolerance=tol)
    min_distance_time = ts.from_datetime(min_distance_time_datetime)

    get_quaternion(min_distance_time_datetime, min_distance_time, earth, moon, sat)
    
if __name__ == '__main__':
    main()