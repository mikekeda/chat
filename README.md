Chat
======================

This is site where you chat with other people.
Link to the site - [https://chat.mkeda.me](https://chat.mkeda.me)

Installation
------------
    # Install Redis
    sudo apt install redis-server
    # Install postgresql
    sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main"
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-9.6
    # Configure database
    sudo su - postgres
    psql
    CREATE USER chat_admin WITH PASSWORD 'home_pass';
    CREATE DATABASE chat;
    GRANT ALL PRIVILEGES ON DATABASE chat to chat_admin;
    # Install packages
    pip install -r requirements.txt
    # Apply migrations
    python manage.py migrate
    # Create an admin user
    python manage.py createsuperuser

Running
-------
    # Locally
    python manage.py runserver

Upgrade python packages
-------
    # Remove versions from requirements.txt
    # Upgrade python packages
    pip install --upgrade --force-reinstall -r requirements.txt
    # Update requirements.txt
    pip freeze > requirements.txt

Useful manage.py commands
-------
    # Run tests
    python manage.py test
    # Run tests and check code style and coverage
    python manage.py jenkins --enable-coverage --pep8-exclude migrations --pylint-rcfile .pylintrc
    # Train Chatterbot
    python manage.py train
