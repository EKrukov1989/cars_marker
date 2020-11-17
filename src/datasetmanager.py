"""Module for DatasetManager class."""

import os
import json
import copy
import shutil
import pathlib
from PIL import Image
from mark import deserialize_mark
import utils


class DatasetManager():
    """Class for work with dataset folder.

    The only class that works with dataset folder and provide all operations:
    - search of unmarked image;
    - loading of unmarked images;
    - saving of marked image.
    """

    __FRAGM_WIDTH = 50

    __folder_dir = None
    __images_dir = None
    __labels_dir = None
    __current_index = 0
    __stems = []

    def __init__(self, ds_folder_path):
        """."""
        self.__folder_dir = ds_folder_path
        self.__images_dir = ds_folder_path / 'images'
        self.__labels_dir = ds_folder_path / 'labels'
        names = os.listdir(self.__images_dir)
        self.__stems = list(map(lambda n: str(pathlib.Path(n).stem), names))
        if self.__stems:
            self.__current_index = 0

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

    def __get_data(self, index):
        stem = self.__stems[index]
        image_path = self.__images_dir / (stem + '.jpg')
        label_path = self.__labels_dir / (stem + '.json')

        img = Image.open(str(image_path))
        img.load()

        label = None
        if label_path.exists():
            with open(label_path) as file:
                label = json.load(file)
        return image_path.name, img, label

    def get_current(self):
        """."""
        return self.__get_data(self.__current_index)

    def get_last(self, num=400):
        """Return n previous images and marks before current."""
        result = []
        if self.__current_index is None:
            return result
        begin_idx = max(self.__current_index + 1 - num, 0)
        end_idx = self.__current_index + 1
        prev_range = range(begin_idx, end_idx)
        for k in prev_range:
            result.append(self.__get_data(k))
        return result

    def save_marks_in_label(self, label):
        """Save marks in json-file."""
        stem = self.__stems[self.__current_index]
        label_path = self.__labels_dir / (stem + '.json')
        if label_path.exists():
            os.remove(label_path)
        with open(label_path, mode='w') as file:
            json.dump(label, file, indent=' '*4)

    def remove_label(self):
        """Remove label file for current_image."""
        stem = self.__stems[self.__current_index]
        label_path = self.__labels_dir / (stem + '.json')
        if label_path.exists():
            os.remove(label_path)
            return True
        else:
            return False

    def __create_stem(self, index):
        CHAR_NUM = 6
        str_index = str(index)
        return '0' * (CHAR_NUM - len(str_index)) + str_index

    def __is_rect_inside_img(self, img_size, rect):
        w, h = img_size
        return rect[0] >= 0 and rect[1] >= 0 and rect[2] < w and rect[3] < h

    def __save_fragment_dataset(self, fragments, marks):
        fr_ds_dir = self.__folder_dir / 'fragm_ds'
        fr_ds_images_dir = fr_ds_dir / 'images'
        fr_ds_labels_dir = fr_ds_dir / 'labels'
        if fr_ds_dir.exists():
            shutil.rmtree(fr_ds_dir)
        os.mkdir(fr_ds_dir)
        os.mkdir(fr_ds_images_dir)
        os.mkdir(fr_ds_labels_dir)

        for i, fragm in enumerate(fragments):
            mark = marks[i]
            stem = self.__create_stem(i)
            fragm_path = fr_ds_images_dir / (stem + '.png')
            label_path = fr_ds_labels_dir / (stem + '.json')
            label = {'filename':  stem + '.png', 'mark': mark.serialized()}
            with open(label_path, mode='w') as file:
                json.dump(label, file, indent=' '*4)
            fragm.save(fragm_path)

    def __has_matches(self, fragments, fragm):
        FW = self.__FRAGM_WIDTH
        INDENT = 5
        THRESHOLD = 0.99
        center_part = fragm.crop([INDENT, INDENT, FW - INDENT, FW - INDENT])
        for f in fragments:
            rects = utils.find_matches(f, center_part, THRESHOLD)
            if rects:
                return True
        return False

    def create_fragment_ds(self):
        """Create fragment dataset from current dataset.

        Result: cropped fragments with exactly one mark for each fragment.
        Fragment dataset will be saved in the folder of initial dataset.
        """
        print('Fragments dataset extraction started.')
        ds_fragments = []
        ds_marks = []
        label_names = os.listdir(self.__labels_dir)
        label_paths = list(map(lambda x: self.__labels_dir / x, label_names))
        for k, l_path in enumerate(label_paths):
            if k % int(round(len(label_paths) / 20)) == 0:
                print('. ', end='')
            if not l_path.exists():
                continue
            label = None
            with open(l_path) as file:
                label = json.load(file)
            marks = list(map(deserialize_mark, label['marks']))
            if not marks:
                continue
            FW = self.__FRAGM_WIDTH
            img_path = self.__images_dir / label['filename']
            img = Image.open(str(img_path))
            img.load()
            for m in marks:
                crop_rect = [m.cx - FW / 2, m.cy - FW / 2,
                             m.cx + FW / 2, m.cy + FW / 2]
                if not self.__is_rect_inside_img(img.size, crop_rect):
                    continue
                fragm = img.crop(crop_rect)
                if self.__has_matches(ds_fragments, fragm):
                    continue
                fr_mark = copy.deepcopy(m)
                fr_mark.cx, fr_mark.cy = FW / 2, FW / 2
                ds_fragments.append(fragm)
                ds_marks.append(fr_mark)
        print()  # for a new line after dot-bar

        if ds_fragments:
            self.__save_fragment_dataset(ds_fragments, ds_marks)
        print('Fragments dataset extraction finished.')
