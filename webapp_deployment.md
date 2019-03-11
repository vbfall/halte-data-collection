#Deployment instructions

Within your deployment environment, go through the following steps:

1. Install requirements
~~~~
$ python -m pip install -r requirements.txt
~~~~

1. Configure Flask
~~~~
$ export FLASK_APP=application.py
In Windows, use *SET* instead of *EXPLORE*
~~~~

1. Serve
~~~~
$ flask run
~~~~
