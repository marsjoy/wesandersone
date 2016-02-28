#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Extracts film still properties for use in neural net
import logging
import os

import numpy as np

from neural_net import NeuralNetwork
from wesandersone.utilities import command
from wesandersone.utilities.arguments import Arguments
from wesandersone.utilities.image import image_to_numpy_ndarray
from wesandersone.utilities.writer import save_row
from wesandersone.workflows.base_etl_workflow import BaseETLWorkflow
from wesandersone.utilities.image import auto_correlogram

logger = logging.getLogger(__name__)


class NeuralNetWorkflow(BaseETLWorkflow):

    def __init__(self, directors=None):
        super(NeuralNetWorkflow, self).__init__(workflow_name='neural_net_workflow')
        self.image_path = self.config.path.get('source_data', None)
        self.file_name = 'neural_net_workflow_scores.csv'
        self.directors = directors
        self.encoding = None
        self.base_dir = str()
        self.file = str()
        self.compressed_file = str()
        self.set_up()
        self.neural_net = NeuralNetwork(num_inputs=256,
                                        num_ouputs=5,
                                        classes=5,
                                        class_lables=['christopher_nolan',
                                                      'coen_brothers',
                                                      'david_lynch',
                                                      'spike_jonze',
                                                      'wes_anderson'])

    def set_up(self):
        self.base_dir, self.file, self.compressed_file = self.get_file_path()
        command.create_directories(self.base_dir)

    def extract(self):
        for director in directors:
            self.encoding = directors[director]
            movies = [x[1] for x in os.walk(
                '{image_path}/{director}/'.format(image_path=self.image_path,
                                                  director=director),
                topdown=False)][-1]
            for movie in movies:
                film_stills_path = '{image_path}/' \
                                   '{director}/' \
                                   '{movie}/'.format(image_path=self.image_path,
                                                     director=director,
                                                     movie=movie)
                self.extract_film_stills(film_stills_path=film_stills_path, movie=movie, director=director)

    def extract_film_stills(self, film_stills_path=None, movie=None, director=None):
        for film_still in os.listdir(film_stills_path):
            try:
                film_still_path = '{film_stills_path}' \
                                  '{film_still}'.format(film_stills_path=film_stills_path,
                                                        film_still=film_still)
                logger.info(film_still_path)
                self.add_film_still_sample(image=film_still_path, movie=movie, director=director)
            except Exception as error:
                logger.error(error)

    def add_film_still_sample(self, image=None, movie=None, director=None):
        image_ndarray = image_to_numpy_ndarray(image=image)
        correlogram_matrix = auto_correlogram(image_ndarray)
        len(correlogram_matrix)
        self.neural_net.add_sample(correlogram_matrix=correlogram_matrix,
                                   target=self.encoding,
                                   sample_path=image)

    def transform(self):
        self.neural_net.process()
        save_network_to_xml(net=None, file_name=None)

    def load(self):
        save_row(file=self.file,
                 row=[self.neural_net.cross_validation_result,
                      self.neural_net.test_result,
                      self.neural_net.train_result])


if __name__ == '__main__':

    args = Arguments(description='a script to extract properties from '
                                 'film stills for use in a neural network. '
                                 'You can pass a director name. '
                                 'If no director name '
                                 'is passed, the script defaults to all directors.')

    directors = {'christopher_nolan': 0,
                 'coen_brothers': 1,
                 'david_lynch': 2,
                 'spike_jonze': 3,
                 'wes_anderson': 4,}

    workflow = NeuralNetWorkflow(directors=directors)

    workflow.process()
