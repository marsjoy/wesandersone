#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.colors as colors
from colormath.color_conversions import convert_color
from colormath.color_objects import HSLColor, HSVColor, LabColor, sRGBColor


def hex_to_rgb(hex=None):
    return colors.hex2color(hex)

def rgb_to_hex(rgb=None):
    return colors.rgb2hex(rgb)

def lab_color_properties_from_rgb(rgb=None):
    lab = lab_from_srgb(rgb=rgb)
    return lab_color_properties(lab=lab)

def lab_from_rgb(rgb=None):
    r, g, b = rgb
    srgb = sRGBColor(r, g, b)
    return convert_color(srgb, LabColor)

def lab_color_properties(lab=None):
    return (lab.lab_l, lab.lab_a, lab.lab_b, lab.observer, lab.illuminant)

def hsv_from_lab(lab=None):
    return convert_color(lab, HSVColor)

def hsl_from_lab(lab=None):
    return convert_color(lab, HSLColor)
