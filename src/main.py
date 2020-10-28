"""Main module for cars-marker.

This module consists all logic of top level
"""

import tkinter as tk
from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw
import numpy
import pathlib

from datasetmanager import DatasetManager
from markmanager import MarkManager

DS_PATH = pathlib.Path('src/cars_ds_test')
BTN_INDENT = 750
BTN_Y_INDENT = 20
BTN_Y_STEP = 40


def main():
    """Start application."""
    root = tk.Tk()
    root.wm_title('cars_marker')
    root.wm_iconbitmap('src/images/window.ico')
    root.geometry('1024x800')
    root.resizable(width=False, height=False)

    ds_m = DatasetManager(DS_PATH)
    mark_m = MarkManager(root)
    mark_m.reset_image(*ds_m.get_current())

    def move_to_prev_img():
        if ds_m.move_backward():
            mark_m.reset_image(*ds_m.get_current())
    prev_img_btn = tk.Button(root, text="prev image (Backspace)", width=20)
    prev_img_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT)
    prev_img_btn.config(command=move_to_prev_img)
    root.bind("<BackSpace>", lambda ev: move_to_prev_img())

    def move_to_next_img():
        if ds_m.move_forward():
            mark_m.reset_image(*ds_m.get_current())
    next_img_btn = tk.Button(root, text="next image (Enter)", width=20)
    next_img_btn.place(x=(BTN_INDENT + 180), y=BTN_Y_INDENT)
    next_img_btn.config(command=move_to_next_img)
    root.bind("<Return>", lambda ev: move_to_next_img())

    def move_to_first_unmarked_img():
        if ds_m.move_to_first_unmarked():
            mark_m.reset_image(*ds_m.get_current())
    first_umm_btn = tk.Button(root, width=28)
    first_umm_btn['text'] = 'move to first unmarked image'
    first_umm_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + BTN_Y_STEP)
    first_umm_btn.config(command=move_to_first_unmarked_img)

    def save_label():
        marks = mark_m.serialize_marks()
        ds_m.save_marks_in_label(marks)
    save_btn = tk.Button(root, text="save marks in label (S)", width=18)
    save_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + 2 * BTN_Y_STEP)
    save_btn.config(command=save_label)
    root.bind("<Key-s>", lambda ev: save_label())

    def remove_label():
        if ds_m.remove_label():
            mark_m.reset_image(*ds_m.get_current())
    rem_lable_btn = tk.Button(root, text="remove label", width=18)
    rem_lable_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + 3 * BTN_Y_STEP)
    rem_lable_btn.config(command=remove_label)

    # TODO: add winsounds

    root.mainloop()


if __name__ == '__main__':
    main()
