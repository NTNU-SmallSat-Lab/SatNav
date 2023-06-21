import numpy as np
import scipy.linalg
from logger import logger as log
from celestial_bodies import get_positions, get_velocity
import math

def eci2LVLH(r_i, v_i):
    z_o = -r_i / np.linalg.norm(r_i)
    y_o = -np.cross(r_i, v_i)/np.linalg.norm(np.cross(r_i, v_i))
    x_o = np.cross(y_o, z_o)
    R_o_i = np.array([x_o, y_o, z_o])
    R_i_o = R_o_i.T
    r_o = np.dot(R_i_o, r_i) # position in orbit frame [km]
    v_o = np.dot(R_i_o, v_i) # velocity in orbit frame [km/s]
    
    return r_o, v_o, R_o_i

def rot_rodrigues(a, b, theta):
    a_hat = a/np.linalg.norm(a)
    b_hat = b/np.linalg.norm(b)
    lmbda = np.cross(a_hat, b_hat)
    lmbda_norm = np.linalg.norm(lmbda)
    if lmbda_norm < 1e-12:
        lmbda_hat = lmbda
    else:
        lmbda_hat = lmbda/lmbda_norm
    skew = skew_sym(theta*lmbda_hat)
    R = scipy.linalg.expm(skew)

    return R

        
def skew_sym(x):
    S = [[0, -x[2], x[1]],
        [x[2], 0, -x[0]],
        [-x[1], x[0], 0]]
    
    return S
    
def rot2q(R):  
    theta = np.arccos((np.trace(R)-1)/2)
    if np.isclose(theta, 0):
        e_hat = np.array([0, 0, 0])
    else:
        e_hat = 1/(2*np.sin(theta))*np.array([R[1,2]-R[2,1], R[2,0]-R[0,2], R[0,1]-R[1,0]])

    q_0 = np.cos(theta/2)
    q_1 = e_hat[0]*np.sin(theta/2)
    q_2 = e_hat[1]*np.sin(theta/2)
    q_3 = e_hat[2]*np.sin(theta/2)
    q = np.array([q_0, q_1, q_2, q_3])
    q = q/np.linalg.norm(q)
    
    return q

def get_quaternion(time, earth, target, sat):
    sat_pos, target_pos = get_positions(time, target, sat, earth)
    sat_vel = get_velocity(time, sat)
    log.debug('sat_pos: {}'.format(sat_pos))
    log.debug('sat_vel: {}'.format(sat_vel))

    [r_o, v_o, R_io] = eci2LVLH(sat_pos, sat_vel)

    target_pos_eci = target_pos

    relative_pos = target_pos_eci - sat_pos
    relative_pos_orbit = np.dot(R_io, relative_pos)

    target_unit_vector = relative_pos_orbit / np.linalg.norm(relative_pos_orbit)
    
    # Calculate the nadir vector in the orbit frame
    z_o_hat_o = np.array([0, 0, 1])

    cos_off_nadir_angle = np.dot(target_unit_vector, z_o_hat_o)
    off_nadir_angle = math.degrees(np.arccos(cos_off_nadir_angle))

    # Calculate the rotation quaternion
    z_b_hat_o = target_unit_vector
    R_bo = rot_rodrigues(z_o_hat_o, z_b_hat_o, np.radians(off_nadir_angle))
    R_ob = R_bo.T
    q_ob = rot2q(R_ob)
    
    # log.debug('off_nadir_angle: {}'.format(off_nadir_angle))

    return q_ob

def get_off_nadir_angle(time, earth, target, sat):
    sat_pos, target_pos = get_positions(time, target, sat, earth)
    sat_vel = get_velocity(time, sat)
    log.debug('sat_pos: {}'.format(sat_pos))
    log.debug('sat_vel: {}'.format(sat_vel))

    [r_o, v_o, R_io] = eci2LVLH(sat_pos, sat_vel)

    target_pos_eci = target_pos

    relative_pos = target_pos_eci - sat_pos
    relative_pos_orbit = np.dot(R_io, relative_pos)

    target_unit_vector = relative_pos_orbit / np.linalg.norm(relative_pos_orbit)
    
    # Calculate the nadir vector in the orbit frame
    z_o_hat_o = np.array([0, 0, 1])

    cos_off_nadir_angle = np.dot(target_unit_vector, z_o_hat_o)
    off_nadir_angle = math.degrees(np.arccos(cos_off_nadir_angle))

    return off_nadir_angle

def get_maximum_off_nadir_angle(t_start, t_end, obj, target, observer, search_interval = 1):
    """
    Find the time when the off nadir angle between a satellite and a target is at minimum within a timeframe.
    """
    
    search_interval = search_interval * 1/24/60 # Transform from minutes to days
    
    max_off_nadir = get_off_nadir_angle(t_start, observer, target, obj)
    max_t = t_start
    total_iterations = (t_end.tt - t_start.tt) / search_interval
    iter = 0
    
    log.debug('Looking for maximum off nadir angle between {} and {} from {} to {} with search_interval {}.'.format(obj.name, target, t_start.tt_strftime('%Y-%m-%d %H:%M:%S'), t_end.tt_strftime('%Y-%m-%d %H:%M:%S'), search_interval))
    while t_start.tt + search_interval*iter < t_end.tt:
        progress = iter / total_iterations * 100
        print(f"Progress: {progress:.1f}%", end="\r")
        
        iter += 1 
        t = t_start + search_interval*iter
        off_nadir = get_off_nadir_angle(t, observer, target, obj)
        if off_nadir > max_off_nadir:
            max_t = t
            max_off_nadir = off_nadir
    
    log.debug('Maximum off nadir angle found at {} with angle {} deg.'.format(max_t.utc_datetime(), max_off_nadir))
    max_t = max_t.utc_datetime()
    
    return max_off_nadir, max_t
