# How to contribute

## Development internals

* [Docker](https://www.docker.com/get-started)
* [docker-compose](https://docs.docker.com/compose)
* Python 3.8 or 3.12
* [pipx](https://pypa.github.io/pipx/) - Install Python applications in isolated environments
* [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
* tox (install via `pipx install tox`)

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

### 2. Install uv and Setup Environment

We use `uv` for fast Python package management. It will automatically create a virtual environment and install dependencies.

```bash
# Install uv if you haven't already
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates venv and installs all dependencies)
$ uv sync --group dev
```

This creates a `.venv` directory with all dependencies installed. You can either activate the virtual environment or use `uv run`:

```bash
# Option 1: Activate venv and run commands normally
$ source .venv/bin/activate
(.venv) $ python --version

# Option 2: Use uv run (recommended)
$ uv run python --version
```

### 3. Dependencies

Dependencies are already installed when you run `uv sync`. To add new dependencies:

```bash
# Add a production dependency
$ uv add package-name

# Add a dev dependency to a specific group
$ uv add --group test pytest-new-plugin
```

OR use the make command for initial setup:

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
# Use uv run to execute commands or activate the venv with: source .venv/bin/activate
tox
```

## Windows Systems

TODO: see [#330](https://github.com/pyslackers/website/issues/330)
