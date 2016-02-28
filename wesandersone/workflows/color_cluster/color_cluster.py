#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Navigates the web, uploads images, and retrieves extracted color information
import logging

import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from wesandersone.workflows.base_workflow import BaseWorkflow

logger = logging.getLogger(__name__)


class ColorCluster(BaseWorkflow):

    def __init__(self, image=None, num_clusters=None):
        super(ColorCluster, self).__init__()
        self.image = image
        self.num_clusters = num_clusters
        self.colors = list()
        self.clusters = None
        self.dominant_colors = list()
        self.quantized_image = None

    def process(self):
        self.image = self.read_image()
        image_vector = self.reshape_image_to_vector(image=self.image)
        quantized_image_vector = self.imquantize_image(image=image_vector)
        self.quantized_image = self.reshape_vector_to_image(
            vector=quantized_image_vector, image=self.image)
        self.dominant_colors = self.find_cluster_centers()

    def read_image(self):
        image = cv2.imread(self.image)
        return self.convert_rgb_to_lab_color(image=image)

    def convert_rgb_to_lab_color(self, image=None):
        image_in_lab_color_space = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        return image_in_lab_color_space

    def reshape_image_to_vector(self, image=None):
        rows, columns, channels = image.shape
        reshaped_image = image.reshape((rows * columns, 3))
        return reshaped_image

    def reshape_vector_to_image(self, vector=None, image=None):
        rows, columns, channels = image.shape
        return vector.reshape((rows, columns, 3))

    def imquantize_image(self, image=None):
        self.clusters = MiniBatchKMeans(n_clusters=self.num_clusters, random_state=0)
        labels = self.clusters.fit_predict(image)
        quantize_image = self.clusters.cluster_centers_.astype('uint8')[labels]
        return quantize_image

    def convert_lab_color_to_rgb(self, image=None):
        image_in_rgb_color_space = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        return image_in_rgb_color_space

    def find_cluster_centers(self):
        return self.clusters.cluster_centers_

    def display_images(self):
        cv2.imshow("image", np.hstack([self.image, self.quantized_image]))
