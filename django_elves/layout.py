"""Basic helpers for laying out sprites in an image, as well as
layout-related constants."""

__all__ = ('VERTICAL', 'HORIZONTAL', 'TOP', 'RIGHT', 'BOTTOM', 'LEFT',
           'direction_name', 'opposite_side', 'Padding')

VERTICAL, HORIZONTAL = 0, 1
TOP, RIGHT, BOTTOM, LEFT = 0, 1, 2, 3

def direction_name(direction):
    "Return the actual name for a direction constant's numeric value."
    return ('top', 'right', 'bottom', 'left')[direction]

def opposite_side(side):
    "Return the opposite site:  TOP <-> BOTTOM, LEFT <-> RIGHT"
    return (side + 2) % 4

class Padding(tuple):
    """A tuple-like object representing padding on 4 sides: TOP,
    RIGHT, LEFT, and BOTTOM.  Immutable, and has CSS-like defaults."""

    def __new__(cls, a, *rest):
        if isinstance(a, cls):
            return a
        if isinstance(a, tuple):
            rest = a[1:]
            a = a[0]

        num = len(rest)
        b = rest[0] if num >= 1 else a
        c = rest[1] if num >= 2 else a
        d = rest[2] if num >= 3 else b
        return tuple.__new__(cls, (a, b, c, d))

    top    = property(lambda self: self[0])
    right  = property(lambda self: self[1])
    bottom = property(lambda self: self[2])
    left   = property(lambda self: self[3])

    def __repr__(self):
        return 'Padding(%d, %d, %d, %d)' % self

