# FARTS
Floor-Area Ratio Transfer System (FARTS) is a student project for PDX Code Guild. The system allows property owners of sites with excess development rights (sending sites) to transfer unused FAR to other sites (receiving sites).

FARTS is currently only available in Portland.

## Installation requirements
A PortlandMaps server-side API is required to use this platform. You can obtain one from [PortlandMaps.com](https://www.portlandmaps.com/development/). Once obtained, you must keep your key secret by setting an environment variable. Development of this project used [`python-dotenv`](https://github.com/theskumar/python-dotenv).

The platform is built on django web framework. To run the build, enter the repo directory and run the commands below:
pipenv shell
./manage.py makemigrations
./manage.py migrate
./manage.py runserver
