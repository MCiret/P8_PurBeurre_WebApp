=====================
"Pur Beurre" project
=====================
**Searching for food substitution in Open Food Facts french database**

|Status badge| |UIlanguage badge| |vPython badge| |vBootstrap badge|

*****************
TABLE OF CONTENTS
*****************

1. `DESCRIPTION`_
    * `Summary`_
    * `Features`_

2. `INSTALLATION`_
    * `Application`_
    * `Database`_
    * `Required libraries`_

3. `OPEN FOOD FACTS API USAGE`_

DESCRIPTION
===========

Summary
-------
This Web application asks user for researching a food product to obtain more healthy alternatives based on nutriscore value.
The user could log in to bookmark a food product.

Food products are weekly collected from Open Food Facts (OFF) french database (requested via the OFF search API).
The API request response is a json data then parsed, reorganized and inserted in a database.

*NB: this source code is for french User Interface.*

Features
--------

1) User (logged or not (see below)) researches a food product in order to obtain an healthy substitute food.

    1.1) User could use research field (present in all pages header and in home page) to enter keywords and display the result page.

        - If only 1 food product matches the research keywords then substitutes foods are displayed.
        - Else if many food products match the research keywords then they are listed to be chosen by user and then substitutes foods are displayed.

    1.2) Click on substitute food picture to display the details page and its Open Food Facts url.

2) User (unlogged) creates or logs in.

    2.1) Unlogged user could click on the person-plus or carot icon to access the account creation page.

        - If the account is created, user is redicted to home page.
        - Else if the account is not created (email already exists or wrong password) the page is redisplayed and a message informs user of the reason why.

    2.2) Unlogged user on account creation page (see 2.1) could use the lnik "Cliquez ici pour vous connecter..." to access the account login page.

        - If the user is logged, he is redicted to home page.
        - Else if the user is not logged (wrong email or password) the page is redisplayed and a message informs user of the problem.

3) User (logged) bookmarks a substitute food product.

    3.1) Logged user could see and use the "Sauvegarder" button below the substitute food product picture to save and get back faster later.

        - If the user had already bookmarked a substitute food product, the text "Sauvegardé 🗹" is displayed below the picture.

    3.1) Logged user could click on carot icon (header menu) to diplay all his bookmarked food products.


INSTALLATION
============

Application
-----------

1) Download the project : use the "Code" (green button) and unzip the P8_PurBeurre_WebApp.zip file.
2) Python3 comes with Python Package Manager (pip) else you have to install it (https://pip.pypa.io/en/stable/installing/)

3) Set up a virtual environment :

    NB: the symbol $ flags the commands prompt

    * UNIX operating system :
        3.1) Install the Python module : $ pip install venv

        3.2) Navigate to the project main directory using command prompt : $ cd .....

        3.3) Create a virtual environment : $ python -m venv name_of_your_virtual_env

        3.4) Activate the virtual environment : $ source name_of_your_virtual_env/bin/activate


    * DOS operating system :
        3.1) Install the Python module : $ pip install venv

        3.2) Navigate to the project main directory using command prompt : $ cd .....

        3.3) Create a virtual environment : $ py -m venv name_of_your_virtual_env

        3.4) Activate the virtual environment : $ .\name_of_your_virtual_env\Scripts\activate


4) Install required libraries : see the Required libraries section below.

5) Environment variables to be set/adapted :

    * project_config/settings.py :

        - variable SECRET_KEY (key to securing signed data) set with DJANGO_KEY enviro. variable name
        - variable DATABASES['default']['PASSWORD'] set with POSTGRE_PWD enviro. variable name

6) Install and fill the database (see db_settingup_ below).

7) Run the code source main.py file : (UNIX) $ python manage.py runserver (DOS) $ py manapge.py runserver

8) Follow the http:// link given by Django starting message on the terminal output (usually http://127.0.0.1:8000/) to display interface in your browser.

Database
--------

.. _db_settingup:

1) Install your favorite SGDB.
2) Set up projetc_config/settings.py --> variable DATABASES with your database connection parameters (see comments above the variable declaration for Django documentation link).
3) Run personalised Django command to request Open Food Facts API and insert food products (and categories) in database : (UNIX) $ python manage.py filldb (DOS) $ py manage.py filldb

.. note:: you can modify which data are requested from Open Food Facts API.


Required libraries
------------------

Python libraries to install in your virtual environment : $ pip install -r requirements.txt

OPEN FOOD FACTS API USAGE
=========================

See research/management/commands/filldb.py

The build_get_request() static method (called by handle() method) shows you the used request.
https://documenter.getpostman.com/view/8470508/SVtN3Wzy#58efae40-73c3-4907-9a88-785faff6ffb1

.. warning:: if you modify the fields parameter then you will have to adapt the front-end part of the application.


Nevertheless, there is no problem if you would like to modify categories, page_size (number of product per page) and/or page (number of page per request).
The categories tags and page_nb are gotten from research/management/off_research_params.json. This file is modified (rewritten) each time the filldb command is used, to "feed" the database, the page_nb parameter is incremented.

.. note:: categories tags have to exists in OFF. They are not case sensitive but you have to use underscore te replace whitespace characters.


.. |vPython badge| image:: https://img.shields.io/badge/Python-3.9-blue.svg
.. |vBootstrap badge| image:: https://img.shields.io/badge/Bootstrap-5-purple.svg

.. |Status badge| image:: https://img.shields.io/badge/Status-Development-orange.svg
.. |UIlanguage badge| image:: https://img.shields.io/badge/UI-French-9cf.svg
