#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import os.path
import re
import time

import arrow
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from wesandersone.workflows.kuler_scraper.kuler_scraper import KulerScraper
from udemy.utils.command import compress, create_directories
from udemy.utils.writer import save_row
from udemy.workflow.base_etl_workflow import BaseETLWorkflow

logger = logging.getLogger(__name__)


class FBMembersWorkflow(BaseETLWorkflow):
    def __init__(self, table=None):
        super(FBMembersWorkflow, self).__init__(table=table)
        self.kuler_scraper = KulerScraper()
        self.file_name = "{table}.csv".format(table=table)
        self.base_dir = None
        self.file = None
        self.compressed_file = None
        self.driver = None

    # Scrape members data
    def extract(self):
        self._get_paths()
        self.get_members()
        self.quit()

    # Nothing to transform since data is extracted to fit for loading
    def transform(self):
        pass

    # Load data into redshift raw_data
    def load(self):
        if os.path.isfile(self.file):
            compress(self.file)
            pass
        else:
            logger.info("No data was loaded")

    # Sets up base directory and files
    def _get_paths(self):
        self.base_dir, self.file, self.compressed_file = \
            self.get_file_path()
        create_directories(self.base_dir)

    # Log in to facebook using credentials from conf file
    def login(self, config, path_data):
        email = config.get('email', None)
        password = config.get('password', None)

        driver = webdriver.PhantomJS(executable_path=path_data)
        driver.set_window_size(1600, 900)
        driver.get('http://www.facebook.com')
        email_field = driver.find_element_by_id('email')
        email_field.send_keys(email)
        password_field = driver.find_element_by_id('pass')
        password_field.send_keys(password)
        button = driver.find_element_by_id('loginbutton')
        button.click()
        self.driver = driver

    def seemore(self):
        try:
            time.sleep(3)
            button = self.driver.find_element_by_link_text('See More')
            button.click()
            time.sleep(3)
            return True
        except Exception as error:
            logger.debug(error)
            return False

    def _parse_member(self, container):
        d = container.text.split('\n')
        name = d[0]
        epoch = container.find_element_by_tag_name('abbr').get_attribute('data-utime')
        member_since = self.convert_epoch_to_timestamp_string(
            container.find_element_by_tag_name('abbr').get_attribute('data-utime'))

    @staticmethod
    def convert_epoch_to_timestamp_string(epoch):
        timestamp = arrow.get(epoch).format('YYYY-MM-DD HH:mm:ss')
        return timestamp

    def quit(self):
        self.driver.quit()
