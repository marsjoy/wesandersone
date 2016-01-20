#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Navigates the web, uploads images, and retrieves extracted color information
import logging
import re

from selenium import webdriver
from selenium.webdriver.common.by import By

from wesandersone.workflows.base_workflow import BaseWorkflow

logger = logging.getLogger(__name__)


class ColorScraper(BaseWorkflow):

    def __init__(self, image=None, use_firefox=False):
        super(ColorScraper, self).__init__()
        self.use_firefox = use_firefox
        self.phantomjs_path = self.config.path.get('phantomjs_path', None)
        self.image = image
        self.driver = None
        self.colors = list()
        self.set_driver()

    def set_driver(self):
        if not self.use_firefox:
            driver = webdriver.PhantomJS(executable_path=self.phantomjs_path)
        else:
            driver = webdriver.Firefox()
        driver.set_window_size(480, 320)
        driver.get('http://labs.tineye.com/color/')
        self.driver = driver

    def process(self):
        self.upload_image()
        self.set_colors()
        self.quit()

    def upload_image(self):
        image_upload_button = self.driver.find_element(By.CSS_SELECTOR, '#upload-image')
        image_upload_button.send_keys(self.image)

    def set_colors(self):
        weight_regex = re.compile('(?<!\S)(\d*\.?\d+|\d{1,3}(,\d{3})*(\.\d+)?)(?!\S)')
        color_class_regex = re.compile("\(([^)]+)\)")
        theme_colors = self.driver.find_element(By.CSS_SELECTOR, '.color-range').find_elements(By.CSS_SELECTOR, '.info')
        for color in theme_colors:
            color_info = color.find_elements(By.TAG_NAME, 'span')
            color_details = dict()
            color_details['hex'] = color_info[0].text
            color_details['weight'] = weight_regex.search(color_info[1].text).group(1)
            color_details['color_name'] = color_info[2].text
            try:
                color_details['color_class'] = color_class_regex.search(color_info[3].text).group(1)
            except:
                color_details['color_class'] = color_info[3].text
            self.colors.append(color_details)

    def quit(self):
        self.driver.quit()
