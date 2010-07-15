from operator import xor
import errno
import os
import sys
from pprint import pformat

from PIL import Image as PImage

from django_elves import app_settings
from django_elves.layout import *

__all__ = ('TOP', 'LEFT', 'RIGHT', 'BOTTOM', 'HORIZONTAL', 'VERTICAL',
           'Sprite', 'Image', 'OpenImage', 'RepeatedImage')

class SpriteValidationError(StandardError):
    pass

class SpriteManager(object):
    def __init__(self):
        self.lookup_dict = None
        self.sprites = set()

    def force_import(self):
        before_import = set(sys.modules.keys())
        # force the user's sprite definitions to be loaded
        __import__(app_settings.SPRITE_DEFS, level=0)
        after_import = set(sys.modules.keys())
        # save, so we know which modules to reload
        self.imported_sprite_modules = after_import - before_import

    def add_sprite(self, sprite):
        self.lookup_dict = None
        self.sprites.add(sprite)

    def table(self):
        self.force_import()
        if self.lookup_dict is None:
            lookup_dict = {}
            for s in self.sprites:
                lookup_dict.update(s.compiled)
            self.lookup_dict = lookup_dict
        return self.lookup_dict

    def compiled(self, original_path):
        return self.table()[original_path]

    def purge_compiled_files(self):
        self.force_import()
        for sprite in self.sprites:
            try:
                os.remove(sprite.compiled_filename())
            except OSError, e:
                if e.errno == errno.ENOENT:
                    pass

        for name in self.imported_sprite_modules:
            try:
                del sys.modules[name]
            except KeyError:
                pass

        self.lookup_dict = None
        self.sprites = set()

sprite_manager = SpriteManager()

class SpritedImage(object):
    _image = None
    def __init__(self, sprite, image_def):
        self.image_def = image_def
        self.sprite = sprite
        self.image_def.validate(self.sprite)
        self.padding = Padding(image_def.padding or sprite.padding)

    def_type = property(lambda self: type(self.image_def))

    @property
    def image(self):
        i = getattr(self, '_image', None)
        if not i:
            path = os.path.join(app_settings.ORIGINAL_PATH, self.image_def.filename)
            self._image = PImage.open(path)
        return self._image

    width = property(lambda self: self.image.size[0])
    height = property(lambda self: self.image.size[1])
    full_width = property(lambda self: self.image.size[0] + self.padding.left + self.padding.right)
    full_height = property(lambda self: self.image.size[1] + self.padding.top + self.padding.bottom)

    def select_dir(self, if_hor, if_ver):
        return if_hor if self.sprite.direction == HORIZONTAL else if_ver

    start_padding = property(lambda self: self.select_dir(self.padding.left, self.padding.top))
    end_padding   = property(lambda self: self.select_dir(self.padding.right, self.padding.bottom))

    thickness = property(lambda self: self.select_dir(self.height, self.width))
    length    = property(lambda self: self.select_dir(self.width, self.height))

    full_thickness = property(lambda self: self.select_dir(self.full_height, self.full_width))
    full_length    = property(lambda self: self.select_dir(self.full_width, self.full_height))

class Image(object):
    """
    :param filename:
      The path, relative to :data:`settings.ELVES_ORIGINAL_PATH`, of
      an image file.  This file can be of any type that PIL (the
      Python Imaging Library) supports, although I personally
      recommend PNG.  Output sprite files are always PNG for now.

    :param padding: A single integer, or a 1 to 4-tuple of integers, representing
      how much transparent space is required around the image in
      question.  Defaults to (0, 0, 0, 0)

      If a tuple, the elements represent::

          (top, right [default=top], bottom [default=top], left [default=right])

      You may omit all but the first element.  This works just like CSS.
    """
    def __init__(self, filename, padding=None):
        self.filename = filename
        if padding:
            padding = Padding(padding)
        self.padding = padding

    def validate(self, sprite):
        pass

    def __hash__(self):
        return hash(self.filename) ^ hash(self.padding)

class RepeatedImage(Image):
    """
    RepeatedImage is used to define an image that must be usable with
    css's ``background-repeat`` property, even within a sprited image.
    If other images in the sprite are thicker than a RepeatedImage, it
    will be repeated within the sprite to fill the available
    horizontal space (for VERTICAL sprites) or vertical space (for
    HORIZONTAL sprites).  Note -- if the image contains a pattern, it
    may not sync up nicely.
    """
    pass

class OpenImage(Image):
    """
    Mainly for backwards-compatibility with existing HTML and CSS that
    expects the image to be aligned to one side of the element,
    especially aligned to the right or bottom, because this is not
    possible to do with a pixel-position.

    Usually you won't need OpenImage, because you can use a regular
    Image in a fixed-size element instead.

    Accepts the same arguments as Image, plus:

    :param open_side: ``TOP``, ``LEFT``, ``RIGHT``, or ``BOTTOM``.
      The side of the image that is open to the element.  If the
      open_side is TOP, for example, the image will be bottom-aligned.
    """
    def __init__(self, filename, open_side, padding=None):
        assert open_side in (TOP, RIGHT, BOTTOM, LEFT)
        self.open_side = open_side
        super(OpenImage, self).__init__(filename, padding)

    def validate(self, sprite):
        if sprite.direction == VERTICAL and self.open_side in (TOP, BOTTOM):
            raise SpriteValidationError('Vertical sprites cannot have OpenImages that open to top or bottom.')
        elif sprite.direction == HORIZONTAL and self.open_side in (LEFT, RIGHT):
            raise SpriteValidationError('Horizontal sprites cannot have OpenImages that open to left or right.')

