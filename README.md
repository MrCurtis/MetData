Met Data
========

A Django app to get and display historical weather data from the Met Office.

Running the app
---------------

The simplest way to get the project up and running is to use
[Vagrant](https://www.vagrantup.com/). Assuming Vagrant and Ansible are
installed, cd in to the repositories root directory and type:

    vagrant up

After a few minutes the process should complete and you should be able to view
the project by typing:

    http://localhost:8000/

into the browser on your host machine.

To setup the project manually:
* Ensure you have sqlite, python3, and pip3 installed on your machine.
* If you like to use virtualenv then create a virtual environment.
* Install the python dependencies by typing:

    pip3 install requirements.txt

from the projects root directory.
* Change in to the project folder (the one that contains manage.py).
* Run the following to set up the database:

    python3 manage.py makemigrations historical_data

    python3 manage.py migrate

* Then run the following command to get the data from the Met Office website
and add it to the database.

    python3 manage.py get_data_from_met_office

* Finally, start the server:

    python3 manage.py runserver 0:8000
