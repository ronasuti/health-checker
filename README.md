# Roman's Fetch Health Checker

This runs on Python, using async to efficiently send out many requests
and print out availability metrics.

# Installation Instructions

Once you've cloned this repository:

1. Make sure Python is installed, preferably 3.12 or later
2. Make sure you have pip available on your system
3. Run `python3 -m venv venv` to create a virtual environment
4. Run `pip install -r requirements.txt` to install packages
5. Run `python3 health_check.py <yaml config file>` to run the program