class SpriteMeta(type):
    def __new__(mcls, name, bases, attrs):
        cls = super(SpriteMeta, mcls).__new__(mcls, name, bases, attrs)
        if cls.images:
            cls.sprited_images = [SpritedImage(cls, i) for i in cls.images]
            sprite = cls()
            sprite_manager.add_sprite(sprite)
        return cls

class StaleCacheException(Exception):
    pass

class Sprite(object):
    """
    The base class for a user-defined sprite.  Sprite has some magic
    defined for it, so all you need to do is define the subclass and
    django-elves will know about it.  Usage::

        class my_sprite_1(Sprite):
            direction = HORIZONTAL or VERTICAL
            padding = (10, 20) # optional default padding

            images = [
                 Image(...),
                 ...
                 ]

    :data:`direction`: ``HORIZONTAL`` or ``VERTICAL``. Specifies
    whether the images that make up the sprite should be arranged in a
    horizontal line or a vertical line.  Currently, django-elves does
    not have a sophisticated packing algorithm -- it just puts all the
    images in a straight line.

    This does have the benefit of allowing sprites to contain images
    that can be repeated using css ``background-repeat``.  Use
    :class:`django_elves.compiler.RepeatedImage` to specify this kind
    of image.

    :data:`padding`: The default padding to use for images where
    padding is not specified.  Optional, defaults to (0, 0, 0, 0).

    :data:`images`: A list of :class:`django_elves.compiler.Image`
    objects that defines which images should be compiled into this
    sprite.  Any Image (or subclass) instance is acceptable.
    """
    sprited_images = None
    __metaclass__ = SpriteMeta

    padding = (0, 0, 0, 0)
    direction = VERTICAL
    images = []
    _compiled = None

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def to_coord(cls, thickness, length):
        if cls.direction == HORIZONTAL:
            return length, thickness
        elif cls.direction == VERTICAL:
            return thickness, length

    def make_image(self):
        max_thickness = max(im.full_thickness for im in self.sprited_images)
        length = sum(im.full_length for im in self.sprited_images)

        spr = PImage.new('RGBA', self.to_coord(max_thickness, length), (0, 0, 0, 0))
        compiled = CompiledSprite(self.hash())

        along = 0
        for im in self.sprited_images:
            def add_compiled(where, repeat=None, align=None):
                compiled[im.image_def.filename] = CompiledImage(self.name(),
                                                                where,
                                                                im.image.size,
                                                                im.padding,
                                                                repeat=repeat,
                                                                align=align)

            if im.def_type == RepeatedImage:
                across = 0
                def get_where():
                    return self.to_coord(across, along + im.start_padding)
                add_compiled(get_where(), repeat='repeat-x' if self.direction == VERTICAL else 'repeat-y')

                while across < max_thickness:
                    spr.paste(im.image, get_where())
                    across += im.thickness

            elif im.def_type == OpenImage:
                basic_direction = BOTTOM if self.direction == HORIZONTAL else RIGHT
                if im.image_def.open_side == basic_direction:
                    where = self.to_coord(0, along)
                    where_padded = where[0] + im.padding.left, where[1] + im.padding.top
                else:
                    where = self.to_coord(max_thickness - im.thickness, along)
                    where_padded = where[0] + im.padding.left, where[1] - im.padding.bottom
                spr.paste(im.image, where_padded)
                add_compiled(where_padded, align=direction_name(opposite_side(im.image_def.open_side)))
            else:
                where = self.to_coord(0, along)
                where_padded = where[0] + im.padding.left, where[1] + im.padding.top
                spr.paste(im.image, where_padded)
                add_compiled(where_padded)

            along += im.full_length

        return compiled, spr

    def compile(self):
        output_image_filename = os.path.join(app_settings.OUTPUT_PATH, self.name() + '.png')

        compiled, im = self.make_image()
        im.save(output_image_filename)
        return compiled

    def hash(self):
        images_hash = reduce(xor, (hash(i) for i in self.images))
        return images_hash ^ hash(self.direction) ^ hash(self.padding)

    def compiled_filename(self):
        return os.path.join(app_settings.COMPILED_PATH, self.name() + '.py')

    @property
    def compiled(self):
        if not getattr(self, '_compiled', None):
            def recompile_and_save():
                self._compiled = self.compile()
                f = open(self.compiled_filename(), 'wb')
                f.write('from django_elves.compiler import CompiledImage, CompiledSprite\n\n')
                f.write('SPRITE = \\\n%r\n' % self._compiled)
                f.close()

            try:
                locals_dict = {}
                execfile(self.compiled_filename(), locals_dict, locals_dict)
                self._compiled = locals_dict['SPRITE']
                if self._compiled.hash != self.hash():
                    raise StaleCacheException()
            except StaleCacheException:
                recompile_and_save()
            except (IOError, OSError), e:
                if e.errno == errno.ENOENT:
                    recompile_and_save()
                else:
                    raise

        return self._compiled

class CompiledSprite(dict):
    def __init__(self, hash, data=None):
        super(CompiledSprite, self).__init__(data or {})
        self.hash = hash

    def __repr__(self):
        return 'CompiledSprite(%r, %s)' % (self.hash, pformat(dict(self)))

class CompiledImage(object):
    def __init__(self, sprite, position, size, padding, repeat=None, align=None):
        self.sprite = sprite
        self.pos = position
        self.size = size
        self.padding = tuple(padding)
        self.repeat = repeat
        self.align = align

    def __repr__(self):
        return 'CompiledImage(%r, %r, %r, %r%s%s)' % (
            self.sprite,
            self.pos,
            self.size,
            self.padding,
            (', repeat=%r' % self.repeat if self.repeat is not None else ''),
            (', align=%r' % self.align if self.align is not None else ''),
            )

