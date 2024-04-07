"""
Django to wait to wait for the database to be available before continuing with the execution of the command.
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        """Handle the command"""
        pass 
        #self.stdout.write('Waiting for database...')
        #self.stdout.write('Database available!')
