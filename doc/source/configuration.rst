Configuration
=============

These should go into your project's django settings file.

Mandatory settings:

:data:`ELVES_COMPILED_PATH`
  Django-elves needs to remember which image is in which part of a
  sprite.  To do so, it writes a file for each sprite it creates.
  This directory specifies where those files should go.  You must
  create the directory yourself.

Optional settings:

:data:`ELVES_ORIGINAL_PATH`
  This is where django-elves will look for images that you put in
  sprite definitions.  In other words, when you define an image in a
  sprite -- ``Image(filename)`` -- the filename is relative to this path.
  The default is your :data:`settings.MEDIA_ROOT`.

:data:`ELVES_OUTPUT_PATH`
  This is the directory where (whither?) the final sprite files shall
  be written.  The default is ``os.path.join(settings.MEDIA_ROOT,
  'autosprites')``.

:data:`ELVES_OUTPUT_URL`

  This is a URL, relative to which django-elves expects the sprite
  files to be served.  It is basically the url version of
  :data:`OUTPUT_PATH`.  The default is
  ``urlparse.urljoin(settings.MEDIA_ROOT, 'autosprites'``.
  
:data:`ELVES_SPRITE_DEFS`:

  This is the python module where you will define your sprites.  The
  default is ``sprites``.  The file itself can be anywhere, as long as
  python can reach it using that name.


