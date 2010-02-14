from os.path import join as joinpath, normpath, abspath, exists
from urlparse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

ORIGINAL_PATH = getattr(settings, 'ELVES_ORIGINAL_PATH', settings.MEDIA_ROOT)
OUTPUT_PATH = getattr(settings, 'ELVES_OUTPUT_PATH', joinpath(settings.MEDIA_ROOT, 'autosprites'))
OUTPUT_URL = getattr(settings, 'ELVES_OUTPUT_URL', urljoin(settings.MEDIA_URL, 'autosprites/'))
SPRITE_DEFS = getattr(settings, 'ELVES_SPRITE_DEFS', 'sprites')

COMPILED_PATH = getattr(settings, 'ELVES_COMPILED_PATH', None)


def check():
    if not COMPILED_PATH:
        raise ImproperlyConfigured('To use django-elves, you must set ELVES_COMPILED_PATH to an empty directory.  '
                                   'Compiled sprite definitions will be cached there.  This must be an absolute path.')

    if not exists(ORIGINAL_PATH):
        raise ImproperlyConfigured('ELVES_ORIGINAL_PATH (%r) does not exist.  It defaults to settings.MEDIA_ROOT.' % ORIGINAL_PATH)
    if not exists(OUTPUT_PATH):
        raise ImproperlyConfigured('ELVES_OUTPUT_PATH (%r) does not exist.  It defaults to settings.MEDIA_ROOT + "/sprites".' % OUTPUT_PATH)

    if normpath(COMPILED_PATH) != normpath(abspath(COMPILED_PATH)):
        raise ImproperlyConfigured('ELVES_COMPILED_PATH must be an absolute path.  %r is invalid.' % COMPILED_PATH)
    if not exists(COMPILED_PATH):
        raise ImproperlyConfigured('ELVES_COMPILED_PATH (%r) does not exist.' % COMPILED_PATH)

    try:
        __import__(SPRITE_DEFS, level=0)
    except ImportError, e:
        raise ImproperlyConfigured('Could not import ELVES_SPRITE_DEFS module (%r): %s' %
                                   (SPRITE_DEFS, e.args[0]))
