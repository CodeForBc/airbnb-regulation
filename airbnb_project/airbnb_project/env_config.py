import os
from dotenv import load_dotenv, find_dotenv

from .exceptions import EnvConfigException

# Load environment variables from a .env file
load_dotenv(find_dotenv())


def get_env_variable(var_name: str) -> str:
    """Get the environment variable or raise an error.

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the environment variable.

    Raises:
        ConfigError: If the environment variable is missing or empty.
    """
    try:
        value = os.environ[var_name]
        if not value:  # Check if the value is empty
            raise EnvConfigException(f"Missing required environment variable: {var_name}")
    except KeyError:
        raise EnvConfigException(f"Missing required environment variable: {var_name}")

    return value  # Return the value if it exists


# Define a dictionary to hold your environment variables
ENV_VARIABLES: dict[str, str] = {
    'POSTGRES_URL':get_env_variable('POSTGRES_URL'),
    'POSTGRES_DB': get_env_variable('POSTGRES_DB'),
    'POSTGRES_USER': get_env_variable('POSTGRES_USER'),
    'POSTGRES_PASSWORD': get_env_variable('POSTGRES_PASSWORD'),
    'POSTGRES_HOST_PORT': get_env_variable('POSTGRES_HOST_PORT'),
    'DJANGO_DEBUG': get_env_variable('DJANGO_DEBUG'),
    'SECRET_KEY': get_env_variable('SECRET_KEY')
}
