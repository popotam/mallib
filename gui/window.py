#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Window.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import pyglet.window
from pyglet.window import key
from mallib.gui import widgets


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
        self.views_switch = widgets.PointingSwitchCycle(self, 'views')
        #self.switch_view(self.views_switch())

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
