#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Settings.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

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
        self._load()
        self._seed()

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
        if getattr(self, 'RANDOM_SEED', None) is None:
            self.RANDOM_SEED = random.randint(0, 999999999)
        seed = self.RANDOM_SEED
        self.random.seed(seed)
        self.logger.info('Using %i as random seed for %s',
                         seed, self.settings_name)

    def reload(self, reseed=True):
        # preserve logger and current random generator
        self.__dict__ = {'logger': self.logger,
                         'random': self.random}
        self._load()
        if reseed:
            self._seed()
