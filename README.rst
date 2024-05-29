=====================
"Pur Beurre" project
=====================
**Searching for food substitution in Open Food Facts french database**

|Status badge| |UIlanguage badge| |vPython badge| |vBootstrap badge| |OCDAPY badge|


🔗 https://pur-beurre.p8.mc-dapy.fr/

*****************
TABLE OF CONTENTS
*****************

1. `DESCRIPTION`_
    * `Learning goals`_
    * `Summary`_
    * `Features`_

2. `INSTALLATION`_
    * `Application`_
    * `Database`_

3. `OPEN FOOD FACTS API`_

DESCRIPTION
===========

Learning goals
--------------
This Web app has been developed during OpenClassrooms training course "Python Application Development".

* 1st Django Web application
* Specifications for features and interface (style guide, pages prototypes and the Bootstrap theme)
* Tests : using unittest (including 1 functionnal (Selenium) test) with TDD approach
* Database modeling
* Get data from OpenFoodFacts API, populate database and use it for searching..
* User authentication, acocunt and "bookmarking" features

Summary
-------
User could search for a food product to obtain more healthy alternatives based on nutriscore value.
User could log in to bookmark its favourites food products.

Food products are collected from Open Food Facts (OFF) french database (requested via the OFF search API).

*NB: this source code is for french User Interface.*

Features
--------

1) User (logged or not (see below)) searches a food product in order to obtain an healthy substitute food.

    1.1) User could use search field (present in all pages header and in home page) to enter keywords and display the result page.

        - If only 1 food product matches the search keywords then substitutes foods are displayed.
        - Else if many food products match the search keywords then they are listed to be chosen by user and then substitutes foods are displayed.

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

    3.1) ``$ pip install pipx`` then ``$ pipx install pipenv``

    3.2) Create a virtual environment and Install project requirements (Pipfile) : ``$ pipenv install``

    3.3) Activate the virtual environment : ``$ pipenv shell``


4) Environment variables to be set/adapted :

    * project_config/settings.py :

        - DJANGO_SECRET_KEY_P8 used to set the SECRET_KEY Django variable (key to secure signed data)
        - Database connection (see 5. below) :
            - DB_NAME
            - DB_USER
            - DB_PWD
            - DB_HOST
            - DB_PORT

5) Install and fill the database (see db_settingup_ below).

6) Run the code source main.py file :

    - (UNIX) ``$ python manage.py runserver``
    - (DOS) ``$ py manapge.py runserver``

7) Follow the http:// link given by Django starting message on the terminal output (usually http://127.0.0.1:8000/) to display interface in your browser.

Database
--------

.. _db_settingup:

1) Install your favorite SGDB + Create an empty database
2) Set up Django project : the DATABASES variable (project_config/settings.py)
3) Database migration (i.e tables creation) :

    - (UNIX) ``$ python manage.py migrate``
    - (DOS) ``$ py manage.py migrate``

4) Fill db : run personalised Django command to request Open Food Facts API and insert food products (and categories) in database :

    - (UNIX) ``$ python manage.py filldb``
    - (DOS) ``$ py manage.py filldb``


|db_model_img|

OPEN FOOD FACTS API
===================

**GET query** see research/management/commands/filldb.py --> build_get_request() static method (called by handle() method)

**Warning** if you modify the fields parameter then you will have to adapt the front-end part of the application.

**PARAMS values** see research/management/off_research_params.json

*ℹ️ : each time filldb command is runned, the page_nb parameter is incremented ==> to get new food products with next run..*


.. |vPython badge| image:: https://img.shields.io/badge/Python-3.11-blue.svg
.. |vDjango badge| image:: https://img.shields.io/badge/Django-3.11-0c4b33.svg
.. |vDB badge| image:: https://img.shields.io/badge/DB-PostgreSQL-336791.svg
.. |vBootstrap badge| image:: https://img.shields.io/badge/Bootstrap-5-purple.svg


.. |Status badge| image:: https://img.shields.io/badge/Status-Production-green.svg
.. |UIlanguage badge| image:: https://img.shields.io/badge/UI-French-aeb6bf.svg

.. |OCDAPY badge| image:: https://img.shields.io/badge/Learning_Project-OpenClassrooms-e74c3c.svg

.. |db_model_img| image:: p8_purbeurre_db.png
