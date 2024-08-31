"""
    Custom commnad.
"""
import time
from psycopg2 import OperationalError as Psycopg2Error
from typing import Any

from django.core.management import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    """ Command module. """
    def handle(self, *args: Any, **options: Any):
        """Handle overring

        Returns:
            str | None: _description_
        """
        self.stdout.write("Waiting for database...")
        found_db = False
        while not found_db:
            try:
                self.check(databases=['default'])
                found_db = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database unavailable, waiting for\
                    1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available"))
        # return super().handle(*args, **options)
