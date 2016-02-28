#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generates a model
import logging

import pandas as pd
from sklearn import cross_validation, metrics, preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

logger = logging.getLogger(__name__)


class Model(object):

    def __init__(
            self,
            raw_data=None,
            model_type=None,
            table_columns=None,
            feature_columns=None,
            target_column=None,
            target_names=None
    ):
        self.raw_data = raw_data
        self.table_columns = table_columns
        self.model_type = model_type if model_type else RandomForestClassifier
        self.feature_columns = feature_columns
        self.target_column = target_column
        self.target_names = target_names
        self.data_frame = None
        self.subsets = dict()
        self.correlation = None
        self.features = None
        self.target = None
        self.test = None
        self.train = None
        self.model = None
        self.predictions = None
        self.score = None
        self.classification_report = None
        self.metrics = dict()

    def set_data_frame(self, file=None, separator='\t',
                       table_columns=None, header=None, encoding='latin-1'):
        data_frame = pd.read_csv(file if file else self.raw_data,
                                 sep=separator,
                                 header=header,
                                 encoding=encoding)
        if header is None:
            data_frame.columns = table_columns if table_columns else self.table_columns
        self.data_frame = data_frame

    def set_correlation(self, data_frame=None):
        self.correlation = data_frame.corr() if data_frame else self.data_frame.corr()

    def set_subset(self, data_frame=None, filter=None, subset=str()):
        self.subsets[subset] = data_frame[filter] if data_frame else self.data_frame[filter]

    def set_features(self, data_frame=None, drop_column=None, features=list()):
        if drop_column:
            self.features = data_frame.drop(drop_column, axis=1) if data_frame else self.data_frame.drop(drop_column, axis=1)  # NOQA
        else:
            if features:
                self.features = data_frame[features] if data_frame else self.data_frame[features]
            else:
                self.features = data_frame[self.feature_columns] if data_frame else self.data_frame[self.feature_columns]  # NOQA

    def set_target(self, data_frame=None, drop_column=None, target=None):
        if drop_column:
            self.target = data_frame.drop(drop_column, axis=1) if data_frame else self.data_frame.drop(drop_column, axis=1)  # NOQA
        else:
            if target:
                self.target = data_frame[target] if data_frame else self.data_frame[target]
            else:
                self.target = data_frame[self.target_column] if data_frame else self.data_frame[self.target_column]  # NOQA

    def set_train_test(self, features=None, target=None, test_size=0.2, random_state=1):
        train_features, test_features, train_target, test_target = cross_validation.train_test_split(  # NOQA
            features if features else self.features,
            target if target else self.target,
            test_size=test_size,
            random_state=random_state)
        self.train = {'features': train_features, 'target': train_target}
        self.test = {'features': test_features, 'target': test_target}

    def set_fitted_model(self, model_type=None, train_features=None, train_target=None):
        model = model_type() if model_type else self.model_type()
        self.model = model.fit(train_features if train_features else self.train['features'],
                               train_target if train_target else self.train['target'])

    def set_predictions(self, model=None, test_features=None):
        if model:
            self.predictions = model.predict(test_features if test_features else self.test['features'])  # NOQA
        else:
            self.predictions = self.model.predict(test_features if test_features else self.test['features'])  # NOQA

    def set_score(self, model=None, test_features=None, test_target=None, complexity_value=10):
        self.score = cross_validation.cross_val_score(model if model else self.model,
                                                      test_features if test_features else self.test['features'],  # NOQA
                                                      test_target if test_target else self.test['target'],  # NOQA
                                                      cv=complexity_value)

    def set_classification_report(self, test_target=None, predictions=None, target_names=list()):
        self.classification_report = classification_report(test_target if test_target else self.test['target'],  # NOQA
                                                           predictions if predictions else self.predictions,  # NOQA
                                                           target_names=target_names if target_names else self.target_names)  # NOQA

    def set_metrics(self, test_target=None, predictions=None, positive_label=1):
        fpr, tpr, thresholds = metrics.roc_curve(test_target if test_target else self.test['target'],  # NOQA
                                                 predictions if predictions else self.predictions,
                                                 pos_label=positive_label)
        self.metrics['false_positive_rate'] = fpr
        self.metrics['true_positive_rate'] = tpr
        self.metrics['thresholds'] = thresholds
        self.metrics['roc_area_under_curve'] = metrics.auc(fpr, tpr)

    @staticmethod
    def get_data_frame(file=None,
                       separator='\t',
                       table_columns=None,
                       header=None,
                       encoding='latin-1'):
        data_frame = pd.read_csv(file, sep=separator, header=header, encoding=encoding)
        if header is None:
            data_frame.columns = table_columns
        return data_frame

    @staticmethod
    def get_correlation(data_frame=None):
        return data_frame.corr()

    @staticmethod
    def get_subset(data_frame=None, filter=None):
        return data_frame[filter]

    @staticmethod
    def export_to_csv(data_frame=None, file=None):
        data_frame.to_csv(file)

    @staticmethod
    def get_features(data_frame=None, drop_column=None, features=list()):
        if drop_column:
            return data_frame.drop(drop_column, axis=1)
        else:
            return data_frame[features]

    @staticmethod
    def get_target(data_frame=None, drop_column=None, target=None):
        if drop_column:
            return data_frame.drop(drop_column, axis=1)
        else:
            return data_frame[target]

    @staticmethod
    def get_train_test(features=None, target=None, test_size=0.2, random_state=1):
        train_features, test_features, train_target, test_target = cross_validation.train_test_split(  # NOQA
            features,
            target,
            test_size=test_size,
            random_state=random_state)
        return train_features, test_features, train_target, test_target

    @staticmethod
    def get_fitted_model(model_type=None, train_features=None, train_target=None):
        model = model_type()
        model.fit(train_features,
                  train_target)
        return model

    @staticmethod
    def get_predictions(model=None, test_features=None):
        return model.predict(test_features)

    @staticmethod
    def get_score(model=None, test_features=None, test_target=None, complexity_value=10):
        return cross_validation.cross_val_score(model,
                                                test_features,
                                                test_target,
                                                cv=complexity_value)

    @staticmethod
    def preprocess_scaler(features=None):
        scaler = preprocessing.StandardScaler()
        return scaler.fit_transform(features)

    @staticmethod
    def fit_model(model=None, train_features=None, train_target=None):
        return model.fit(train_features, train_target)

    @staticmethod
    def predict(model=None, sample=None):
        return model.predict(sample)

    @staticmethod
    def get_classification_report(test_target=None, predictions=None, target_names=list()):
        return classification_report(test_target, predictions, target_names=target_names)

    @staticmethod
    def get_metrics(test_target=None, predictions=None, positive_label=1):
        fpr, tpr, thresholds = metrics.roc_curve(test_target,
                                                 predictions=predictions,
                                                 pos_label=positive_label)
        roc_auc = metrics.auc(fpr, tpr)
        return {
            'false_positive_rate': fpr,
            'true_positive_rate': tpr,
            'thresholds': thresholds,
            'roc_area_under_curve': roc_auc
        }
