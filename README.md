
# StarNav

StarNav is a Python program designed to calculate the precise UTC time when a satellite is closest to a target (e.g., the Moon) and then generate a quaternion to point the satellite's sensors towards that target.

## Installation

To install the program, clone the repository to your local machine:

`git clone https://github.com/NTNU-SmallSat-Lab/StarNav.git`

Then navigate to the root directory of the project and install the required dependencies using pip:

`pip3 install -r requirements.txt`

## Usage
To run the program, run `python3 src/main.py`. 
The program allows for user specified parameters, run `python3 src/main.py --help`  for more information about these.
TLE files are required to calculate the satellites's position and velocity. These are automatically downloaded from Celestrak if they are not present in the 'data' directory, or if it is more than 24 hours since the last download. Else it is assumed that the TLE files are up to date.

The program will calculate the precise UTC time when the satellite is closest to the target and generate the quaternion to point the satellite's sensors. These are printed to the console.

## Known Issues
* The program currently only supports the Moon as a target. Support for other targets will be added in the future.
* There is no check to ensure that the target is not obscured by the Earth. This should not happen as it then clearly is not in it's closes point in orbit, but can happen if the tolerance parameter is too low. This check will be added in the future.
* The program is under development, and unknown bugs are to be expected. 

## License
This program is licensed under the Apache-2.0 License. See the `LICENSE` file for more information.