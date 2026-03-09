#!/usr/bin/env python
"""Django management command entry point."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django niet gevonden. Controleer of het geinstalleerd is "
            "en beschikbaar is in de PYTHONPATH omgevingsvariabele."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
