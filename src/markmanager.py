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

import tkinter as tk
from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw
import geomutils as gu


class MarkManager():
    """Class for marking image.

    This class provides everything for marking chosen image:
    - shows results of marking
    - provides controls and hotkeys for marks
    - serializes marks (in label-object)
    """

    __SCALE_COEFF = 3
    __RESIZED_SIZE = (224 * __SCALE_COEFF, 224 * __SCALE_COEFF)
    # GUI elements
    __root = None
    __canvas = None
    __fname_label = None

    __img = None
    __name = None
    __initial_marks = []
    __marks = []

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

    def reset_image(self, name, img, label):
        """."""
        self.__img = img.convert('RGBA')
        self.__name = name
        self.__initial_marks = label['marks'] if label else []
        self.__marks = self.__initial_marks
        self.__redraw()

    def serialize_marks(self):
        """."""
        label = {}
        label['filename'] = self.__name
        label['img_width'] = self.__img.width
        label['img_height'] = self.__img.height
        label['marks'] = self.__marks
        return label

    def __redraw(self):
        if self.__img:
            img = self.__img.resize(self.__RESIZED_SIZE)
            if self.__initial_marks:
                img = self.__draw_marks(img, self.__initial_marks, 'grey')
            if self.__marks:
                img = self.__draw_marks(img, self.__marks, 'blue')
            img_tk = ImageTk.PhotoImage(img)
            self.__canvas.create_image(0, 0, anchor='nw', image=img_tk)
            self.__canvas.image = img_tk
            self.__fname_label['text'] = self.__name
        else:
            self.__canvas.image = None
            self.__fname_label['text'] = 'no image'

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
        cx, cy, w, l, r = self.__get_mark_params(mark)
        xf = self.__create_xf(r, (cx, cy), scale)
        draw = ImageDraw.Draw(img)
        pline = [(l / 2, w / 2), (l / 2, -w / 2),
                 (-l / 2, -w / 2), (-l / 2, w / 2)]
        box_pts = gu.apply_xf(pline, xf)
        draw.polygon(box_pts, outline=color)
        arrow_pts = gu.apply_xf([(0, 0), (DIR_LEN, 0)], xf)
        draw.line(arrow_pts, fill=color, width=4)
        return img

    def __get_mark_params(self, mark):
        cx, cy = mark['center_x'], mark['center_y']
        width, length = mark['width'], mark['length']
        r = mark['rot_deg']
        return cx, cy, width, length, r

    def __create_xf(self, rot, translation, scale):
        rot_xf = gu.create_rotation_around_center_xf(rot)
        trans_xf = gu.create_translation_xf(translation)
        scale_xf = gu.create_scale_xf(scale)
        xf = gu.combine_xfs([trans_xf, rot_xf, scale_xf])
        return xf
