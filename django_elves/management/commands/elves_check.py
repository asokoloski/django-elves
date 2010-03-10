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
        from django.utils.termcolors import colorize
        from django.core.exceptions import ImproperlyConfigured
        errors = []

        def bail_if_errors():
            if errors:
                for e in errors:
                    print colorize(e, fg='red')
                exit(1)

        try:
            app_settings.check()
        except ImproperlyConfigured, e:
            errors.append(e.args[0])

        bail_if_errors()

        from django_elves.compiler import sprite_manager
        if len(sprite_manager.sprites) == 0:
            print 'No sprites found.  This may be ok, if you have not defined any yet.'

        if int(options['verbosity']) > 1:
            print " --- SPRITES --- "
            for s in sorted(sprite_manager.sprites, key=lambda s: type(s).__name__):
                print type(s).__name__
                for im in s.images:
                    print '  ', im.filename
