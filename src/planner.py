from distances import get_minimum_distance
from quaternions import get_quaternion, get_off_nadir_angle, get_maximum_off_nadir_angle

from logger import logger as log

def multi_planner(t_start, t_end, sat, target, observer, intervals, search_interval, ts):
    """
    Calculates the minimum distance between the satellite and target for a given time frame and
    the corresponding quaternion for each time frame.

    :param t_start: The start time of the time frame.
    :param t_end: The end time of the time frame.
    :param sat: The satellite object.
    :param target: The target object.
    :param observer: The observer object.
    :param intervals: The number of intervals to split the time frame into.
    :param search_interval: The search_interval for the minimum distance calculation.
    :param ts: The timescale object.
    :return: A list of tuples containing the minimum distance time and corresponding quaternion for
             each time frame.
    """
    
    duration = (t_end - t_start) / intervals
    
    results = []
    for i in range(intervals):
        # log.info('Completed {}%'.format(round(i / intervals * 100, 2)))
        log.info(f'Completed {i}/{intervals}')
        # Calculate the start and end times for the current time frame
        new_t_start = t_start + i * duration
        new_t_end = new_t_start + duration
        
        # # Calculate the minimum distance and corresponding quaternion for the current time frame
        # _, min_distance_time_datetime = get_minimum_distance(new_t_start, new_t_end, sat, target, observer, search_interval=search_interval)
        # min_distance_time_ts = ts.from_datetime(min_distance_time_datetime)
        # quaternion = get_quaternion(min_distance_time_ts, observer, target, sat)
        # off_nadir_angle = get_off_nadir_angle(min_distance_time_ts, observer, target, sat)
        
        # # Store the results for the current time frame
        # results.append((min_distance_time_datetime, quaternion, off_nadir_angle))
        
        # Calculate the maximum off nadir angle and corresponding quaternion for the current time frame
        off_nadir_angle, max_off_nadir_time_datetime = get_maximum_off_nadir_angle(new_t_start, new_t_end, sat, target, observer, search_interval=search_interval)
        max_off_nadir_time_ts = ts.from_datetime(max_off_nadir_time_datetime)
        quaternion = get_quaternion(max_off_nadir_time_ts, observer, target, sat)
        
        # Store the results for the current time frame
        results.append((max_off_nadir_time_datetime, quaternion, off_nadir_angle))
    
    return results

def single_planner(t_start, t_end, sat, target, observer, search_interval, ts):
    """
    Calculates the minimum distance between the satellite and target for a given time frame and
    the corresponding quaternion.

    :param t_start: The start time of the time frame.
    :param t_end: The end time of the time frame.
    :param sat: The satellite object.
    :param target: The target object.
    :param observer: The observer object.
    :param search_interval: The search_interval for the minimum distance calculation.
    :param ts: The timescale object.
    :return: The minimum distance time and corresponding quaternion.
    """
    
    # _, min_distance_time_datetime = get_minimum_distance(t_start, t_end, sat, target, observer, search_interval=search_interval) 
    # min_distance_time_ts = ts.from_datetime(min_distance_time_datetime)
    # quaternion = get_quaternion(min_distance_time_ts, observer, target, sat)
    # off_nadir_angle = get_off_nadir_angle(min_distance_time_ts, observer,target, sat)
    
    # return min_distance_time_datetime, quaternion, off_nadir_angle
    
    off_nadir_angle, max_off_nadir_time_datetime = get_maximum_off_nadir_angle(t_start, t_end, sat, target, observer, search_interval=search_interval)
    max_off_nadir_time_ts = ts.from_datetime(max_off_nadir_time_datetime)
    quaternion = get_quaternion(max_off_nadir_time_ts, observer, target, sat)
    
    return max_off_nadir_time_datetime, quaternion, off_nadir_angle
    