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

    def __init__(self, purpose='train', num_inputs=None, num_ouputs=None, classes=None, class_lables=None):
        super(NeuralNetwork, self).__init__()
        self.purpose = purpose
        self.data_path = self.config.neural_net.get(self.purpose, None)
        self.file_name = 'neural_net'
        self.all_data = ClassificationDataSet(num_inputs,
                                              num_ouputs,
                                              nb_classes=classes,
                                              class_labels=class_lables)
        self.train = None
        self.test = None
        self.neural_network = None
        self.train_result = None
        self.test_result = None
        self.cross_validation_result = None

    def process(self):
        self.prepare_train_test()
        self.build_network()
        trainer = self.train_network(dataset=self.train)
        self.score_train_test(trainer=trainer)
        self.cross_validate(dataset=self.all_data)

    def add_sample(self, correlogram_matrix=None, target=None, sample_path=None):
        self.all_data.addSample(correlogram_matrix, target)
        logger.info('sample added from {sample_path}'.format(sample_path=sample_path))

    def prepare_train_test(self):
        self.test, self.train = self.all_data.splitWithProportion(0.25)

    def build_network(self):
        self.neural_network = buildNetwork(self.train.indim, 7, self.train.outdim, outclass=SoftmaxLayer) # feed forward network

    def train_network(self, dataset=None):
        starter_trainer = BackpropTrainer(self.neural_network, dataset=dataset, momentum=0.1, verbose=True, weightdecay=0.01)
        starter_trainer.trainUntilConvergence(validationProportion=0.25,  maxEpochs=100)
        return starter_trainer

    def score_train_test(self, trainer=None):
        self.test_result = percentError(trainer.testOnClassData(dataset=self.test), self.test['class'])
        logger.info('test error result: {result}'.format(result=self.test_result))
        self.train_result = percentError(trainer.testOnClassData(dataset=self.train), self.train['class'] )
        logger.info('train error result: {result}'.format(result=self.train_result))

    def cross_validate(self, dataset=None):
        trainer = BackpropTrainer(self.neural_network, dataset=dataset, momentum=0.1, verbose=True, weightdecay=0.01)
        validator = CrossValidator(trainer=trainer, dataset=dataset, n_folds=10)
        mean_validation_result = validator.validate()
        self.cross_validation_result = mean_validation_result
        logger.info('cross val result: {result}'.format(result=self.cross_validation_result))

    @staticmethod
    def save_network_to_xml(net=None, file_name=None):
        NetworkWriter.writeToFile(net, file_name)

    @staticmethod
    def read_network_from_xml(file_name=None):
        return NetworkReader.readFrom(file_name)
