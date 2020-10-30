"""Module for Mover class."""


class Rotator():
    """Class for handling events for mark rotation."""

    __SLOW = 1
    __FAST = 5

    __root = None
    __callback = None

    __forw_press_counter = 0
    __back_press_counter = 0

    def __init__(self, root, callback):
        """."""
        self.__root = root
        self.__callback = callback

        r = self.__root
        r.bind("<Key-w>", lambda e: self.__forw_press())
        r.bind("<Key-q>", lambda e: self.__back_press())
        r.bind("<KeyRelease-w>", lambda e: self.__forw_release())
        r.bind("<KeyRelease-q>", lambda e: self.__back_release())

    def __forw_press(self):
        self.__forw_press_counter += 1
        self.__rotate()

    def __back_press(self):
        self.__back_press_counter += 1
        self.__rotate()

    def __forw_release(self):
        self.__forw_press_counter = 0

    def __back_release(self):
        self.__back_press_counter = 0

    def __rotate(self):
        rot = self.__compute_current_rotation()
        if rot != 0:
            self.__callback(rot)

    def __compute_current_rotation(self):
        def get_spped_in_certain_direction(counter):
            if counter == 0:
                return 0
            elif counter == 1:
                return self.__SLOW
            else:
                return self.__FAST

        forw = get_spped_in_certain_direction(self.__forw_press_counter)
        back = get_spped_in_certain_direction(self.__back_press_counter)
        return forw - back
