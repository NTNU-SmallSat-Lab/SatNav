import argparse
from celestial_bodies import get_satellite_from_catnr, get_target
from datetime import timedelta
from distances import distance_obj_to_target
import numpy as np
import math
from logger import logger as log
from logger import set_log_level
from planner import multi_planner

from skyfield.api import load

set_log_level('INFO')

def plan_hypso_moon_capture(t_start_delta=0, t_end_delta=72, intervals=3, search_interval=1):
    """
    Calculates the minimum distance between the satellite and target for a given time frame and
    the corresponding quaternion for each time frame.

    :param t_start_delta: The start time of the time frame.
    :param t_end_delta: The end time of the time frame.
    :param intervals: The number of intervals to split the time frame into.
    :param search_interval: The search_interval for the minimum distance calculation.
    :return: A list of tuples containing the minimum distance time and corresponding quaternion for
             each time frame.
    """
    
    ts = load.timescale()
    t_now = ts.now()

    tle_url = 'http://celestrak.org/NORAD/elements/gp.php?CATNR='
    sat = get_satellite_from_catnr(51053, tle_url, True)
    target = get_target(301)
    planets = load('de421.bsp')
    earth = planets['earth']
    moon = planets['moon']
    sun = planets['sun']
    
    t_start = t_now + timedelta(hours=t_start_delta)
    t_end = t_now + timedelta(hours=t_end_delta)
    
    results = multi_planner(t_start, t_end, sat, target, earth, intervals, search_interval, ts)

    results_dict = {}
    for i, result in enumerate(results):
        off_nadir_angle = result[2]
        quaternions = result[1]
        capture_time_utc = result[0]
        capture_start = int(result[0].timestamp())
        total_time = calculate_total_capture_time(off_nadir_angle)
        # capture_time_start = calculate_capture_start_time(capture_time, total_time)
        frames, fps = calculate_frames(total_time)
        t_start = ts.utc(capture_time_utc) 
        d_sun_moon = round(distance_obj_to_target(t_start, sun, moon, sun))
        d_sat_moon = round(distance_obj_to_target(t_start, sat, moon, earth))
        
        results_dict[f'capture_{i+1}'] = {'datetime_center': capture_time_utc, 'capture_start': capture_start, 'qs (r)': quaternions[0], 'qx (l)': quaternions[1], 'qy (j)': quaternions[2], 'qz (k)': quaternions[3], 'fps': fps, 'frames': frames, 'total_time': total_time, 'off_nadir_angle': off_nadir_angle, 'd_sun_moon': d_sun_moon, 'd_sat_moon': d_sat_moon}

    return results_dict
    
def calculate_total_capture_time(off_nadir_angle):
    """
    Calculates the total capture time for a given off-nadir angle.

    :param off_nadir_angle: The off-nadir angle.
    :return: The total capture time in seconds.
    """
    
    off_nadir_angle_rad = np.deg2rad(off_nadir_angle)
    extra_rotation_speed = (360/(95*60))*-np.cos(off_nadir_angle_rad)
    moon_fov = 0.52 # moon's field of view in degrees
    sat_speed = 7.6 # satellite's linear speed in km/s
    moon_diameter = 3474 # moon's diameter in km

    total_time = 1/(math.sqrt((sat_speed / moon_diameter)**2 + (extra_rotation_speed / moon_fov)**2))

    return total_time
    
def calculate_capture_start_time(capture_center_time, total_time):
    """
    Calculates the capture start time for a given capture time and off-nadir angle.

    :param capture_time: The capture time.
    :param total_time: The total capture time.
    :return: The capture start time.
    """
    
    capture_start_time = capture_center_time - timedelta(seconds=total_time/2)
    capture_start_time = capture_start_time.timestamp()

    return int(capture_start_time)

def calculate_frames(total_time):
    target_frames = 106
    target_fps = 20

    # Calculate the required FPS to capture the object in the given time
    required_fps = target_frames / total_time
    required_fps = max(min(required_fps, target_fps), 1)  # Ensure the FPS is between 1 and 20

    # Calculate the number of frames based on the required FPS
    num_frames = round(total_time * required_fps)

    return num_frames, required_fps

