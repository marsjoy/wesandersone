#!/usr/bin/env python
# -*- coding: utf-8 -*-

CONFIGURATION = {

    'task': 'classification',

    'model_version': 1.0,

    'table_columns': [

    ],

    'target_column': '',

    'target_names': None,

    'samples': {

        'sample_.csv': {

            'separator': ',',

            'header': 0,

            'feature_columns': [

            ]
        },
    },

}


def get_configuration():
    global CONFIGURATION
    return CONFIGURATION
