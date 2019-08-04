# The Easy Path (recommended)

To get started on the easy path, you simply need [`docker`](https://www.docker.com/get-started) and [`docker-compose`](https://docs.docker.com/compose/). By utilizing docker and compose you don't need to think about anything on your host system (python versions, virtual environments, etc). Instead you can run the following and be ready to rock:

```bash
$ docker-compose up --build
```

This will build the docker container for you which uses the correct [python version](.python-version), installs the dependencies, and binds the ports. This also "volume mounts" your local directory into the container, meaning that any changes you make on your host machine will be available in the docker container. The exception to these changes being reflected immediately will be if/when a dependency is added or updated, in which case you'll need to run the above command again (basically just ctrl-c, up arrow, enter, and wait for the rebuild).

## Testing

While you can allow for CircleCI to run tests/checks, running locally simply uses `docker` and `tox`:

```bash
# if you need to rebuild first, `docker-compose build`

$ docker-compose run web tox
```

Tox forwards positional arguments to pytest, that way you can use all standard pytest arguments. For example, only running a specific test can be done like this:

```bash
$ docker-compose run web tox -e py37 tests/test_website.py::test_endpoint_index
```

To run the black auto-formatter on the code you can use:

```bash
$ docker-compose run web tox -e autoformat
```

# The Involved Path

If instead you'd prefer to set-up your project on the host machine, you are free to do so. This is a non-exhaustive primer on the steps required, if you need help directly please ask in [#community_projects](slack://open?team=T07EFKXHR&id=C2FMLUBEU).

## Unix-like Systems (Linux/MacOS)

### 1.Python Version

If you have [`pyenv`](https://github.com/pyenv/pyenv) installed already, the [python version](.python-version) should be set automatically for you based on the `.python-version` file. However if you do not, you should make sure that Python3.7+ is available on your host.

### 2. Virtual Environment

For a host of reasons that are covered elsewhere, you should never install dependencies to your "system python". Instead you should set up a "virtual environment".

```bash
$ python -V
Python 3.7.3
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

### 4. Environment (optional)

If you want to test changes and make sure things work, you can copy the [`.env.sample`](.env.sample) to `.env` and add in the required configuration variables to work. You may want to set up a "dev" slack team for this.

### 5. Runtime Dependencies

You'll need to run the following:

* `redis`
    * You can do this easily with `docker run --rm -it -p 6379:6379 redis:5-alpine`

### 6. Run the App

Now you should be good to run the application:

```bash
(.venv) $ gunicorn --bind 127.0.0.1:8000 --worker-class aiohttp.GunicornWebWorker --reload pyslackersweb:app_factory
```

Once that launches you can visit [localhost:8000](http://localhost:8000) in your browser and be in business.

## Windows Systems

TODO: see [#330](https://github.com/pyslackers/website/issues/330)
