# Contributing new Actors

## Table of Contents
- [leapp-supplements](#contributing-new-actors)
  - [Table of Contents](#table-of-contents)
  - [Actor list](#before-starting)
  - [Testing your actor](#testing-your-actor)
    - [Writing tests](#writing-tests)
    - [Running the tests locally](#running-the-tests-locally)
    - [Running the tests inside a container](#running-the-tests-inside-a-container)
      - [Prerequisites](#prerequisites)
      - [Running the containerized tests](#running-the-containerized-tests)
      - [Entering the containerized environment](#entering-the-containerized-environment)


## Before starting

Familiarize yourself with the [Leapp project documentation](https://leapp.readthedocs.io/en/latest/).
The section [Creating your first actor](https://leapp.readthedocs.io/en/latest/first-actor.html) is a good place to start.
You should also dig around the [Leapp Dashboard](https://oamg.github.io/leapp-dashboard/#/)
to make sure the custom actor functionality you are considering doesn't already exist in the mainstream framework.

## Testing your actor

### Writing tests

Make sure to write tests for your actors as explained in [Tests for Actors](https://leapp.readthedocs.io/en/latest/test-actors.html)

### Running the tests locally
To run the tests locally, use the simple make targets such as `lint`, `pytest` and `test`:
```bash
make test
```

### Running the tests inside a container

#### Prerequisites
In order to run the containerized environment you will need to install [strato-skipper](https://github.com/Stratoscale/skipper)
```bash
pip install strato-skipper
```

#### Running the containerized tests
The [Makefile](./Makefile) includes targets for running the tests inside the container. Each simple target has equivilant targets with a suffix of the environment, such as `test-rhel8` or `lint-rhel7`:
```bash
make test-rhel8
```

Alternatively, you can use skipper directly by setting the `SKIPPER_CONF` environment variable.
For example:
```
SKIPPER_CONF=${PWD}/skipper-rhel8.yaml skipper make test
```

#### Entering the containerized environment
The [Makefile](./Makefile) includes targets for entering specific environment. For example:
```
make shell-rhel8
```
