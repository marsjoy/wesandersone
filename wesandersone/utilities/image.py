#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scipy.misc import imread


def image_to_numpy_ndarray(image=None):
    return imread(image)

def image_to_numpy_flattened_array(image=None):
    ndarray = imread(image)
    return ndarray.flatten()
