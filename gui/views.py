#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Views.

mallib: common library for mal projects
@author: Pawel Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak. All rights reserved.

'''

import pyglet.clock


class View(object):
    def __init__(self, window):
        self.window = window
        self.frame = None
        self.camera = None
        self.fps_display = pyglet.clock.ClockDisplay()

    def push_handlers(self):
        """
        Push event handlers to window dispatcher.
        Simplui, camera and view events are sent.
        Use on activating view.
        """
        self.setup()
        self.window.push_handlers(self.camera)
        self.window.push_handlers(self.frame)
        self.window.push_handlers(self)

    def pop_handlers(self):
        """
        Pop event handlers from window dispatcher.
        Use on view deactivation
        """
        self.window.pop_handlers()
        self.window.pop_handlers()
        self.window.pop_handlers()

    def update(self, df):
        pass

    def setup(self):
        pass
