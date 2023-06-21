# StarNav

StarNav is a Python program designed to calculate the precise UTC time when a satellite is closest to a target (e.g., the Moon) and then generate a quaternion to point the satellite's sensors towards that target.

## Installation

To install the program, clone the repository to your local machine:

`git clone https://github.com/NTNU-SmallSat-Lab/StarNav.git`

Then navigate to the root directory of the project and install the required dependencies using pip:

`pip3 install -r requirements.txt`

## Usage

### HYPSO-1 specific planning:
To plan for a capture of the Moon by HYPSO-1, run `python3 src/hypso_moon_script_cmd_generator.py`. 
For help on the script, run `python3 src/hypso_moon_script_cmd_generator.py -h`.
This script creates the necessary commands to create FC- and PC-scripts through NTNU-SmallSat_Lab's script generator, see https://github.com/NTNU-SmallSat-Lab/flight-scripts/tree/main/script_generator for more information.

### General usage:

To run the program, run `python3 src/main.py`.

The program will ask for the following parameters, empty inputs will use the default values:

* If the goal is to calculate a single capture, or plan a range of captures. 

**Default = 1**, i.e. single capture.

* The satellite catalog number (e.g. 25544 for the ISS). 

**Default = 51053**, i.e. HYPSO-1.

* The start time delta (in hours) for search from the current time. 

**Default = 0**, i.e. now.

* The end time delta (in hours) for search from the current time. 

**Default = 24**, i.e. 1 day from now.

* If the goal is to plan a range of captures, the interval (in hours) between each capture.

**Default = end_time-start_time/24**, i.e. one capture per day.

* The search interval (in days) for minimum time distance of search. 

**Default = 1/24/60**, i.e. 1 minute.

* Force flag to force download of TLE files. 

**Default = False**.

TLE files are required to calculate the satellites's position and velocity. These are automatically downloaded from Celestrak if they are not present in the 'data' directory, or if it is more than 24 hours since the last download. Else it is assumed that the TLE files are up to date.

The program will calculate the precise UTC time when the satellite is closest to the target and generate the quaternion to point the satellite's sensors. These are printed to the console. If the goal is to plan a range of captures, the program will generate a file called `plan.txt` in the root directory of the project. This file contains the UTC time, quaternion and off nadir angle for each capture.

## Supported Celestial Bodies
* 301 -> MOON
* 399 -> EARTH 
* 199 -> MERCURY
* 299 -> VENUS
* 499 -> MARS

## Known Issues

* There is no check to ensure that the target is not obscured by the Earth. This should not happen as it then clearly is not in it's closes point in orbit, but can happen if the search interval parameter is too low. This check will be added in the future.

* The program is under development, and unknown bugs are to be expected.

## License

This program is licensed under the Apache-2.0 License. See the `LICENSE` file for more information.