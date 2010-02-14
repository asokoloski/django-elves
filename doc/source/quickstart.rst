Quick Start Guide
=================

This guide is intended to get you up and running with a mininmum of
configuration.  Once you get django_elves working, you may want to
look at the full configuration options.

#. Add the following setting to your :file:`settings.py`::

       COMPILED_PATH = '/(ABSOLUTE_PATH)...'

   Path to an empty directory.  Your sprite definitions will each be
   compiled into a layout, and cached in a python file in this directory.
   It is recommeded to set this to something like::

       COMPILED_PATH = '/YOUR_DJANGO_PROJECT_DIR/sprites' 

#. Make sure that any css files you need to serve are rendered as django
   templates.  A basic view has been provided, called *serve_rendered*, to
   aid with development. You really only want to render css files if
   possible, so the urlpatterns entry would look like::

       urlpatterns = patterns('',
           ...
           (r'^site_media/(?P<path>.*\.css)$', 'django_elves.views.simple.serve_rendered',
            {'document_root': settings.MEDIA_ROOT}),
       	...
       )

#. Create an empty file in the root of your project directory, called
   :file:`sprites.py`.  This is where you will defined which images are
   grouped together in sprites.

#. Run the management command

   :command:`manage.py elves_check`

   and fix any errors that it shows.  You will probably have to create
   the directory :file:`autosprites` within your settings.MEDIA_ROOT directory.

#. Define your sprites.  Here is an example sprite file:

   .. include:: example_sprite_file.rst