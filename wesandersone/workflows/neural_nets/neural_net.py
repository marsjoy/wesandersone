#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create a neural network from film stills
import ast
import csv
import logging

import numpy as np

from pybrain.datasets import ClassificationDataSet
from pybrain.structure import SoftmaxLayer
from pybrain.structure.modules import SoftmaxLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.validation import CrossValidator
from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.utilities import percentError
from sklearn.utils import shuffle
from wesandersone.utilities import command
from wesandersone.utilities.image import image_to_numpy_ndarray
from wesandersone.workflows.base_workflow import BaseWorkflow

logger = logging.getLogger(__name__)


class NeuralNetwork(BaseWorkflow):

    def __init__(self):
        super(NeuralNetwork, self).__init__(workflow_name='neural_net')
        self.purpose = purpose
        self.data_path = self.config.neural_net.get(self.purpose, None)
        self.file_name = 'neural_net'
        self.neural_net_classifications_path = '{file}_.csv'.format(file=self.file)
        self.all_data = ClassificationDataSet(3, 1, nb_classes=6,
                                              class_labels=['christopher_nolan',
                                                            'coen_brothers',
                                                            'david_lynch',
                                                            'francis_ford_coppola',
                                                            'spike_jonze',
                                                            'wes_anderson'
                                                            ])
        self.train = None
        self.test = None
        self.neural_net = None
        self.train_result = None
        self.test_result = None
        self.cross_validation_result = None
        self.base_dir = str()
        self.file = str()
        self.compressed_file = str()
        self.set_up()

    def set_up(self):
        self.base_dir, self.file, self.compressed_file = self.get_file_path()
        command.create_directories(self.base_dir)

    def process(self):
        self.add_samples()
        self.prepare_train_test()
        self.build_network()
        trainer = self.train_network(dataset=self.train)
        self.score_train_test(trainer=trainer)
        self.cross_validate(dataset=self.all_data)
        self.save_network_to_xml(net=self.neural_net, file_name=self.file_name)

    def add_samples(self):
        target_conversions = {1:0, 2:1, 3:2, 4:3, 5:5, 6:5}
        with open(self.data_path) as net_data:
            reader = csv.reader(net_data, delimiter=',', quotechar='"')
            for line in reader:
                image, encoding = line
                rgbs = ast.literal_eval(image)
                for rgb in rgbs:
                    target = target_conversions[int(encoding)]
                    self.all_data.addSample(rgb, target)

    def prepare_train_test(self):
        test_data, train_data = alldata.splitWithProportion(0.25)
        self.test = test_data._convertToOneOfMany()
        self.train = train_data._convertToOneOfMany()

    def build_network(self):
        self.neural_network = buildNetwork(self.train.indim, 7, self.train.outdim, outclass=SoftmaxLayer) # feed forward network

    def train_network(self, dataset=None):
        starter_trainer = BackpropTrainer(self.neural_network, dataset=dataset, momentum=0.1, verbose=True, weightdecay=0.01)
        trainer = starter_trainer.trainUntilConvergence(validationProportion=0.25)
        return trainer

    def score_train_test(self, trainer=None):
        self.train_result = percentError(trainer.testOnClassData(), self.train['class'] )
        self.test_result = percentError(trainer.testOnClassData(dataset=self.test), self.test['class'])

    def cross_validate(self, dataset=None):
        trainer = BackpropTrainer(self.neural_network, dataset=dataset, momentum=0.1, verbose=True, weightdecay=0.01)
        validator = CrossValidator(trainer=trainer, dataset=dataset, n_folds=10)
        mean_validation_result = validator.validate()
        self.cross_validation_result = mean_validation_result

    @staticmethod
    def save_network_to_xml(self, net=None, file_name=None):
        NetworkWriter.writeToFile(net, file_name)

    @staticmethod
    def read_network_from_xml(self, file_name=None):
        return NetworkReader.readFrom(file_name)
