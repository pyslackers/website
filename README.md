# pyslackers-website

[![Build Status](https://travis-ci.org/pyslackers/website.svg?branch=master)](https://travis-ci.org/pyslackers/website)

The website for the PySlackers slack community - a place for python learners, teachers, tinkerers, etc.

### Development

Please see [CONTRIBUTING.md](/CONTRIBUTING.md).

### Testing

```bash
$ pytest --cov=.
```

### Deployment
=======

To deploy, you need to do a few things:

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

1. Install the ansible role dependencies
    * `cd ansible && ansible-galaxy install -r requirements.yml`
2. Set the password file:
    * `echo "MY PASSWORD" > ansible/.pass`
3. Run the playbook (omit the tags if you need to provision a server):
    * `cd ansible && ansible-playbook playbook.yml --tags "deploy"`

This will do the full server configuration and deployment, follow the roles for details :).

## Running full stack in Docker

The full stack can be run with the following command:

```
docker-compose -f docker-compose-fullstack.yml build
docker-compose -f docker-compose-fullstack.yml up
```
