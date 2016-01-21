#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from abc import abstractmethod
from abc import ABCMeta
from wesandersone.config.config import Config


class BaseWorkflow():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.config = Config()
        self.path_data = self.config.path.get('target_data', None)

    @abstractmethod
    def process(self):
        pass
