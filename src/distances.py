import numpy as np
from skyfield.api import load, wgs84
from logger import logger as log

planets = load('de421.bsp')
earth = planets['earth']

def distance_obj_to_target(t, obj, target, observer=earth):
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
    
    target_position = earth.at(t).observe(target).position.km

    obj_position = obj.at(t).position.km
    
    return np.linalg.norm(target_position - obj_position)

def get_minimum_distance(t_start, t_end, obj, target, observer=earth, tolerance=1/86400):
    """
    Find the time when the distance between an object and a target is minimum within a timeframe.
    
    Arguments: 
        t_start: skyfield time object
        t_end: skyfield time object
        obj: skyfield object
        target: skyfield object
        observer: skyfield object
        tolerance: float, time step in days
        
    Returns:
        min_d: float, minimum distance in km
        min_t: datetime object, time of minimum distance
    """
    min_d = distance_obj_to_target(t_start, obj, target, observer)
    min_t = t_start
    iter = 0
    
    log.info('Looking for minimum distance between {} and {} from {} to {} with tolerance {}.'.format(obj.name, target, t_start.tt_strftime('%Y-%m-%d %H:%M:%S'), t_end.tt_strftime('%Y-%m-%d %H:%M:%S'), tolerance))
    while t_start.tt + tolerance*iter < t_end.tt:
        progress = round(iter/(1/tolerance)*100)
        print('Completed ', progress, "%", end='\r')
        
        iter += 1
        t = t_start + tolerance*iter
        d = distance_obj_to_target(t, obj, target, observer)
        if d < min_d:
            min_t = t
            min_d = d
            
    log.info('Minimum distance found at {} with distance {} km.'.format(min_t.utc_datetime(), min_d))
    min_t = min_t.utc_datetime()
    
    return min_d, min_t

def get_positions_at(t_start, t_end, obj, tolerance):
    positions = []
    iter = 0
    while t_start.tt + tolerance*iter < t_end.tt:
        iter +=1
        t = t_start + tolerance*iter
        position = obj.at(t).position.km
        positions.append(position)
        
    return positions

def get_positions_obs(t_start, t_end, obj, tolerance, observer=earth):
    positions = []
    iter = 0
    while t_start.tt + tolerance*iter < t_end.tt:
        iter +=1
        t = t_start + tolerance*iter
        position = observer.at(t).observe(obj).position.km
        positions.append(position)
        
    return positions

