#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Window.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""
from __future__ import absolute_import, division, print_function

import pyglet.gl
import pyglet.window
from pyglet.window import key
import mallib.gui.widgets as malwidgets


def get_best_config(**kwargs):
    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screen = display.get_default_screen()
    template = pyglet.gl.Config(**kwargs)
    try:
        return screen.get_best_config(template)
    except pyglet.window.NoSuchConfigException:
        return None


class MalWindow(pyglet.window.Window):
    def __init__(self, width, height,
                 exclusive_mouse=False,
                 launch_fullscreen=False,
                 icon_path=None,
                 **kwargs):
        super(MalWindow, self).__init__(width, height, **kwargs)
        self.set_exclusive_mouse(exclusive_mouse)
        if launch_fullscreen:
            self.set_fullscreen()
        self.set_minimum_size(320, 200)
        # ensure on_resize call
        self.width, self.height = width, height
        if icon_path:
            self.set_icon(pyglet.image.load(icon_path))

        self.current_view = None
        self.views = []
        self.views_switch = malwidgets.PointingSwitchCycle(self, 'views')
        #self.switch_view(self.views_switch())
        self.resources = {}

    def switch_view(self, new_view):
        if self.current_view:
            self.current_view.pop_handlers()
        self.current_view = new_view
        self.current_view.push_handlers()

    def update(self, dt):
        self.current_view.update(dt)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.TAB:
            self.views_switch.inc()
            self.switch_view(self.views_switch())
        elif symbol == key.GRAVE:
            from mallib.shell import interactive_shell
            interactive_shell(self._shell_context())

    def _shell_context(self):
        return {}
