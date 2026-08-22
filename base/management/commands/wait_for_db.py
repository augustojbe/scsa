import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Wait for the database to become available before booting the app.'

    def handle(self, *args, **options):
        max_attempts = 60
        wait_seconds = 1
        for attempt in range(1, max_attempts + 1):
            try:
                connections['default'].ensure_connection()
                self.stdout.write(
                    self.style.SUCCESS(f'Database is available (attempt {attempt}).')
                )
                return
            except OperationalError:
                self.stdout.write(
                    f'Database not ready (attempt {attempt}/{max_attempts}); '
                    f'retrying in {wait_seconds}s...'
                )
                time.sleep(wait_seconds)
        raise SystemExit('Database did not become available in time.')
