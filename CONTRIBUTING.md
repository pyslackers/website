# Developing

This guide is opinionated and we recommend following this directly, however you may choose to run the dependencies another way if you desire - but we don't support it officially.

## Prereqs

These must be installed before proceeding:

* `docker` and `docker-compose`
    * Follow the instructions on the [Docker website](https://docs.docker.com/compose/install/)
* `python3.6+`
    * Mac: `brew install python3`
    * Windows: [python.org](https://www.python.org/downloads/windows/)
    * Linux: You probably know what's up
* `virtualenv`
    * `$ pip3 install virtualenv`
* `node` and `yarn`

## Run the things

1. Create a virtualenv (you only need to do this once)
    * `$ python3 -m venv .venv`
2. Activate your virtualenv (you need to do this for every shell instance)
    * `$ source .venv/bin/activate`
3. Install the application requirements (do this each time they change)
    * `(.venv) $ pip install -r requirements.txt` - python dependencies
    * `(.venv) $ yarn install` - client side dependencies
4. Startup the runtime dependencies, in detached mode (so they run in the background)
    * `(.venv) $ docker-compose up -d` (they can be stopped later with `docker-compose stop`)
5. Run the database migrations
    * `(.venv) $ ./manage.py migrate`
6. Create an admin (super) user, following the prompts
    * `(.venv) $ ./manage.py createsuperuser`
7. Run the processes for the server and asset compilation (this will run background jobs in-line)
    * `(.venv) $ honcho start -f Procfile.dev`
8. View the application at [http://localhost:8000](http://localhost:8000)

_Note: Scheduled background jobs will not run with this setup, if you need to populate the cache you can run them manually_

Example (edit for your target task):

```bash
(.venv) $ ./manage.py shell
Python 3.6.3 (default, Jul 17 2017, 16:44:45)
(InteractiveConsole) 
>>> from pyslackers_website.slack.tasks import capture_snapshot_of_user_count
>>> capture_snapshot_of_user_count()
```

# Testing

You need to follow the [above](#developing), and then run:

```bash
(.venv) $ pytest
```
