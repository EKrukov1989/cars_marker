"""Module for MarkManager class.

Example of label.json:
{
    'filename': '000000000.jpg',
    'img_height': 224,
    'img_width': 224,
    'marks':[
        {
            'center_x':26.5,
            'center_y':27.5,
            'width':9,
            'length':22,
            'rot_deg':62.5}
        }
    ]
}
"""

import copy
import time
import numpy as np
import tkinter as tk
from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw
import geomutils as gu
from mover import Mover
from rotator import Rotator


class Mark():
    """."""

    cx, cy, w, le, r = 0, 0, 0, 0, 0

    def __init__(self, cx, cy, w, length, r):
        """."""
        self.cx, self.cy = cx, cy
        self.w, self.length, self.r = w, length, r

    def serialize(self):
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


class MarkManager():
    """Class for marking image.

    This class provides everything for marking chosen image:
    - shows results of marking
    - provides controls and hotkeys for marks
    - serializes marks (in label-object)
    """

    __IMG_SZ = (224, 224)
    __SCALE_COEFF = 3
    __RESIZED_SIZE = (__IMG_SZ[0] * __SCALE_COEFF, __IMG_SZ[1] * __SCALE_COEFF)

    __MOVE_C = 1
    __ROT_C = 1
    __W_C = 1
    __L_C = 1
    _W_MIN, _W_MAX = 6, 16
    _L_MIN, _L_MAX = 15, 28

    __LEGEND = """Commands:
A, Delete - add/remove new mark;
Page Down, Page Up - chose next of previous mark on image;
Left, Right, Up, Down - move chosen mark;
Control + Left/Right/Up/Down - change width and length of mark;
W, Q - rotate chosen mark clockwese/counterclockwise.
"""

    __root = None
    __canvas = None
    __fname_label = None

    __img = None
    __name = None
    __init_label = None
    __initial_marks = []
    __marks = []
    __chosen_mark_idx = None

    __mover = None
    __rotator = None

    def __init__(self, root):
        """."""
        self.__root = root
        self.__canvas = tk.Canvas(root)
        self.__canvas['bg'] = 'white'
        w, h = self.__RESIZED_SIZE
        self.__canvas.place(x=20, y=30, width=w, height=h)
        self.__fname_label = tk.Label(root, text="No image")
        self.__fname_label.place(x=20, y=10)
        self.__redraw()
        self.__connect_hotkeys(self.__root)

    def __connect_hotkeys(self, root):
        r = root
        r.bind("<Key-a>", lambda ev: self.__add_mark_and_select_it())
        r.bind("<Prior>", lambda ev: self.__choose_prev_mark())
        r.bind("<Next>", lambda ev: self.__choose_next_mark())
        r.bind("<Delete>", lambda ev: self.__remove_mark())

        self.__mover = Mover(root, self.__move_mark)
        self.__rotator = Rotator(root, self.__rotate_mark)
        r.bind("<Control-Left>", lambda ev: self.__change_width(-self.__W_C))
        r.bind("<Control-Right>", lambda ev: self.__change_width(self.__W_C))
        r.bind("<Control-Up>", lambda ev: self.__change_length(self.__L_C))
        r.bind("<Control-Down>", lambda ev: self.__change_length(-self.__L_C))

    def reset_image(self, name, img, label):
        """."""
        self.__img = img.convert('RGBA')
        self.__name = name
        self.__init_label = label
        self.__initial_marks = []
        if label:
            self.__initial_marks = list(map(deserialize_mark, label['marks']))
        self.__marks = copy.deepcopy(self.__initial_marks)
        self.__chosen_mark_idx = 0 if len(self.__marks) > 0 else None
        self.__redraw()

    def __redraw(self):
        if not self.__img:
            self.__canvas.image = None
            self.__fname_label['text'] = 'no image'
            return
        img = self.__img.resize(self.__RESIZED_SIZE)
        if self.__initial_marks:
            img = self.__draw_marks(img, self.__initial_marks, 'grey')
        if self.__marks:
            unchosen_marks = copy.deepcopy(self.__marks)
            del unchosen_marks[self.__chosen_mark_idx]
            chosen_marks = [self.__marks[self.__chosen_mark_idx]]
            if unchosen_marks:
                img = self.__draw_marks(img, unchosen_marks, 'blue')
            img = self.__draw_marks(img, chosen_marks, 'red')
        img_tk = ImageTk.PhotoImage(img)
        self.__canvas.create_image(0, 0, anchor='nw', image=img_tk)
        self.__canvas.image = img_tk
        lbl_str = 'exists' if self.__init_label else 'absents'
        t = 'image file: {}, (label file - {})'.format(self.__name, lbl_str)
        self.__fname_label['text'] = t
        self.__root.update_idletasks()

    def __draw_marks(self, img, marks, color):
        UPSC_C = 4
        UPSC_SZ = (224 * UPSC_C, 224 * UPSC_C)
        mark_img = Image.new('RGBA', UPSC_SZ, color=(0, 0, 0, 0))
        for mark in marks:
            self.__draw_mark(mark_img, UPSC_C, mark, color=color)
        mark_img = mark_img.resize(self.__RESIZED_SIZE)
        img.alpha_composite(mark_img)
        return img

    def __draw_mark(self, img, scale, mark, color):
        DIR_LEN = 20
        m = mark
        xf = self.__create_xf(m.r, (m.cx, m.cy), scale)
        draw = ImageDraw.Draw(img)
        pline = [(m.length / 2, m.w / 2), (m.length / 2, -m.w / 2),
                 (-m.length / 2, -m.w / 2), (-m.length / 2, m.w / 2)]
        box_pts = gu.apply_xf(pline, xf)
        draw.polygon(box_pts, outline=color)
        arrow_pts = gu.apply_xf([(0, 0), (DIR_LEN, 0)], xf)
        draw.line(arrow_pts, fill=color, width=4)
        return img

    def __create_xf(self, rot, translation, scale):
        rot_xf = gu.create_rotation_around_center_xf(rot)
        trans_xf = gu.create_translation_xf(translation)
        scale_xf = gu.create_scale_xf(scale)
        xf = gu.combine_xfs([trans_xf, rot_xf, scale_xf])
        return xf

    def get_legend(self):
        """."""
        return self.__LEGEND

    def __choose_prev_mark(self):
        if self.__chosen_mark_idx > 0:
            self.__chosen_mark_idx -= 1
            self.__redraw()

    def __choose_next_mark(self):
        if self.__chosen_mark_idx < len(self.__marks) - 1:
            self.__chosen_mark_idx += 1
            self.__redraw()

    def __add_mark_and_select_it(self):
        m = Mark(self.__IMG_SZ[0] / 2, self.__IMG_SZ[1] / 2, 10, 20, 0)
        if self.__marks:
            SH_C = 5
            lm = self.__marks[-1]
            m.cx += SH_C if lm.cx < self.__IMG_SZ[0] / 2 else -SH_C
            m.cy += SH_C if lm.cy < self.__IMG_SZ[1] / 2 else -SH_C
        self.__marks.append(m)
        self.__chosen_mark_idx = len(self.__marks) - 1
        self.__redraw()

    def __remove_mark(self):
        if self.__marks:
            del self.__marks[-1]
            m_len = len(self.__marks)
            self.__chosen_mark_idx = (m_len - 1) if m_len > 0 else None
            self.__redraw()

    def __move_mark(self, shift):
        if self.__chosen_mark_idx is not None:
            chosen_mark = self.__marks[self.__chosen_mark_idx]
            chosen_mark.cx += shift[0]
            chosen_mark.cy -= shift[1]  # because of y inversion
            chosen_mark.cx = int(np.clip(chosen_mark.cx, 0, self.__IMG_SZ[0]))
            chosen_mark.cy = int(np.clip(chosen_mark.cy, 0, self.__IMG_SZ[1]))
            self.__redraw()

    def __rotate_mark(self, rot):
        if self.__chosen_mark_idx is not None:
            chosen_mark = self.__marks[self.__chosen_mark_idx]
            chosen_mark.r += rot
            self.__redraw()

    def __change_width(self, width_change):
        if self.__chosen_mark_idx is not None:
            chosen_mark = self.__marks[self.__chosen_mark_idx]
            chosen_mark.w += width_change
            chosen_mark.w = int(np.clip(chosen_mark.w,
                                self._W_MIN, self._W_MAX))
            self.__redraw()

    def __change_length(self, length_change):
        if self.__chosen_mark_idx is not None:
            chosen_mark = self.__marks[self.__chosen_mark_idx]
            chosen_mark.length += length_change
            chosen_mark.length = int(np.clip(chosen_mark.length,
                                     self._L_MIN, self._L_MAX))
            self.__redraw()

    def serialize_marks(self):
        """."""
        label = {}
        label['filename'] = self.__name
        label['img_width'] = self.__img.width
        label['img_height'] = self.__img.height
        label['marks'] = list(map(lambda m: m.serialize(), self.__marks))
        return label
