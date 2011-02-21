#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Settings.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import copy
import glob
import random
import logging


class ConfigError(Exception):
    pass


class Settings(object):
    logger_name = ''
    settings_name = 'generic'
    settings_filenames = None
    globals = {}

    def __init__(self):
        self.logger = logging.getLogger(self.logger_name)
        self.random = random.Random()
        self.reload()

    def _load(self):
        self.logger.info("Loading %s settings...", self.settings_name)
        try:
            for each_file in sorted(glob.glob(self.settings_filenames)):
                execfile(each_file, self.globals, self.__dict__)
        except Exception as e:
            message = ("%s settings file '%s' is corrupted"
                       % (self.settings_name, each_file))
            logging.getLogger(self.logger_name).exception(message)
            raise ConfigError(message, e)

    def _seed(self):
        if self.get('RANDOM_SEED') is None:
            self.set('RANDOM_SEED', random.randint(0, 999999999))
        seed = self.get('RANDOM_SEED')
        self.random.seed(seed)
        self.logger.info('Using %i as random seed for %s',
                         seed, self.settings_name)

    def get(self, attr, default=None):
        try:
            return getattr(self, attr)
        except AttributeError:
            return default

    def set(self, attr, value):
        setattr(self, attr, value)

    def reload(self, reseed=True):
        # preserve logger and current random generator
        self.__dict__ = {'logger': self.logger,
                         'random': self.random}
        # copy default settings to instance
        # (it will be available in settings files)
        defaults = dict((key, copy.deepcopy(value))
                        for key, value in self.__class__.__dict__.items()
                        if isinstance(key, str) and key[0].isupper())
        self.__dict__.update(defaults)
        self._load()
        if reseed:
            self._seed()
