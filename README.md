# website

## Usage

### Development

The easiest way to get up and running to contribute is with [`docker`](https://www.docker.com/get-started) and [`docker-compose`](https://docs.docker.com/compose/):

```bash
$ docker-compose up --build
```

Now go to [localhost:8000](http://localhost:8000) and you should see the site.

This setup utilizes volumes to mount your local copy of the repository into the running container, so all changes (aside from dependency changes) will be reflected when you simply refresh the page.

If you want to actually test the slack integration(s), you will need to create a `.env` file with the creds. For the required variable names - see [`.env.sample`](.env.sample)
