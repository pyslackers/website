# pyslackers-website

The website for the PySlackers slack community - a place for python learners, teachers, tinkerers, etc.

## Development

Prereqs:

* `docker`
* `python3.6+`
* Google OAuth2 client credentials - if you want to log in using a Google account locally
    * http://localhost:8000/admin/socialaccount/socialapp/add/
* Twitter OAuth2 client credentials - if you want to log in using a Twitter account locally
    * http://localhost:8000/admin/socialaccount/socialapp/add/

    docker-compose up -d
    export PY_ENV=development
    ./manage.py migrate
    
    \# Note: reload works for the website, but not celery worker. If you are testing a celery worker, you will need to Ctrl-C and restart.
    ./manage.py devserver

View the application at [http://localhost:8000](http://localhost:8000).

## Deployment

We maintain a collection of [ansible](https://www.ansible.com/) roles and playbooks to deploy our applications. You can see those at [pyslackers/ansible](https://github.com/pyslackers/ansible).

    ansible-playbook -i ...  # TODO

This will do the full server configuration and deployment, follow the roles for details :).
