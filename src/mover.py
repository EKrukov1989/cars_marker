"""Module for Mover class."""


class Mover():
    """Class for handling arrow events.

    This class binds events for Left, Right, up, Down buttons 
    and call callback accroding with complex intrinsic logic
    """

    __SLOW = 1
    __FAST = 5

    __root = None
    __callback = None

    __left_press_counter = 0
    __right_press_counter = 0
    __up_press_counter = 0
    __down_press_counter = 0

    def __init__(self, root, callback):
        """."""
        self.__root = root
        self.__callback = callback

        r = self.__root
        r.bind("<Left>", lambda e: self.__left_press())
        r.bind("<Right>", lambda e: self.__right_press())
        r.bind("<Down>", lambda e: self.__down_press())
        r.bind("<Up>", lambda e: self.__up_press())
        r.bind("<KeyRelease-Left>", lambda e: self.__left_release())
        r.bind("<KeyRelease-Right>", lambda e: self.__right_release())
        r.bind("<KeyRelease-Down>", lambda e: self.__down_release())
        r.bind("<KeyRelease-Up>", lambda e: self.__up_release())

    def __left_press(self):
        self.__left_press_counter += 1
        self.__move()

    def __right_press(self):
        self.__right_press_counter += 1
        self.__move()

    def __up_press(self):
        self.__up_press_counter += 1
        self.__move()

    def __down_press(self):
        self.__down_press_counter += 1
        self.__move()

    def __left_release(self):
        self.__left_press_counter = 0

    def __right_release(self):
        self.__right_press_counter = 0

    def __up_release(self):
        self.__up_press_counter = 0

    def __down_release(self):
        self.__down_press_counter = 0

    def __move(self):
        shift = self.__compute_current_shift()
        if shift[0] != 0 or shift[1] != 0:
            self.__callback(shift)

    def __compute_current_shift(self):
        def get_speed_in_certain_direction(counter):
            if counter == 0:
                return 0
            elif counter == 1:
                return self.__SLOW
            else:
                return self.__FAST

        left = get_speed_in_certain_direction(self.__left_press_counter)
        right = get_speed_in_certain_direction(self.__right_press_counter)
        up = get_speed_in_certain_direction(self.__up_press_counter)
        down = get_speed_in_certain_direction(self.__down_press_counter)
        return (right - left, up - down)
