from os.path import join as joinpath, normpath, abspath, exists
from urlparse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

ORIGINAL_PATH = getattr(settings, 'ELVES_ORIGINAL_PATH', settings.MEDIA_ROOT)
if not exists(ORIGINAL_PATH):
    raise ImproperlyConfigured('ELVES_ORIGINAL_PATH (%r) does not exist.  It defaults to settings.MEDIA_ROOT.' % ORIGINAL_PATH)

OUTPUT_PATH = getattr(settings, 'ELVES_OUTPUT_PATH', joinpath(settings.MEDIA_ROOT, 'sprites'))
if not exists(OUTPUT_PATH):
    raise ImproperlyConfigured('ELVES_OUTPUT_PATH (%r) does not exist.  It defaults to settings.MEDIA_ROOT + "/sprites".' % OUTPUT_PATH)

OUTPUT_URL = getattr(settings, 'ELVES_OUTPUT_URL', urljoin(settings.MEDIA_URL, 'sprites/'))

try:
    COMPILED_PATH = settings.ELVES_COMPILED_PATH
except AttributeError:
    raise ImproperlyConfigured('To use django-elves, you must set ELVES_COMPILED_PATH to an empty directory.  '
                               'Compiled sprite definitions will be cached there.  This must be an absolute path.')

if normpath(COMPILED_PATH) != normpath(abspath(COMPILED_PATH)):
    raise ImproperlyConfigured('ELVES_COMPILED_PATH must be an absolute path.')
if not exists(COMPILED_PATH):
    raise ImproperlyConfigured('ELVES_COMPILED_PATH (%r) does not exist.' % COMPILED_PATH)

