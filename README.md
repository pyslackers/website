# pyslackers-website

[![Build Status](https://travis-ci.org/pyslackers/website.svg?branch=master)](https://travis-ci.org/pyslackers/website)

The website for the PySlackers slack community - a place for python learners, teachers, tinkerers, etc.

## Development

Prereqs:

* docker
* python3.6+

The following external services are required

* PostgreSQL 9.6+
* Redis

How you install these services is up to you, but the easiest way is by using
Docker and Docker compose.

1. Install Docker and Docker Compose by following the instructions on the [Docker website](https://docs.docker.com/compose/install/)

2. Run Docker Compose in detached mode `-d`:

    `docker-compose up -d`

3. If not running the containers in detached mode open a new terminal window.

4. Create a virtualenv. This will create the virtualenv in the project directory.

    `python3 -m venv .venv `

5. Activate the virtualenv.

    `source .venv/bin/activate`

6. Install all the requirements.

    `pip install -r requirements.txt`

7. Run Django migrations.

    `PY_ENV=development ./manage.py migrate`

8. Create a superuser.
    
    `PY_ENV=development ./manage.py createsuperuser`

9. Run the Django devserver.

    `PY_ENV=development ./manage.py devserver`

10. View the application at [http://localhost:8000](http://localhost:8000).

## Local OAuth2 login

* Google OAuth2 client credentials - if you want to log in using a Google account locally
    * http://localhost:8000/admin/socialaccount/socialapp/add/
* Twitter OAuth2 client credentials - if you want to log in using a Twitter account locally
    * http://localhost:8000/admin/socialaccount/socialapp/add/

## Deployment

We maintain a collection of [ansible](https://www.ansible.com/) roles and playbooks to deploy our applications. You can see those at [pyslackers/ansible](https://github.com/pyslackers/ansible).

    ansible-playbook -i ...  # TODO

This will do the full server configuration and deployment, follow the roles for details :).
