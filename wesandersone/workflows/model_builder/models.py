#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

MODELS = {
    'classification': {
        'RandomForestClassifier': RandomForestClassifier,
        'SVC': SVC,
        'KNeighborsClassifier': KNeighborsClassifier,
        'LogisticRegression': LogisticRegression,
        'GaussianNB': GaussianNB,
    },
    'regression': {
    }

}


def get_models():
    global MODELS
    return MODELS
