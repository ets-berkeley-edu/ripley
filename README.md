# Ripley

Ripley heroically supports UC Berkeley's Canvas LMS instance.

![Ripley, a character from the movie Alien, is holding a cat.](src/assets/images/ripley-with-cat.png)

## Installation

* Install Python 3
* Create your virtual environment (venv)
* Install dependencies

```
pip3 install -r requirements.txt [--upgrade]
```

### Front-end dependencies

```
nvm use
npm install
```

### Configuration

If you plan to use any resources outside localhost, put your configurations in a separately encrypted area:

```
mkdir /Volumes/XYZ/ripley_config
export RIPLEY_LOCAL_CONFIGS=/Volumes/XYZ/ripley_config
```

## Database

### Create Postgres user and databases

![Photo of computer room of the movie Alien.](src/assets/images/muthur.png)

```
createuser ripley --no-createdb --no-superuser --no-createrole --pwprompt
createdb nostromo --owner=ripley
createdb nostromo_test --owner=ripley
createdb ripley_loch_test --owner=ripley

# Load schema
export FLASK_APP=application.py
flask initdb
```

## Redis

### Local Redis Server installation (optional)

#### Install and start Redis server

```
brew install redis

# Start server
redis-server
```

#### Configure Ripley to talk to local Redis

```
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_USE_FAKE_CLIENT = False
```

## Jobs

Listen on the queue for jobs, with Redis.

![Close-up image of the Xenomorph from the movie Alien.](src/assets/images/xenomorph.png)

On macOS 10.13 and later, disable the fork() crash behavior (see https://github.com/rq/rq/issues/1418):

```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

Start the worker:

```
.platform/hooks/postdeploy/02_start_rq_worker.sh
```

## Run tests, lint the code

We use [Tox](https://tox.readthedocs.io) for continuous integration. Under the hood, you'll find [PyTest](https://docs.pytest.org), [Flake8](http://flake8.pycqa.org) and [ESLint](https://eslint.org/). Please install NPM dependencies (see above) before running tests.

```
# Run tests and linters in parallel:
tox -p

# Pytest
tox -e test

# Run specific test(s)
tox -e test -- tests/test_models/test_foo.py
tox -e test -- tests/test_externals/

# Linters, à la carte
tox -e lint-py
tox -e lint-vue

# Auto-fix linting errors in Vue code
tox -e lint-vue-fix

# Lint specific file(s)
tox -e lint-py -- scripts/foo.py
```
