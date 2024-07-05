# airbnb-regulation

## Description

Illegal Airbnb listings are contributing to housing shortage in BC. This project aims to flag Airbnb listings that violates BC short-term rental policy.

More information can be found in [Home wiki](https://github.com/CodeForBc/airbnb-regulation/wiki).

## Architecture
Check out [Architecture wiki](https://github.com/CodeForBc/airbnb-regulation/wiki/Architecture)

## Modules
This project is set up in 2 modules: data ingestion and listing processing. The results/views are displayed on Grafana dashboard.

- [Data ingestion module](https://github.com/CodeForBc/airbnb-regulation/wiki/Data-Ingestion-Module): To ensure Airbnb compliance with local rules and regulations, data scraping is necessary to verify if each listing meets the required standards.
- [Listing processing module](https://github.com/CodeForBc/airbnb-regulation/wiki/Listing-processing-module): To determine illegal rental listings on Airbnb, it is important to make sure business registry for each listing is validated. A system composed of policies and rules needs to be set up to effectively handle a large number of listings.
- [Grafana dashboard](https://github.com/CodeForBc/airbnb-regulation/wiki/Grafana-dashboard)

## Package Management

This package uses [Poetry](https://python-poetry.org/) to manage dependencies and
isolated [Python virtual environments](https://docs.python.org/3/library/venv.html).

To proceed,
[install Poetry globally](https://python-poetry.org/docs/#installation)
onto your system.

Please note that **Python 3.8+** is required to install Poetry per [System requirement](https://python-poetry.org/docs/#system-requirements).

### Dependencies

Dependencies are defined in [`pyproject.toml`](./pyproject.toml) and specific versions are locked
into [`poetry.lock`](./poetry.lock). This allows for exact reproducible environments across
all machines that use the project, both during development and in production.

To make sure virtual env is created in project's root directory
```bash
$ poetry config virtualenvs.in-project true
```

To confirm the config has been changed, it can be checked with 
```bash
$ poetry config --list
```

> Please note if a virtual environment has already been created under `{cache-dir}/virtualenvs`, setting this to `true` will not cause poetry to create or use a local virtual environment.
> 
> To remove an existed env, list the env and remove it with
> ```bash
> $ poetry env list --full-path // see list of env-paths
> $ poetry env remove env-path
> ```

To install all dependencies into an isolated virtual environment:

> Append `--sync` to uninstall dependencies that are no longer in use from the virtual environment.

```bash
$ poetry install
```

To [activate](https://python-poetry.org/docs/basic-usage#activating-the-virtual-environment) the
virtual environment that is automatically created by Poetry:

```bash
$ poetry shell
```

To deactivate the environment:

```bash
$ exit
```

To upgrade all dependencies to their latest versions:

```bash
$ poetry update
```

To add dependency:

```bash
$ poetry add <dependency_name>
```

To add development dependency:
```bash
$ poetry add -G dev <dependency_name>
```

## References

[Poetry Configuration](https://python-poetry.org/docs/configuration/)

[Poetry Managing environments](https://python-poetry.org/docs/managing-environments/)