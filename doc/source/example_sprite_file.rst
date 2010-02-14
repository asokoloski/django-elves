
::

        from django_elves.compiler import *
        
        class icons(Sprite):
            direction = VERTICAL
            # default padding -- (10, 0) would also work,
            # as it has CSS-style defaults
            padding = (10, 0, 10, 0)
            # this means that within 10 pixels to the top and bottom of each sprite,
            # there will be nothing but transparent pixels (or the edge of the image).
        
            images = [
                Image('icons/smiley1.png'),
                Image('icons/smiley2.png'),
                Image('icons/smiley3.png'),
                Image('icons/frown.png', padding=(12, 0)), # different padding
                ]
        
        class box_sprite(Sprite):
            direction = HORIZONTAL
            
            images = [
                OpenImage('box_top.png', open_side=BOTTOM),
                RepeatedImage('box_mid.png'),
                OpenImage('box_bottom.png', open_side=TOP),
                ]
        
