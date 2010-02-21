Sprite Definitions
==================

Sprite definitions go into a python file referenced by the
ELVES_SPRITE_DEFS setting. ::

    from django_elves.compiler import *
    # compiler is import-* safe

    class registration_icons(Sprite):
        ...

    class overview_icons(Sprite):
        ...

.. autoclass:: django_elves.compiler.Sprite

.. autoclass:: django_elves.compiler.Image

.. autoclass:: django_elves.compiler.RepeatedImage

.. autoclass:: django_elves.compiler.OpenImage
