#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv


def save_row(file=None, row=None, field_names=None):
    if isinstance(row, dict) and not field_names:
        raise ValueError("You must provide field names")
    with open(file, 'a', encoding='utf-8') as f:
        if isinstance(row, dict):
            writer = csv.DictWriter(f, fieldnames=field_names, quoting=csv.QUOTE_ALL)
        else:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(row)


def save_rows(file=None, rows=None, field_names=None):
    if len(rows) == 0:
        return
    if isinstance(rows[0], dict) and not field_names:
        raise ValueError("You must provide field names")
    with open(file, 'a', encoding='utf-8') as f:
        if isinstance(rows[0], dict):
            writer = csv.DictWriter(f, fieldnames=field_names, quoting=csv.QUOTE_ALL)
        else:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
