#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scipy.misc import imread


def image_to_numpy_array(image=None):
    return imread(image)
