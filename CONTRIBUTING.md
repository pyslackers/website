This guide is opinionated and we recommend following this directly, however you may choose to run the dependencies another way if you desire - but we don't support it officially.

## Prereqs

These must be installed before proceeding:

* `docker`
    * Follow the instructions on the [Docker website](https://docs.docker.com/compose/install/)
* `docker-compose`
    * Follow the instructions on the [Docker website](https://docs.docker.com/compose/install/)
* `python3.6+`
    * Mac: `brew install python3`
    * Windows: https://www.python.org/downloads/windows/
    * Linux: You probably know what's up

## Run the things

1. Create a virtualenv (you only need to do this once)
    * `python3 -m venv .venv`
2. Activate your virtualenv (you need to do this for every shell)
    * `source .venv/bin/activate`
3. Install the application requirements:
    * `pip install -r requirements.txt`
4. Startup the runtime dependencies, in detached mode (so they run in the background):
    * `docker-compose up -d`
    * You can stop these later with `docker-compose stop`
5. Run the Django migrations
    * `PY_ENV=development ./manage.py migrate`
6. Create an admin (super) user, following the prompts
    * `PY_ENV=development ./manage.py createsuperuser`
7. Run the devserver (this will start the background workers too)
    * `PY_ENV=development ./manage.py devserver`
8. View the application at [http://localhost:8000](http://localhost:8000)

### Local OAuth2 Login

We support direct login/account setup along with OAuth2 login with Google and Twitter. These require a bit of extra setup if you'd like to use them locally.

First you need to log into their respective consoles and register a new app:

* Google: https://console.developers.google.com/apis/dashboard
    * Redirect URL: http://localhost:8000/accounts/login/google/callback/
* Twitter: https://apps.twitter.com/app/new
    * Redirect URL: http://localhost:8000/accounts/login/twitter/callback/

Take note of the `client_id` and `client_secret` for each, and register them with the management command:

```bash
PY_ENV=development ./manage.py createoauth2app --client-id $CLIENT_ID --client-secret $CLIENT_SECRET --provider {google,twitter}
``` 



