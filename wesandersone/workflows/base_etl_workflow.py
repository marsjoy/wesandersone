#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import traceback
from abc import abstractmethod

from wesandersone.workflows.base_workflow import BaseWorkflow

logger = logging.getLogger(__name__)


class BaseETLWorkflow(BaseWorkflow):
    def __init__(self, table, start_date, end_date):
        super(BaseETLWorkflow, self).__init__()
        self.path_data = self.config.path.get('target_data', None)
        self.table = table
        self.start_date = start_date
        self.end_date = end_date
        self.file_name = None

    def process(self):
        try:
            self.extract()
            self.verify_extract()
            self.transform()
            self.verify_transform()
            self.load()
            self.verify_load()
        except Exception as e:
            logger.error(e)

    @abstractmethod
    def load(self):
        pass

    def verify_load(self):
        pass

    @abstractmethod
    def extract(self):
        pass

    def verify_extract(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    def verify_transform(self):
        pass

    def get_file_path(self):
        if self.file_name is None:
            raise Exception('Must be set file_name')

        base_dir = "{path_data}/{table}".format(path_data=self.path_data,
                                                table=self.table)
        file = "{base_dir}/{file_name}".format(base_dir=base_dir, file_name=self.file_name)
        compressed_file = "{base_dir}/{file_name}.gz".format(base_dir=base_dir,
                                                             file_name=self.file_name)

        return base_dir, file, compressed_file
