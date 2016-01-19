#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse


class Arguments(object):
    def __init__(self, **args):
        description = args.get('description', None)
        formatter_class = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
        self.parser = argparse.ArgumentParser(formatter_class=formatter_class,
                                              description=description)

    def add_arguments(self, lists):
        for v in lists:
            self.add_argument(v)

    def add_argument(self, name, **args):
        if 'dest' not in args:
            args['dest'] = name
        if 'required' not in args:
            args['required'] = False
        if not name.startswith('-'):
            name = '-' + name
        self.parser.add_argument(name, **args)

    def get(self, name, default=None):
        args = vars(self.parser.parse_args())
        value = args[name] if name in args else None
        value = default if value is None else value
        return value
