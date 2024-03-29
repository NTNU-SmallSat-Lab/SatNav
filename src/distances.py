import numpy as np
from skyfield.api import load, wgs84
from logger import logger as log

def distance_obj_to_target(t, obj, target, observer):
    """
    Compute the linear distance between an orbiting object and a target at time t.
    
    Arguments:
        t: skyfield time object
        obj: skyfield object
        target: skyfield object
        observer: skyfield object

    Returns:
        float, distance in km
    """
    
    target_position = observer.at(t).observe(target).position.km

    obj_position = obj.at(t).position.km
    
    return np.linalg.norm(target_position - obj_position)

def get_minimum_distance(t_start, t_end, obj, target, observer, search_interval=1):
    """
    Find the time when the distance between an object and a target is minimum within a timeframe.
    
    Arguments: 
        t_start: skyfield time object
        t_end: skyfield time object
        obj: skyfield object
        target: skyfield object
        observer: skyfield object
        search_interval: float, time step in minutes
        
    Returns:
        min_d: float, minimum distance in km
        min_t: datetime object, time of minimum distance
    """
    
    search_interval = search_interval * 1/24/60 # Transform from minutes to days
    
    min_d = distance_obj_to_target(t_start, obj, target, observer)
    min_t = t_start
    total_iterations = (t_end.tt - t_start.tt) / search_interval
    iter = 0
    
    log.debug('Looking for minimum distance between {} and {} from {} to {} with search_interval {}.'.format(obj.name, target, t_start.tt_strftime('%Y-%m-%d %H:%M:%S'), t_end.tt_strftime('%Y-%m-%d %H:%M:%S'), search_interval))
    while t_start.tt + search_interval*iter < t_end.tt:
        progress = iter / total_iterations * 100
        print(f"Progress: {progress:.1f}%", end='\r')
        # print('Completed ', progress, "%", end='\r')
        
        iter += 1
        t = t_start + search_interval*iter
        d = distance_obj_to_target(t, obj, target, observer)
        if d < min_d:
            min_t = t
            min_d = d
            
    log.debug('Minimum distance found at {} with distance {} km.'.format(min_t.utc_datetime(), min_d))
    min_t = min_t.utc_datetime()
    
    return min_d, min_t