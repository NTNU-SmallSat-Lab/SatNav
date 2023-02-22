import numpy as np
import scipy
from logger import logger as log
import math

def get_positions(earth, time, target, object):
    target_position = earth.at(time).observe(target).position.km
    obj_position = object.at(time).position.km
    
    positions = [obj_position, target_position]

    return positions

def get_velocity(time,  object):
    obj_velocity = object.at(time).velocity.km_per_s
    
    return obj_velocity

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
    lmbda_hat = lmbda/np.linalg.norm(lmbda)
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
    e_hat = 1/(2*np.sin(theta))*np.array([R[1,2]-R[2,1], R[2,0]-R[0,2], R[0,1]-R[1,0]])
    
    q_0 = np.cos(theta/2)
    q_1 = e_hat[0]*np.sin(theta/2)
    q_2 = e_hat[1]*np.sin(theta/2)
    q_3 = e_hat[2]*np.sin(theta/2)
    q = np.array([q_0, q_1, q_2, q_3])
    q = q/np.linalg.norm(q)
    
    return q

def get_quaternion(time, earth, target, sat):
    sat_pos, target_pos = get_positions(earth, time, target, sat)
    sat_vel = get_velocity(time, sat)
    log.info('sat_pos: {}'.format(sat_pos))
    log.info('sat_vel: {}'.format(sat_vel))

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

    log.info('----------------------------------------------------')
    log.info('Time = {}'.format(time.utc_iso()))
    log.info('Qx = {:.10f}'.format(q_ob[1]))
    log.info('Qy = {:.10f}'.format(q_ob[2]))
    log.info('Qz = {:.10f}'.format(q_ob[3]))
    log.info('Qs = {:.10f}'.format(q_ob[0]))
    log.info('----------------------------------------------------')

    log.info('HSI Off-Nadir Pointing Angle: {}'.format(off_nadir_angle))

    return q_ob
