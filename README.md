# pyslackers-website

[![Build Status](https://travis-ci.org/pyslackers/website.svg?branch=master)](https://travis-ci.org/pyslackers/website)

The website for the PySlackers slack community - a place for python learners, teachers, tinkerers, etc.

### Development

Please see [CONTRIBUTING.md](/CONTRIBUTING.md).

### Deployment

We use [ansible](https://www.ansible.com/) to deploy our apps and configure servers, which adds a more dependencies:

```bash
# This is intentionally excluded from the requirements.txt, and should
# be done outside a virtualenv (ansible doesn't work properly with virtualenvs)
$ pip3 install ansible
```

To deploy, you need to do a few things:

1. Install the ansible role dependencies
    * `cd ansible && ansible-galaxy install -r requirements.yml`
2. Set the password file:
    * `echo "MY PASSWORD" > ansible/.pass`
3. Run the playbook:
    * `cd ansible && ansible-playbook playbook.yml`
