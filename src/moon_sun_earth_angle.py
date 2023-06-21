from celestial_bodies import *
from distances import *
from skyfield.api import load
import numpy as np
from datetime import timedelta

def distance_pos(t, pos1, pos2):
    return np.linalg.norm(pos1 - pos2)

def position_body(t, body, observer):
    body_position = observer.at(t).observe(body).position.km
    
    return body_position

def calculate_angle(pos_sun, pos_earth, pos_moon):
    # Convert positions to numpy arrays for easier calculations
    pos_sun = np.array(pos_sun)
    pos_earth = np.array(pos_earth)
    pos_moon = np.array(pos_moon)

    # Calculate vectors from Earth to Sun and Moon
    vec_sun_earth = pos_sun - pos_earth
    vec_moon_earth = pos_moon - pos_earth

    # Calculate the dot product between the vectors
    dot_product = np.dot(vec_sun_earth, vec_moon_earth)

    # Calculate the magnitudes of the vectors
    magnitude_sun_earth = np.linalg.norm(vec_sun_earth)
    magnitude_moon_earth = np.linalg.norm(vec_moon_earth)

    # Calculate the angle in radians using the arccosine function
    angle_rad = np.arccos(dot_product / (magnitude_sun_earth * magnitude_moon_earth))

    # Convert the angle to degrees
    angle_deg = np.degrees(angle_rad)

    return angle_deg

def calculate_angle_2(pos_sun, pos_earth, pos_moon):
    # calculate the angle between the moon, earth and sun, so that on full moon the angle is 0 degrees
    # and on new moon the angle is 180 degrees. This is opposite of the angle calculated in calculate_angle()
    
    # Convert positions to numpy arrays for easier calculations
    pos_sun = np.array(pos_sun)
    pos_earth = np.array(pos_earth)
    pos_moon = np.array(pos_moon)
    
    # Calculate vectors from Earth to Sun and Moon
    vec_sun_earth = pos_sun - pos_earth
    vec_moon_earth = pos_moon - pos_earth
    
    # Calculate the dot product between the vectors
    dot_product = np.dot(vec_sun_earth, vec_moon_earth)
    
    # Calculate the magnitudes of the vectors
    magnitude_sun_earth = np.linalg.norm(vec_sun_earth)
    magnitude_moon_earth = np.linalg.norm(vec_moon_earth)
    
    # Calculate the angle in radians using the arccosine function
    angle_rad = np.arccos(dot_product / (magnitude_sun_earth * magnitude_moon_earth))
    
    # Convert the angle to degrees
    angle_deg = np.degrees(angle_rad)
    
    # Calculate the angle between the moon, earth and sun
    angle_deg = 180 - angle_deg
    
    return angle_deg

ts = load.timescale()
t_now = ts.now()
# t_var = t_now - timedelta(days = 1)
# 44 days, 21 hours, 34 minutes and 42 seconds
t_var = t_now - timedelta(days = 44, hours = 21, minutes = 34, seconds = 42)

planets = load('de421.bsp')
earth = planets['earth']
moon = planets['moon']
sun = planets['sun']

pos_sun = position_body(t_var, sun, earth)
pos_earth = position_body(t_var, earth, earth)
pos_moon = position_body(t_var, moon, earth)
print('pos_sun: ', pos_sun)
print('pos_earth: ', pos_earth)
print('pos_moon: ', pos_moon)

distance_earth_sun = distance_pos(t_var, pos_sun, pos_earth)
distance_earth_moon = distance_pos(t_var, pos_moon, pos_earth)

print('distance earth sun: ', distance_earth_sun)
print('distance earth moon: ', distance_earth_moon)

# Calculate the angle between sun, earth and moon at specific times
angle = calculate_angle(pos_sun, pos_earth, pos_moon)
angle_2 = calculate_angle_2(pos_sun, pos_earth, pos_moon)
print('Angle: ', angle)
print('Angle 2: ', angle_2)