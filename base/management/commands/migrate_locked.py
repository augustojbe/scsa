from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

MIGRATION_LOCK_ID = 88776655


class Command(BaseCommand):
    help = (
        'Run migrations under a PostgreSQL advisory lock so only one '
        'app replica migrates at a time.'
    )

    def handle(self, *args, **options):
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute('SELECT pg_advisory_lock(%s)', [MIGRATION_LOCK_ID])
                self.stdout.write('Advisory lock acquired; running migrations...')
                try:
                    call_command('migrate', *args, **options)
                finally:
                    cursor.execute('SELECT pg_advisory_unlock(%s)', [MIGRATION_LOCK_ID])
                    self.stdout.write('Advisory lock released.')
        else:
            call_command('migrate', *args, **options)
