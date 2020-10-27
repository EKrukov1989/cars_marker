"""Main module for cars-marker.

This module consists all logic of top level
"""

import tkinter as tk


def main():
    """Start application."""
    root = tk.Tk()

    root.wm_iconbitmap('src/images/window.ico')
    root.minsize(800, 600)
    root.state('zoomed')
    root.wm_title('cars_marker')

    launch_button = tk.Button(root, text="Hello", width=15)
    launch_button.pack()

    root.mainloop()


if __name__ == '__main__':
    main()
