"""Explicit extension loading for configuration-independent runtime probes."""
import os


def isolated_options():
    """Keep system INI files disabled; optionally load packaged shared modules.

    PHP_TEST_EXTENSIONS is a comma-separated list such as ``json.so``.
    Minimal builds with integrated modules leave it unset.
    """
    options = ['-n']
    for extension in os.environ.get('PHP_TEST_EXTENSIONS', '').split(','):
        if extension.strip():
            options.extend(['-d', 'extension=' + extension.strip()])
    return options
