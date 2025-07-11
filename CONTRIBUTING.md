# How to contribute

## Development internals

* [Docker](https://www.docker.com/get-started)
* [docker-compose](https://docs.docker.com/compose)
* Python 3.8 or 3.12
* tox

##  Quickstart

To get the application running quickly the entire stack can be started by running the following:

```bash
$ docker-compose up --build
```

By utilizing docker and compose you don't need to think about anything on your host system (python versions, virtual environments, etc). This will build the docker container for you which uses the correct [python version](.python-version), installs the dependencies, and binds the ports. This also "volume mounts" your local directory into the container, meaning that any changes you make on your host machine will be available in the docker container. The exception to these changes being reflected immediately will be if/when a dependency is added or updated, in which case you'll need to run the above command again (basically just ctrl-c, up arrow, enter, and wait for the rebuild).

### Testing with all services running w/ docker compose

While you can allow for CircleCI to run tests/checks, running locally simply uses `docker` and `tox`:

```bash
# if you need to rebuild first, `docker-compose build`

$ docker-compose run --rm web tox -e test
```

Tox forwards positional arguments to pytest, that way you can use all standard pytest arguments. For example, only running a specific test can be done like this:

```bash
$ docker-compose run --rm web tox -e test tests/test_website.py::test_endpoint_index
```

To run the black auto-formatter on the code you can use:

```bash
$ docker-compose run --rm web tox -e autoformat
```

## Running the application locally

If instead you'd prefer to set-up your project on the host machine, you are free to do so. This is a non-exhaustive primer on the steps required, if you need help directly please ask in [#community_projects](slack://open?team=T07EFKXHR&id=C2FMLUBEU).

## Unix-like Systems (Linux/MacOS)

### 1. Python Version

If you have [`pyenv`](https://github.com/pyenv/pyenv) installed already, the [python version](.python-version) should be set automatically for you based on the `.python-version` file. However if you do not, you should make sure that Python 3.8 or 3.12 is available on your host.

### 2. Virtual Environment

For a host of reasons that are covered elsewhere, you should never install dependencies to your "system python". Instead you should set up a "virtual environment".

```bash
$ python -V
Python 3.8.16  # or Python 3.12.x
$ python -m venv .venv
```

You will now have a directory in your project called `.venv`, which is ignored by source control as it is not portable. You need to activate this _per shell instance_.

```bash
$ source .venv/bin/activate
```

Now your shell should have the virtual environment's name prepended:

```bash
(.venv) $
```

You can check that the python and pip paths are as expected, the `.venv` directory in your current working directory:

```bash
(.venv) $ which python
${PWD}/.venv/bin/python
(.venv) $ which pip
${PWD}/.venv/bin/pip
```

### 3. Dependencies

Now you need the dependencies installed, which is as simple as:

```bash
(.venv) $ pip install -r requirements/development.txt
```

OR run the above steps with the following make command:

```bash
$ make install
```

### 4. Environment (optional)

If you want to test changes and make sure things work, you can copy the [`.env.sample`](.env.sample) to `.env` and add in the required configuration variables to work. You may want to set up a "dev" slack team for this.

### 5. Run the services

You'll need to run the following:

```bash
make setup_services
```

### 6. Run the App

Now you should be good to run the application:

```bash
make start_app
```
Once that launches you can visit [localhost:8000](http://localhost:8000) in your browser and be in business.

### 7. Run tests locally

To run the tests with automatic setup and teardown of services simply run:

```bash
# Ensure the virtualenv is activated i.e source .venv/bin/activate
tox
```

## Windows Systems

TODO: see [#330](https://github.com/pyslackers/website/issues/330)
