#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from abc import abstractmethod
from wesandersone.config.config import Config


class BaseWorkflow(metaclass=abc.ABCMeta):

    def __init__(self):
        self.config = Config()
        self.path_data = self.config.path.get('target_data', None)

    @abstractmethod
    def process(self):
        pass
