from urlparse import urljoin

from django import template as T

from django_elves import app_settings
from django_elves.compiler import sprite_manager

register = T.Library()

class SpriteNotFoundError(StandardError):
    pass

@register.tag()
def sprite(parser, token):
    """

    ``{% sprite "filename" xpos ypos %}``

    :param filename: This is the name of the original image, relative to your MEDIA_ROOT
        (or ELVES_ORIGINAL_PATH if you have defined it).

    :param xpos: Default 0. The x offset of the image inside the
        element.  This should not be quoted.

    :param ypos: Default 0. The y offset of the image inside the
        element.  This should not be quoted.

    If you are planning to use a sprited image within an element that
    is larger than the element itself, you should specify a padding
    for the sprite in the sprite definition.  This will ensure that
    other images don't "intrude" on your element's background.

    Examples::

        {% sprite "images/arrows/circle/blue/right.png" 0 3 %}
        {% sprite "images/smiley.png" 10 10 %}
        {% sprite "images/sweet_background.png" %}
    """
    args = token.split_contents()
    try:
        x, y = args[2:4]
    except (IndexError, ValueError):
        x, y = '0', '0'

    return make_sprite_tag(T.Variable(args[1]), T.Variable(x), T.Variable(y))

def make_sprite_tag(filename_var, x_var, y_var):
    # if possible, evaluate sprite while compiling the template.
    # otherwise defer evaluation
    if filename_var.literal and x_var.literal and y_var.literal:
        cls = CompiledSpriteTag
    else:
        cls = RuntimeSpriteTag
    return cls(filename_var, x_var, y_var)


class SpriteTag(T.Node):
    errtype = T.TemplateSyntaxError

    def __init__(self, filename_var, x_var, y_var):
        super(SpriteTag, self).__init__()
        self.filename_var = filename_var
        self.x_var = x_var
        self.y_var = y_var
        self.setup()

    def setup(self):
        pass

    def evaluate(self, context):
        x = self.x_var.resolve(context)
        y = self.y_var.resolve(context)
        try:
            y = int(y)
            x = int(x)
        except (TypeError, ValueError):
            if x not in ('right', 'left'):
                raise self.errtype('%s tag needs integral x and y coordinates, or right or left' % args[0])

        im_file = self.filename_var.resolve(context)
        try:
            chunk = sprite_manager.compiled(im_file)
        except KeyError:
            raise SpriteNotFoundError('Could not find sprited image named "%s".  ' % im_file)

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

        return chunk.sprite, chunk.repeat or 'no-repeat', (xpos, ypos)

class CompiledSpriteTag(SpriteTag):
    def setup(self):
        self.sprite_name, self.repeat, self.pos = self.evaluate({})

    def render(self, context):
        return RENDERER.render('%s.png' % self.sprite_name, self.repeat, self.pos)

class RuntimeSpriteTag(SpriteTag):
    def render(self, context):
        sprite_name, repeat, pos = self.evaluate(context)
        return RENDERER.render('%s.png' % sprite_name, repeat, pos)

class SpriteCSSRenderer(object):
    def render(self, filename, repeat, pos):
        sprite_url = urljoin(app_settings.OUTPUT_URL, filename)
        return "background-image: url('%s'); background-repeat: %s; background-position: %s %s;" % \
            (sprite_url, repeat, pos[0], pos[1])

RENDERER = SpriteCSSRenderer()

