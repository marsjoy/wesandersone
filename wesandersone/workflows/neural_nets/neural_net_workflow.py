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

logger = logging.getLogger(__name__)


class NeuralNetWorkflow(BaseETLWorkflow):

    def __init__(self,
                 movies=None,
                 director=None,
                 encoding=None):
        super(NeuralNetWorkflow, self).__init__(workflow_name='neural_net_workflow')
        self.movies = movies
        self.director = director
        self.encoding = encoding
        self.image_path = self.config.path.get('source_data', None)
        self.file_name = 'extracted_film_still_properties'
        self.base_dir = str()
        self.file = str()
        self.compressed_file = str()
        self.set_up()
        self.extracted_film_still_properties_path = '{file}_' \
                                                    '{director}.csv'.format(file=self.file,
                                                                            director=director)

    def set_up(self):
        self.base_dir, self.file, self.compressed_file = self.get_file_path()
        command.create_directories(self.base_dir)

    def extract(self):
        for movie in movies:
            film_stills_path = '{image_path}/' \
                               '{director}/' \
                               '{movie}/'.format(image_path=self.image_path,
                                                 director=self.director,
                                                 movie=movie)
            for film_still in os.listdir(film_stills_path):
                try:
                    film_still_path = '{film_stills_path}' \
                                      '{film_still}'.format(film_stills_path=film_stills_path,
                                                            film_still=film_still)
                    logger.info(film_still_path)
                    self.save_film_still_with_labels(image=film_still_path)
                except Exception as error:
                    logger.error(error)

    def save_film_still_with_labels(self, image=None):
        image_ndarray = image_to_numpy_ndarray(image=image)
        converted_image_ndarray = np.divide(image_ndarray, 255.0)
        reshaped = np.vstack(converted_image_ndarray).tolist()
        save_row(file=self.extracted_film_still_properties_path,
                 row=[reshaped, self.encoding])

    def transform(self):
        pass

    def load(self):
        pass

if __name__ == '__main__':

    args = Arguments(description='a script to extract properties from '
                                 'film stills for use in a neural network. '
                                 'You can pass a director name. '
                                 'If no director name '
                                 'is passed, the script defaults to all directors.')

    args.add_argument(
        '--director',
        help='a single director name',
    )

    director = args.get('--director', None)

    if not director:
        directors = {'christopher_nolan': 1,
                     'coen_brothers': 2,
                     'david_lynch': 3,
                     'francis_ford_coppola': 4,
                     'spike_jonze': 5,
                     'wes_anderson': 6,}
    else:
        directors = [director]

    image_path = '/Users/marswilliams/wesandersone/images/'

    for director in directors:
        movies = [x[1] for x in os.walk(
            '{image_path}/{director}/'.format(image_path=image_path,
                                              director=director),
            topdown=False)][-1]
        workflow = NeuralNetWorkflow(movies=movies,
                                     director=director,
                                     encoding=directors[director])

        workflow.process()
