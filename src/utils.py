"""Common geometrical functions."""

import math
import numpy as np
import cv2 as cv


def create_rotation_xf(rotation):
    """Make transform matrix for ratation around zero-point."""
    a = math.radians(rotation)
    return np.array([[math.cos(a), -math.sin(a), 0],
                     [math.sin(a),  math.cos(a), 0],
                     [0, 0, 1]])


def create_scale_xf(s):
    """Make transform matrix for scale."""
    return np.array([[s, 0, 0],
                     [0, s, 0],
                     [0, 0, s]])


def create_translation_xf(translation):
    """Make transform matrix for translation."""
    tx, ty = translation
    return np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0,  1]])


def create_rotation_around_center_xf(rotation, center_of_rotation=None):
    """Make transform matrix for rotation around certain center."""
    if center_of_rotation:
        cx, cy = center_of_rotation
        tr_fwd = create_translation_xf((-cx, -cy))
        rot = create_rotation_xf(rotation)
        tr_bwd = create_translation_xf((cx, cy))
        return np.matmul(np.matmul(tr_bwd, rot), tr_fwd)
    else:
        return create_rotation_xf(rotation)


def combine_xfs(xf_list):
    """."""
    res = np.identity(3, dtype=np.float32)
    for xf in xf_list:
        res = np.matmul(res, xf)
    return res


def apply_xf(points, xf):
    """."""
    # points - list of tuples, xf - np.array(3x3), retval - list of tuples
    res = []
    for pt in points:
        new_pt = np.matmul(xf, np.array([pt[0], pt[1], 1]))
        res.append((new_pt[0], new_pt[1]))
    return res

def find_matches(img, fragm, threshold):
    """Find matches of fragm in bi image.
    
    Return coincedences as list of rects.
    """
    fr_rgb = np.array(fragm, dtype=np.uint8)
    img_rgb = np.array(img, dtype=np.uint8)
    fr_grey = cv.cvtColor(fr_rgb, cv.COLOR_RGB2GRAY)
    img_grey = cv.cvtColor(img_rgb, cv.COLOR_RGB2GRAY)
    res = cv.matchTemplate(img_grey, fr_grey, cv.TM_CCOEFF_NORMED)
    h, w = fr_grey.shape
    locs = np.where(res >= threshold)
    rects = []
    for pt in zip(*locs):
        rect = [pt[1], pt[0], pt[1] + w, pt[0] + h]
        rects.append(rect)
    return rects
