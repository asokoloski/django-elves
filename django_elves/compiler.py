from operator import xor
import os
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
        # force the user's sprite definitions to be loaded
        __import__(app_settings.SPRITE_DEFS, level=0)

    def add_sprite(self, sprite):
        self.lookup_dict = None
        self.sprites.add(sprite)

    def compiled(self, original_path):
        self.force_import()

        if self.lookup_dict is None:
            lookup_dict = {}
            for s in self.sprites:
                lookup_dict.update(s.compiled)
            self.lookup_dict = lookup_dict

        return self.lookup_dict[original_path]
            
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
    pass

class OpenImage(Image):
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

class Sprite(object):
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

    @property
    def compiled(self):
        if not getattr(self, '_compiled', None):
            compiled_filename = os.path.join(app_settings.COMPILED_PATH, self.name() + '.py')
            locals_dict = {}
            try:
                execfile(compiled_filename, locals_dict, locals_dict)
            except (IOError, OSError), e:
                import errno
                if e.errno == errno.ENOENT:
                    self._compiled = self.compile()
                    f = open(compiled_filename, 'wb')
                    f.write('from django_elves.compiler import CompiledImage, CompiledSprite\n\n')
                    f.write('SPRITE = \\\n%r\n' % self._compiled)
                    f.close()
                else:
                    raise
            else:
                self._compiled = locals_dict['SPRITE']
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

