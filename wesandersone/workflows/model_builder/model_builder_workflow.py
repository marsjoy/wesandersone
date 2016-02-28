#!/usr/bin/env python
# -*- coding: utf-8 -*-
# For building a scikitlearn model
import logging

import arrow

from wesandersone.utils import command
from wesandersone.utils.writer import save_row, save_rows
from wesandersone.workflows.base_etl_workflow import BaseETLWorkflow
from wesandersone.workflows.base_workflow import Arguments
from wesandersone.workflows.modeling_builder.model import Model
from wesandersone.workflows.modeling_builder.models import get_models
from wesandersone.workflows.modeling_builder.configuration import get_configuration

logger = logging.getLogger(__name__)

COPY_OPTIONS = "CSV gzip maxerror as 0 ACCEPTINVCHARS " \
               "dateformat 'auto' timeformat 'auto' null as 'Null'"


class ModelBuilderWorkflow(BaseETLWorkflow):
    def __init__(self,
                 sample=None,
                 separator=None,
                 header=None,
                 model_name=None,
                 model_type=None,
                 model_version=1.0,
                 table_columns=None,
                 feature_columns=None,
                 target_column=None,
                 start_date=None):
        super(ModelBuilderWorkflow, self).__init__(workflow_name='model_builder')
        self.sample = '{path}/{sample}'.format(path=self.config.path.get('source_data', None),
                                               sample=sample)
        self.separator = separator
        self.header = header
        self.model_type = model_type
        self.model_name = model_name
        self.model_version = model_version
        self.file_name = self.table
        self.file = None
        self.table_columns = table_columns
        self.feature_columns = feature_columns
        self.target_column = target_column
        self.model = None
        self.get_paths()

    def get_paths(self, query_name=None):
        base_dir, self.file, raw_file, self.compressed_file = self.get_file_path()
        command.create_directories(base_dir)
        return base_dir

    def extract(self):
        pass

    def transform(self):
        self.model = Model(raw_data=self.sample,
                           table_columns=table_columns,
                           feature_columns=self.feature_columns,
                           target_column=self.target_column,
                           model_type=self.model_type)
        self.model.set_data_frame(separator=self.separator, header=self.header)
        self.model.set_features()
        self.model.set_target()
        self.model.set_train_test()
        self.model.set_fitted_model()
        self.model.set_predictions()
        self.model.set_score()
        self.model.set_classification_report()
        self.model.set_metrics()
        logger.info(self.model.score)
        logger.info(self.model.metrics)
        logger.info(self.model.classification_report)
        feature_lists = self.format_features_list()
        samples_and_predictions = [i[0] + [i[1],
                                           model_version] for i in zip(feature_lists,
                                                                       self.model.predictions.tolist())]  # NOQA
        save_rows(file='{file}_{model_name}_predictions.csv'.format(file=self.file,
                                                                    model_name=self.model_name),
                  rows=samples_and_predictions)
        save_row(file='{file}_{model_name}_'
                      'scores.csv'.format(file=self.file, model_name=self.model_name),
                 row=self.model.score.tolist() + [model_version])
        save_rows(file='{file}_{model_name}_classification_report.csv'.format(file=self.file,
                                                                              model_name=self.model_name),  # NOQA
                  rows=[i + [model_version] for i in self.format_classification_report()])
        save_rows(file='{file}_{model_name}_metrics_report.csv'.format(file=self.file,
                                                                       model_name=self.model_name),
                  rows=[i + [model_version] for i in [self.model.metrics['false_positive_rate'],
                                                      self.model.metrics['true_positive_rate'],
                                                      self.model.metrics['thresholds'],
                                                      [self.model.metrics['roc_area_under_curve']]]])  # NOQA

    def format_features_list(self):
        feature_lists = list()
        for i in range(len(self.model.test['features'])):
            feature_list = list()
            feature_list.append(self.model.test['features'].iloc[i].tolist())
            feature_lists.append(feature_list)
        return [feature[0] for feature in feature_lists]

    def format_classification_report(self):
        split_model = self.model.classification_report.split('\n')
        report = [
            ['class'] + split_model[0].split(),
            [i.split() for i in split_model][2],
            [i.split() for i in split_model][3],
            [''.join([i.split() for i in split_model][5][0:3])] +
            [i.split() for i in split_model][5][3:]
        ]
        return report

    def format_metrics(self):
        self.model.metrics['false_positive_rate'] = self.model.metrics['false_positive_rate'].tolist()  # NOQA
        self.model.metrics['true_positive_rate'] = self.model.metrics['true_positive_rate'].tolist()  # NOQA
        self.model.metrics['thresholds'] = self.model.metrics['thresholds'].tolist()

    def load(self):
        pass

if __name__ == '__main__':

    args = Arguments(description='this script is for building scikit learn models')
    args.add_argument(
        '--table_columns',
        help="the names of the table columns, passed in order of schema, as a "
             "space-separated list of quoted names "
             "(e.g., 'review' 'reviewer')",
        nargs='*'
    )
    args.add_argument(
        '--target_column',
        help='the name of the target column',
        nargs='*'
    )
    args.add_argument(
        '--date',
        help='target date in YYYY-MM-DD format (i.e. 2015-07-17), defaults to today'
    )
    args.add_argument(
        '--feature_columns',
        help="names of feature columns, passed as a space-separated list of quoted names "
             "(e.g., 'review' 'reviewer')",
        nargs='*'
    )
    args.add_argument(
        '--samples',
        help='names of samples',
        nargs='*'
    )
    args.add_argument(
        '--model_types',
        help="names of sklearn models, passed as a space-separated list of quoted names "
             "(e.g., 'svc' 'SVM')",
        nargs='*'
    )
    args.add_argument(
        '--model_version',
        help="version of current model",
    )
    args.add_argument(
        '--separator',
        help="separator",
    )
    args.add_argument(
        '--header',
        help="header",
    )
    args.add_argument(
        '--task',
        help="task: classification or regression",
        choices=['regression', 'classification']
    )
    configuration = get_configuration()
    models = get_models()
    user_date = args.get('--date', arrow.now().replace(days=-1).format('YYYY-MM-DD'))
    target_column = args.get('--target_column', configuration['target_column'])
    table_columns = args.get('--table_columns', configuration['table_columns'])
    task = args.get('--task', configuration['task'])
    model_types = args.get('--model_types',
                           models['classification'] if task == 'classification' else models['regression'])  # NOQA
    model_version = args.get('--model_version', configuration['model_version'])
    samples = args.get('--samples', configuration['samples'])

    if samples:
        for sample in samples:
            feature_columns = args.get('--feature_columns', samples[sample]['feature_columns'])
            separator = args.get('--separator', samples[sample]['separator'])
            header = args.get('--header', samples[sample]['header'])
            datestamp = arrow.get(user_date).format('YYYY-MM-DD')

            for model_type in model_types:
                workflow = ModelBuilderWorkflow(sample=sample,
                                                separator=separator,
                                                header=header,
                                                table_columns=table_columns,
                                                feature_columns=feature_columns,
                                                target_column=target_column,
                                                model_type=model_types[model_type],
                                                model_name=model_type,
                                                model_version=model_version,
                                                start_date=datestamp)
                workflow.process()
