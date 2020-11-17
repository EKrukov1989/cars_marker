"""Module for Mark-class."""


class Mark():
    """This class with only one puprose - unify all data of mark."""

    cx, cy, w, le, r = 0, 0, 0, 0, 0

    def __init__(self, cx, cy, w, length, r):
        """."""
        self.cx, self.cy = cx, cy
        self.w, self.length, self.r = w, length, r

    def serialized(self):
        """."""
        return {'center_x': self.cx, 'center_y': self.cy,
                'width': self.w, 'length': self.length,
                'rot_deg': self.r}


def deserialize_mark(mark_dict):
    """."""
    cx, cy = mark_dict['center_x'], mark_dict['center_y']
    w, length = mark_dict['width'], mark_dict['length']
    r = mark_dict['rot_deg']
    return Mark(cx, cy, w, length, r)
