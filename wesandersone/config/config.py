#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from logging import config
from os import environ

from .constants import (CFG_FILE, MYSQL_CFG_FILE)

try:
    from configparser import ConfigParser
except Exception:
    try:
        from six.moves.configparser import ConfigParser
    except Exception:
        from ConfigParser import ConfigParser


def get_config_files():
    if 'WESANDERSONE_HOME' not in environ:
        raise Exception('You have to set WESANDERSONE_HOME environment variable.')

    wesandersone_home = environ['WESANDERSONE_HOME']

    conf_dir = 'conf/'
    config_path = wesandersone_home + conf_dir + CFG_FILE
    mysql_config_path = wesandersone_home + conf_dir + MYSQL_CFG_FILE
    config_files = [config_path, mysql_config_path]
    return config_files


class Config(object):
    _isInstantiated = False
    _root_mode = None

    def __init__(self):
        self._root_config = ConfigParser()
        self._root_config.read(get_config_files())
        dictionary = {}
        for section in self._root_config.sections():
            dictionary[section] = {}
            for option in self._root_config.options(section):
                dictionary[section][option] = self._root_config.get(section, option)

        self.__dict__ = dictionary

    def dict(self):
        return self.__dict__

    @staticmethod
    def write(path, section, key, value):
        config = ConfigParser()
        config.read(path)
        config[section][key] = value
        with open(path, 'w') as configfile:
            config.write(configfile)


logging_properties = Config().path.get('logging', None)
config.fileConfig(logging_properties, disable_existing_loggers=False)