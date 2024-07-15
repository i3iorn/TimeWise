"""
Original source found at jdhalbert/bitwarden_secrets_manager_python
"""

import time
import os
import json
import logging
import subprocess
from threading import Lock
from pathlib import Path
from copy import deepcopy

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class BWS:
    """
    A Python wrapper for managing secrets with Bitwarden CLI (bws).

    This class provides methods to interact with the Bitwarden Secrets Manager, allowing for
    secret retrieval, addition, update, and deletion, with caching capabilities.
    """

    def __init__(
            self,
            project_name: str = None,
            bws_access_token: str = None,
            bws_path: str = "bws"
    ):
        """
        Initializes the BWS class with project details and configurations.

        Args:
            project_name (str): The name of the project to manage secrets for.
            bws_access_token (str, optional): Access token for Bitwarden. Defaults to None.
            bws_path (str, optional): Path to the Bitwarden CLI executable. Defaults to 'bws'.
        """
        self.project_name = project_name or os.getenv('BWS_PROJECT_NAME')
        self.bws_application_path = Path(bws_path or os.getenv('BWS_APPLICATION_PATH', 'bws'))
        self.access_token = self._set_access_token(bws_access_token or os.getenv('BWS_ACCESS_TOKEN'))
        self.project_id = self._fetch_project_id()
        self.secrets_cache = {}
        self.last_cache_refresh = 0
        self.cache_duration = int(os.getenv('BWS_CACHE_DURATION', 300))
        self._lock = Lock()
        self._last_cache_refresh = time.time()
        self.refresh_secrets_cache()

        logger.info(f"Initialized BWS with project: {self.project_name}")

    def __getitem__(self, key: str) -> str:
        """When accessing the BWS object like a dictionary, only the 'value' field for the given key is returned.

        Args:
            key (str): Secret name.

        Returns:
            str: Secret 'value' field.
        """
        if not self._validate_secret_key(key):
            raise KeyError(f"Invalid key: {key}")

        if self._is_secret_stale(key):
            logger.info(f"Refreshing secrets cache at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            self.refresh_secrets_cache()

        return self.get_secret(key=key, value_only=True)

    def __setitem__(self, key: str, value: str) -> None:
        """Adds or updates the provided key/value pair.

        Args:
            key (str): Secret name.
            value (str): Secret value.
        """
        if key in self:
            self.update_secret_value(key=key, value=value)
        else:
            self.add_secret(key=key, value=value)

    def __len__(self) -> int:
        return len(self._secrets)

    def __contains__(self, key) -> bool:
        return key in self._secrets

    def __delitem__(self, key) -> None:
        self.delete_secret(key=key)

    def __enter__(self):
        # Acquire resources or lock
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release resources or lock
        self._lock.release()
        # Handle exceptions if necessary
        if exc_type:
            logger.error(f"Exception occurred: {exc_val}")
            return False  # Propagate exception
        return True

    @staticmethod
    def _set_access_token(bws_access_token: str | None) -> str:
        """
        Sets the access token for Bitwarden CLI.

        Args:
            bws_access_token (str | None): The access token to use.

        Returns:
            str: The access token.

        Raises:
            ValueError: If no access token is provided or found in environment variables.
        """
        if bws_access_token:
            return bws_access_token
        elif "BWS_ACCESS_TOKEN" in os.environ:
            logger.info("Using BWS_ACCESS_TOKEN from environment variable.")
            return os.environ["BWS_ACCESS_TOKEN"]
        else:
            raise ValueError("No BWS_ACCESS_TOKEN provided or set as environment variable.")

    def _fetch_project_id(self) -> str:
        """
        Retrieves the project ID based on the project name.

        Returns:
            str: The project ID.

        Raises:
            ValueError: If the project name is not found.
        """
        projects = self._call_bws_and_return(["project", "list"], as_json=True)

        for project in projects:
            logger.debug(f"Found project: {project}")
            if project["name"] == self.project_name:
                return project["id"]
        raise ValueError(f'Project "{self.project_name}" not found.')

    def _call_bws_and_return(self, cl_args: list[str], as_json: bool = True) -> str | dict | list:
        """
        Executes a Bitwarden CLI command and returns the output.

        Args:
            cl_args (list[str]): The CLI arguments to pass to Bitwarden CLI.
            as_json (bool, optional): Whether to parse the output as JSON. Defaults to True.

        Returns:
            str | dict | list: The output from the Bitwarden CLI command.
        """
        try:
            logger.debug(f"Calling Bitwarden CLI with args: {cl_args}")
            output = subprocess.check_output(
                [self.bws_application_path] + cl_args + ["-c", "no", "-t", self.access_token],
                text=True,
                stderr=subprocess.STDOUT,
            )
            logger.debug(f"Bitwarden CLI call succeeded: {output}")
            return json.loads(output) if as_json else output
        except subprocess.CalledProcessError as error:
            logger.critical(f"Bitwarden CLI call failed: {error.output}, command: {error.cmd}")
            raise RuntimeError(f"Command execution failed: {error.cmd}, output: {error.output}")

    @staticmethod
    def _handle_subprocess_error(error):
        """Enhanced error reporting for subprocess errors."""
        logger.critical(f"Subprocess call failed with error: {error.output}, command: {error.cmd}")
        raise RuntimeError(f"Command execution failed: {error.cmd}, output: {error.output}")

    def _make_call(self, cl_args: list[str], print_to_console: bool = False) -> str:
        """Make a call to `bws` with the provided args. Usually use self.call_and_return_text() instead of this.

        Args:
            cl_args (list[str]): Args in list format (e.g. ['project', 'list'])
            print_to_console (bool, optional): Call print() on the stdout results. Defaults to False.

        Returns:
            str: Call results.
        """
        try:
            output = subprocess.check_output(
                [self.bws_application_path] + cl_args + ["-c", "no", "-t", self.access_token],
                text=True,
                stderr=subprocess.STDOUT,
            )
            if print_to_console:
                print(output)
            return output
        except subprocess.CalledProcessError as cpe:
            self._handle_subprocess_error(cpe)

    def _get_secrets_from_bws(self) -> dict[str, dict[str, str]]:
        """Get list of all secrets from `bws` CLI.

        Returns:
            dict[str, dict[str, str]: Secert objects keyed by secret key name. E.g.:
            {'secret_1':
                {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'organizationId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'projectId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'key': 'secret_1',
                'value': 'secret_1_value',
                'note': '',
                'creationDate': '2001-01-01T01:23:45.678901234Z',
                'revisionDate': '2001-01-01T01:23:45.678901234Z'},
            ...
            }
        """
        secrets = self.call_and_return_text(cl_args=["secret", "list", self.project_id], as_json=True)
        secrets_keyed_by_key = {secret["key"]: secret for secret in secrets}
        if len(secrets_keyed_by_key) != len(secrets):
            raise ValueError(
                "Projects with multiple keys with the same name are not supported. Each key name in your "
                "project must be unique."
            )
        return secrets_keyed_by_key

    def _is_secret_stale(self, key: str) -> bool:
        """Check if a secret is stale and needs to be refreshed."""
        secret_last_updated = self._secrets[key].get('revisionDate')
        if not secret_last_updated:
            return True
        return (time.time() - time.strptime(secret_last_updated)) > self.cache_duration

    @staticmethod
    def _validate_secret_key(key: str) -> bool:
        """Enhanced validation for secret keys."""
        return isinstance(key, str) and key.isalnum() and 1 <= len(key) <= 40

    def _attempt_cache_refresh(self, force_refresh: bool) -> None:
        try:
            self._secrets = self._get_secrets_from_bws()
            self._last_cache_refresh = time.time()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to refresh secrets cache due to subprocess error: {e}")
            if force_refresh or not self._secrets:
                raise
        except ValueError as e:
            logger.error(f"Failed to refresh secrets cache due to value error: {e}")
            if force_refresh or not self._secrets:
                raise

    def refresh_secrets_cache(self, force_refresh=False) -> None:
        """Re-download all secrets from BWS, with optional cache invalidation."""
        with self._lock:
            current_time = time.time()
            needs_refresh = force_refresh or (current_time - self._last_cache_refresh > self.cache_duration)
            if needs_refresh:
                self._attempt_cache_refresh(force_refresh)

    def call_and_return_text(
        self, cl_args: list, print_to_console: bool = False, as_json: bool = True
    ) -> str | dict | list:
        """Make a call to `bws` CLI. Be careful with this as it can break compatibility with the BWS class (e.g.
            deleting all secrets in a project or creating secrets with duplicate key names). See README.md for more
            information.

        Args:
            cl_args (list): Args in list format (e.g. ['project', 'list']). Supply each word or option as a separate
                list item.
            print_to_console (bool, optional): Call print() on the stdout results. Defaults to False.
            as_json (bool, optional): Return the results converted to JSON. Defaults to True.

        Returns:
            str|dict|list: stdout
        """
        text: str = self._make_call(cl_args=cl_args, print_to_console=print_to_console)
        return json.loads(text) if as_json else text

    def get_secret(self, key: str, value_only: bool = False) -> dict | str:
        """When accessing the BWS object like a dictionary, only the 'value' field for the given key is returned.

        Args:
            key (str): Secret name.
            value_only (bool): Return only the secret's 'value' field instead of the whole dict.

        Returns:
            dict | str: Entire secret dict if value_only, else just the secret 'value' field as string.
                E.g. if dict:
                    {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                    'organizationId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                    'projectId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                    'key': 'secret_1',
                    'value': 'secret_1_value',
                    'note': '',
                    'creationDate': '2001-01-01T01:23:45.678901234Z',
                    'revisionDate': '2001-01-01T01:23:45.678901234Z'}

                E.g. if str: 'secret_1_value'
        """
        return self._secrets[key]["value"] if value_only else self._secrets[key]

    def add_secret(self, key: str, value: str, print_to_console: bool = False) -> dict:
        """Add a new secret key/value pair. Adds to the internal cache without refreshing the whole thing.

        Args:
            key (str): Key to add.
            value (str): Secret value.
            print_to_console (bool, optional): Call print() on the stdout results. Defaults to False.

        Returns:
            dict: Full new secret dict. E.g.
                {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'organizationId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'projectId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'key': 'secret_key',
                'value': 'secret_value',
                'note': '',
                'creationDate': '2001-01-01T01:23:45.678901234Z',
                'revisionDate': '2001-01-01T01:23:45.678901234Z'}
        """
        if key in self:
            raise RuntimeError(f"Key {key} already exists in the project. Did you mean to call update_secret_value()?")
        full_secret = self.call_and_return_text(
            cl_args=["secret", "create", key, value, self.project_id], print_to_console=print_to_console
        )
        logger.info(f'Added secret "{key}" to project "{self.project_name}"')
        self._secrets[key] = full_secret
        return full_secret

    def update_secret_value(self, key: str, value: str, print_to_console: bool = False) -> dict:
        """Update the value of a given secret. Updates internal cache without refreshing the whole thing.

        Args:
            key (str): Key to update.
            value (str): Replacement value.
            print_to_console (bool, optional): Call print() on the stdout results. Defaults to False.

        Returns:
            dict: Full updated secret dict. E.g.
                {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'organizationId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'projectId': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'key': 'secret_key',
                'value': 'secret_value',
                'note': '',
                'creationDate': '2001-01-01T01:23:45.678901234Z',
                'revisionDate': '2001-01-01T01:23:45.678901234Z'}
        """
        secret_id = self._secrets[key]["id"]
        full_secret = self.call_and_return_text(
            cl_args=["secret", "edit", secret_id, "--value", value], print_to_console=print_to_console
        )
        logger.info(f'Updated value for secret "{key}" in project "{self.project_name}"')
        self._secrets[key] = full_secret
        return full_secret

    def delete_secret(self, key: str, print_to_console: bool = False) -> None:
        """Delete a secret. Updates internal cache without refreshing the whole thing.

        Args:
            key (str): Key to delete.
            print_to_console (bool, optional): Call print() on the stdout results. Defaults to False.
        """
        secret_id = self._secrets[key]["id"]
        self.call_and_return_text(
            cl_args=["secret", "delete", secret_id], print_to_console=print_to_console, as_json=False
        )
        del self._secrets[key]
        logger.info(f'Deleted secret "{key}" from project "{self.project_name}"')

    def items(self) -> list[tuple[str, dict]]:
        """Call .items() on the secrets cache.

        Returns:
            list[tuple[str, dict]]: List of secrets like [(key:str, value:dict)].
        """
        return self._secrets.items()

    def as_dict(self) -> dict[str, dict[str, dict]]:
        """Returns a deepcopy of the internal secrets cache containing all project secrets.

        Returns:
            dict[str, dict[str, dict]]: Deepcopy of internal _secrets object.
        """
        return deepcopy(self._secrets)

    def help(self, print_to_console=True) -> str:
        """`bws` -h (help) command.

        Args:
            print_to_console (bool, optional): Defaults to True.

        Returns:
            str: Console output as string.
        """
        return self.call_and_return_text(cl_args=["-h"], print_to_console=print_to_console, as_json=False)

    def version(self, print_to_console=True) -> str:
        """`bws` -V (version) command.

        Args:
            print_to_console (bool, optional): Defaults to True.

        Returns:
            str: Console output as string.
        """
        return self.call_and_return_text(cl_args=["-V"], print_to_console=print_to_console, as_json=False)
