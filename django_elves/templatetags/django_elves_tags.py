from urlparse import urljoin

from django import template as T

from django_elves import app_settings
from django_elves.compiler import sprite_manager

register = T.Library()

@register.tag()
def sprite(parser, token):
    """
    CSS Sprites are a method for combining multiple images into one to
    reduce latency when loading pages.  They use a composite image and
    background position offsets to show only part of the image to the
    user.

    To create sprites automatically:

    Create a new python file, or edit one, in the directory
    playfire/media/sprites/.  These files and their names are purely
    organizational -- you can have more than one sprite in the file.::

        # playfire/media/sprites/sprites1.py
        from g4mer.templatetags.sprites import *

        class arrows(Sprite):
            direction = VERTICAL
            padding = 10, 0, 10, 0 # or 10, 0 -- defaults work just like css

            images = [
                Image('images/arrows/circle/blue/left.png', padding=(10, 5)),
                Image('images/arrows/circle/blue/right.png'),
                Image('images/arrows/circle/red/left.png', padding=(10, 2)),
                Image('images/arrows/circle/red/right.png'),
                ]

    In this example, arrows will become the name of the sprite
    (arrows.png).  It includes four images, two of which have
    individual padding specified.  The other two take their default
    padding from the top-level Sprite padding, and if that did not
    exist the padding would be (0, 0, 0, 0).

    direction = VERTICAL means that the sprited images will be
    arranged vertically.

    To use the sprite, simply include the sprite templatetag with the
    original image name, like so::

        {% sprite "images/arrows/circle/blue/right.png" 0 3 %}

    This will result in the following css.::

        background: url("http://local-media/static/images/sprites/6e4e30a8/arrows.png?59a512") no-repeat 0px -37px;

    Without the 3, it would have a y-offset of -40px; The offset
    passed in the sprite tag is added to the offset necessary to
    position the sprited image.  Offsets default to zero.

    More complicated sprites are also possible.  If you want your
    sprite to work with content that expands vertically, you can do
    something like this::

        from g4mer.templatetags.sprites import *

        class dialogs(Sprite):
            direction = HORIZONTAL

            images = [
                OpenImage('images/top.png', open_side=BOTTOM),
                RepeatedImage('images/middle.png'),
                OpenImage('images/bottom.png', open_side=TOP),
                ]

    In this case, you can use the sprite tag without offset arguments,
    and they will be automatically deduced. The top image will be
    aligned to the top of its element, the bottom image to the bottom,
    and the middle image will have repeat: repeat-y enabled.
    """
    args = token.split_contents()
    try:
        x, y = args[2:4]
    except (IndexError, ValueError):
        x, y = 0, 0

    try:
        y = int(y)
        x = int(x)
    except (TypeError, ValueError):
        if x not in ('right', 'left'):
            raise T.TemplateSyntaxError('%s tag needs integral x and y coordinates' % args[0])

    args = args[0:2] + args[4:]
    im_file = T.Variable(args[1])
    assert im_file.literal, 'Sprite filenames must be literal strings.  They cannot be template variables.'
    im_file = im_file.resolve({})
    try:
        chunk = sprite_manager.compiled(im_file)
    except KeyError:
        raise T.TemplateSyntaxError('Could not find sprited image named "%s".  ' % im_file)

    xpos, ypos = None, None
    if chunk.align in ('top', 'bottom'):
        ypos = chunk.align
    elif chunk.align in ('left', 'right'):
        xpos = chunk.align
    elif x in ('left', 'right'):
        xpos = x

    if ypos is None:
        ypos = str(y - chunk.pos[1]) + 'px'
    if xpos is None:
        xpos = str(x - chunk.pos[0]) + 'px'

#    wrapper = 'background: url("%%s") %(repeat)s %(x)s %(y)s;' % tup
#    return process_media_tag(parser, args, 'static', wrapper=wrapper)
    return SpriteTag(chunk.sprite, chunk.repeat or 'no-repeat', xpos, ypos)

class SpriteTag(T.Node):
    def __init__(self, sprite_filename, repeat, x, y):
        self.sprite_url = urljoin(app_settings.OUTPUT_URL, '%s.png' % sprite_filename)
        self.repeat = repeat
        self.pos = x, y
        super(SpriteTag, self).__init__()

    def render(self, context):
        return "background-image: url('%s'); background-repeat: %s; background-position: %s %s" % \
            (self.sprite_url, self.repeat, self.pos[0], self.pos[1])

        
