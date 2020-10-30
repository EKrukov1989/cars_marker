"""Module for DatasetManager class."""

import os
import json
import pathlib
from PIL import Image


class DatasetManager():
    """Class for work with dataset folder.

    The only class that works with dataset folder and provide all operations:
    - search of unmarked image;
    - loading of unmarked images;
    - saving of marked image.
    """

    __images_dir = None
    __labels_dir = None
    __current_index = 0
    __stems = []

    def __init__(self, ds_folder_path):
        """."""
        self.__images_dir = ds_folder_path / 'images'
        self.__labels_dir = ds_folder_path / 'labels'
        names = os.listdir(self.__images_dir)
        self.__stems = list(map(lambda n: str(pathlib.Path(n).stem), names))

    def move_forward(self):
        """."""
        if self.__current_index == len(self.__stems) - 1:
            return False
        else:
            self.__current_index += 1
            return True

    def move_backward(self):
        """."""
        if self.__current_index == 0:
            return False
        else:
            self.__current_index -= 1
            return True

    def __get_index_of_first_unmarked(self):
        for k, stem in enumerate(self.__stems):
            label_path = self.__labels_dir / (stem + '.json')
            if not label_path.exists():
                return k
        return None

    def move_to_first_unmarked(self):
        """Find first unmarked image in dataset and set it as current."""
        index = self.__get_index_of_first_unmarked()
        if index is None or index == self.__current_index:
            return False
        else:
            self.__current_index = index
            return True

    def get_current(self):
        """."""
        stem = self.__stems[self.__current_index]
        image_path = self.__images_dir / (stem + '.jpg')
        label_path = self.__labels_dir / (stem + '.json')

        img = Image.open(str(image_path))
        img.load()

        label = None
        if label_path.exists():
            with open(label_path) as f:
                label = json.load(f)

        return image_path.name, img, label

    def save_marks_in_label(self, label):
        """Save marks in json-file."""
        stem = self.__stems[self.__current_index]
        label_path = self.__labels_dir / (stem + '.json')
        if label_path.exists():
            os.remove(label_path)
        with open(label_path, mode='w') as f:
            json.dump(label, f, indent=' '*4)

    def remove_label(self):
        """Remove label file for current_image."""
        stem = self.__stems[self.__current_index]
        label_path = self.__labels_dir / (stem + '.json')
        if label_path.exists():
            os.remove(label_path)
            return True
        else:
            return False
