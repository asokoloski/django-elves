from os.path import join as joinpath, normpath, abspath, exists
from urlparse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

ORIGINAL_PATH = getattr(settings, 'ELVES_ORIGINAL_PATH', settings.MEDIA_ROOT)
OUTPUT_PATH = getattr(settings, 'ELVES_OUTPUT_PATH', joinpath(settings.MEDIA_ROOT, 'autosprites'))
OUTPUT_URL = getattr(settings, 'ELVES_OUTPUT_URL', urljoin(settings.MEDIA_URL, 'autosprites/'))
SPRITE_DEFS = getattr(settings, 'ELVES_SPRITE_DEFS', 'sprites')

COMPILED_PATH = getattr(settings, 'ELVES_COMPILED_PATH', None)

CSS_RENDERER = getattr(settings, 'ELVES_CSS_RENDERER', 'django_elves.templatetags.django_elves_tags.SpriteCSSRenderer')

# allow lazy evaluation
for name in ['ORIGINAL_PATH', 'OUTPUT_PATH', 'OUTPUT_URL', 'SPRITE_DEFS', 'COMPILED_PATH']:
    val = globals()[name]
    if callable(val):
        globals()[name] = val(settings)

def check():
    def ok(msg):
        print msg

    if not COMPILED_PATH:
        raise ImproperlyConfigured('To use django-elves, you must set ELVES_COMPILED_PATH to an empty directory.  '
                                   'Compiled sprite definitions will be cached there.  This must be an absolute path.')

    if normpath(COMPILED_PATH) != normpath(abspath(COMPILED_PATH)):
        raise ImproperlyConfigured('ELVES_COMPILED_PATH must be an absolute path.  %r is invalid.' % COMPILED_PATH)
    if not exists(COMPILED_PATH):
        raise ImproperlyConfigured('ELVES_COMPILED_PATH (%r) does not exist.' % COMPILED_PATH)
    ok('ELVES_COMPILED_PATH = %s' % COMPILED_PATH)

    if not exists(ORIGINAL_PATH):
        raise ImproperlyConfigured('ELVES_ORIGINAL_PATH (%r) does not exist.  It defaults to settings.MEDIA_ROOT.' % ORIGINAL_PATH)
    ok('ELVES_ORIGINAL_PATH = %s' % ORIGINAL_PATH)

    if not exists(OUTPUT_PATH):
        raise ImproperlyConfigured('ELVES_OUTPUT_PATH (%r) does not exist.  It defaults to settings.MEDIA_ROOT + "/autosprites".' % OUTPUT_PATH)
    ok('ELVES_OUTPUT_PATH = %s' % OUTPUT_PATH)

    try:
        __import__(SPRITE_DEFS, level=0)
    except ImportError, e:
        raise ImproperlyConfigured('Could not import ELVES_SPRITE_DEFS module (%r): %s' %
                                   (SPRITE_DEFS, e.args[0]))
    ok('ELVES_SPRITE_DEFS = %s' % SPRITE_DEFS)

    ok('ELVES_OUTPUT_URL = %s' % OUTPUT_URL)

    from django_elves.templatetags.django_elves_tags import get_renderer
    get_renderer()
    ok('ELVES_CSS_RENDERER = %s' % CSS_RENDERER)

