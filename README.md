# pyslackers-website

The website for the PySlackers slack community - a place for python learners, teachers, tinkerers, etc.

## Development

Prereqs:

* `docker`
* `python3.6+`

    docker-compose up -d
    export PY_ENV=development
    ./manage.py migrate
    ./manage.py runserver

View the application at http://localhost:8000.

## Deployment

We maintain a collection of [ansible](https://www.ansible.com/) roles and playbooks to deploy our applications. You can see those at [pyslackers/ansible](https://github.com/pyslackers/ansible).

    ansible-playbook -i ...  # TODO

This will do the full server configuration and deployment, follow the roles for details :).
