import os
from django.core.management.base import NoArgsCommand
from optparse import make_option
from django_elves import app_settings

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
    )
    help = "Cleans out generated sprite files, so they can be re-generated."

    requires_model_validation = False

    def handle_noargs(self, **options):
        from django_elves.compiler import sprite_manager
        sprite_manager.purge_compiled_files()