def create_script_generator_cmd(capture, buff_file=33, append=True):
    """ 
    Creates the command to run the script generator.
     
    :param capture: The capture dictionary.
    :param buff_file: The buff file.
    :return: The command to run the script generator.
    """
    
    capture_start = capture['capture_start']
    
    r = capture['qs (r)']
    l = capture['qx (l)']
    j = capture['qy (j)']
    k = capture['qz (k)']
    
    if k < 1e-15:
        k = 0.0
    
    fps = math.floor(capture['fps'])
    frames = capture['frames']
    
    # Adjust fps
    fps = fps/2
    fps = math.ceil(fps)
    
    # Add the datetime and off-nadir angle to the command after %
    if append:
        # cmd = f'-b {buff_file} -u {capture_start} -s -a -p nonbinned -n moon -d -e 50.0 -r {r} -l {l} -j {j} -k {k} -fps {fps} -fr {frames} % {capture["datetime_center"]}, off-nadir: {capture["off_nadir_angle"]}, d_sun_moon: {capture["d_sun_moon"]} km, d_sat_moon: {capture["d_sat_moon"]} km'
        cmd = f'-b {buff_file} -u {capture_start} -s -a -p nonbinned -n moon -d -e 50.0 -r {r} -l {l} -j {j} -k {k} -fps {fps} % {capture["datetime_center"]}, off-nadir: {capture["off_nadir_angle"]}, d_sun_moon: {capture["d_sun_moon"]} km, d_sat_moon: {capture["d_sat_moon"]} km'
    else:
        # cmd = f'-b {buff_file} -u {capture_start} -s -p nonbinned -n moon -d -e 50.0 -r {r} -l {l} -j {j} -k {k} -fps {fps} -fr {frames} % {capture["datetime_center"]}, off-nadir: {capture["off_nadir_angle"]}, d_sun_moon: {capture["d_sun_moon"]} km, d_sat_moon: {capture["d_sat_moon"]} km'
        cmd = f'-b {buff_file} -u {capture_start} -s -a -p nonbinned -n moon -d -e 50.0 -r {r} -l {l} -j {j} -k {k} -fps {fps} % {capture["datetime_center"]}, off-nadir: {capture["off_nadir_angle"]}, d_sun_moon: {capture["d_sun_moon"]} km, d_sat_moon: {capture["d_sat_moon"]} km'

    return cmd

def get_script_generator_cmds(start_time_delta, end_time_delta, intervals, search_interval, buff_file, append):
    t_now = load.timescale().now()
    t_start = t_now + timedelta(hours=start_time_delta)
    t_end = t_now + timedelta(hours=end_time_delta)
    log.info('Using start time: {} UTC'.format(t_start.tt_strftime('%Y-%m-%d %H:%M:%S')))
    log.info('Using end time: {} UTC'.format(t_end.tt_strftime('%Y-%m-%d %H:%M:%S')))
    log.info('Using {} intervals with {} seconds between each search'.format(intervals, round(search_interval*60)))

    plans = plan_hypso_moon_capture(start_time_delta, end_time_delta, intervals=intervals, search_interval=search_interval)

    # log.info('Generated the following plans:')
    # for key in plans:
    #     log.info('Capture {}:'.format(key))
    #     log.info('\tCapture time utc: {}'.format(plans[key]['datetime_center']))
    #     log.info('\tCapture time unix: {}'.format(plans[key]['capture_start']))
    #     log.info('\tOff-nadir angle: {}'.format(plans[key]['off_nadir_angle']))
    #     log.info('\tTotal capture time: {}'.format(plans[key]['total_time']))
    #     log.info('\tFrames: {}'.format(plans[key]['frames']))
    #     log.info('\tFPS: {}'.format(plans[key]['fps']))
    #     log.info('')
    
    append = True
    if len(plans) <= 1:
        append = False
        
    log.info('Generated the following commands:')
    for key in plans:
        cmd = create_script_generator_cmd(plans[key], append=append)
        print(cmd)

default_start_delta = 0
default_end_delta = 24
default_search_interval = 1
default_buff = 33
default_append = False

# Add the command line arguments
parser = argparse.ArgumentParser(description='Generate the script generator commands for moon captures.')
parser.add_argument('-s', '--start', type=int, default=0, help=(f'The start time delta in hours. Default is {default_start_delta}.'))
parser.add_argument('-e', '--end', type=int, default=24, help=(f'The end time delta in hours. Default is {default_end_delta}.'))
parser.add_argument('-i', '--intervals', type=int, default=None, help='The number of intervals to use. Default is (-e - -s)/24 (one capture per day).')
parser.add_argument('-t', '--time_interval', type=float, default=default_search_interval, help=(f'The time interval to use when searching. Default is {default_search_interval} (1, i.e. every minute).'))
parser.add_argument('-b', '--buff', type=int, default=default_buff, help=(f'The buff file to use. Defualt is {default_buff}.'))
parser.add_argument('-a', '--append', type=bool, default=default_append, help=(f'Set to true if you plan multiple captures. Default is {default_append}.'))

# Parse the command line arguments
args = parser.parse_args()
args.intervals = args.intervals if args.intervals is not None else int((args.end - args.start) / 24)
 
get_script_generator_cmds(args.start, args.end, args.intervals, args.time_interval, args.buff, args.append)