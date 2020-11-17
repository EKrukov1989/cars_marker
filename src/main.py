"""Main module for cars-marker.

This module consists all logic of top level
"""

import tkinter as tk
import pathlib

from datasetmanager import DatasetManager
from markmanager import MarkManager

TEST_DS_PATH = pathlib.Path('src/cars_ds_test')
DS_PATH = pathlib.Path('D:/my_cars_ds')
BTN_INDENT = 750
BTN_Y_INDENT = 20
BTN_Y_STEP = 40


def main():
    """Start application."""
    root = tk.Tk()
    root.wm_title('cars_marker')
    root.wm_iconbitmap('src/images/window.ico')
    root.geometry('1200x800')
    root.resizable(width=False, height=False)

    ds_m = DatasetManager(DS_PATH)
    mark_m = MarkManager(root)
    mark_m.reset_image(ds_m.get_last())

    def move_to_prev_img():
        if ds_m.move_backward():
            mark_m.reset_image(ds_m.get_last())
    prev_img_btn = tk.Button(root, text="prev image (Backspace)", width=20)
    prev_img_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT)
    prev_img_btn.config(command=move_to_prev_img)
    root.bind("<BackSpace>", lambda ev: move_to_prev_img())

    def move_to_next_img():
        if ds_m.move_forward():
            mark_m.reset_image(ds_m.get_last())
    next_img_btn = tk.Button(root, text="next image (Enter)", width=20)
    next_img_btn.place(x=(BTN_INDENT + 180), y=BTN_Y_INDENT)
    next_img_btn.config(command=move_to_next_img)
    root.bind("<Return>", lambda ev: move_to_next_img())

    def move_to_first_unmarked_img():
        if ds_m.move_to_first_unmarked():
            mark_m.reset_image(ds_m.get_last())
    first_umm_btn = tk.Button(root, width=28)
    first_umm_btn['text'] = 'move to first unmarked image'
    first_umm_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + BTN_Y_STEP)
    first_umm_btn.config(command=move_to_first_unmarked_img)

    def save_label():
        marks = mark_m.serialize_marks()
        ds_m.save_marks_in_label(marks)
        mark_m.reset_image(ds_m.get_last())
    save_btn = tk.Button(root, text="save marks in label (S)", width=18)
    save_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + 2 * BTN_Y_STEP)
    save_btn.config(command=save_label)
    root.bind("<Key-s>", lambda ev: save_label())

    def remove_label():
        if ds_m.remove_label():
            mark_m.reset_image(ds_m.get_last())
    rem_label_btn = tk.Button(root, text="remove label", width=18)
    rem_label_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + 3 * BTN_Y_STEP)
    rem_label_btn.config(command=remove_label)

    def create_ds():
        ds_m.create_fragment_ds()
    create_ds_btn = tk.Button(root, text="Create fragment dataset", width=28)
    create_ds_btn.place(x=BTN_INDENT, y=BTN_Y_INDENT + 4 * BTN_Y_STEP)
    create_ds_btn.config(command=create_ds)

    legend_label = tk.Label(root, text=mark_m.get_legend())
    legend_label.config(justify=tk.LEFT)
    legend_label.place(x=BTN_INDENT, y=500)

    root.mainloop()


if __name__ == '__main__':
    main()
