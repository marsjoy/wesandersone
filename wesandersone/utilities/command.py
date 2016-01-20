#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import subprocess
import sys
import time

import arrow

from wesandersone.config.config import Config

logger = logging.getLogger(__name__)

config = Config()


def run(cmd, get_stderr=False, env=None):
    try:
        start_time = time.time()
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        elapsed_time = time.time() - start_time
        logger.debug("[elapsed_time: %.2f] %s", elapsed_time, cmd)
        if sys.version_info > (3, 0) and not isinstance(out, int):
            output = str(out, 'utf-8')
        else:
            output = out
        if get_stderr:
            if sys.version_info > (3, 0) and not isinstance(err, int):
                error = str(err, 'utf-8')
            else:
                error = str(err)
            return output, error
        else:
            return output
    except Exception as e:
        logger.error("%s %s" % (cmd, str(e)))
        raise e

def remove(path, retrieve=True, force=True):
    command = "rm {option}{retrieve}{force} {path}" \
        .format(option='-' if retrieve or force else '',
                retrieve='r' if retrieve else '',
                force='f' if force else '',
                path=path)
    run(command)

def create_directories(path):
    command = "mkdir -p {path}".format(path=path)
    run(command)


def compress(path):
    command = "gzip -f {path}".format(path=path)
    run(command)


def decompress(path):
    command = "gunzip -f {path}".format(path=path)
    run(command)
