About CSS Sprites
=================

CSS Sprites are a method for combining multiple images into one to
reduce latency when loading pages.  They use a composite image and
background position offsets to show only part of the image to the
user.

Using a single sprited image is often faster than separate images,
because the user's browser has to make a separate HTTP request for
each image.  Sending a large sprited image may turn out to be much
faster than even 2 or 3 small images.

Also, sprite images in PNG format can often be compressed quite well,
with any blank areas between the images taking up very little space.
Blank space may be needed if an image is intended to be displayed as
the background of a larger element, so that the other images in the
sprite do not peek out.

However, blank space is not entirely free, because when the image
arrives at the client computer, the browser will decompress it.  A
large image with lots of empty space may compress well, but it will
still take up a lot of space in memory once decompressed.