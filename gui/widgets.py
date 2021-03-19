#!/usr/bin/env python
"""Widgets.

mallib: common library for mal projects
@author: Pawel Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak. All rights reserved.

"""

from pyglet.gl import *
import pyglet.text
from pyglet.window import key
from pyglet.window import mouse


class Switch(object):
    def __init__(self, state=False):
        self.value = state

    def toggle(self):
        self.value = not self.value

    def off(self):
        self.value = False

    def on(self):
        self.value = True

    def __bool__(self):
        return self.value

    def __trunc__(self):
        if self:
            return 1
        else:
            return 0


class CheckboxProxy(Switch):
    def __init__(self, checkbox, state=False, callback=None):
        self.checkbox = checkbox
        self.callback = callback
        if callback:
            self.checkbox.action = lambda caller: self.callback(caller.value)
        super().__init__(state=state)

    @property
    def value(self):
        return self.checkbox.value

    @value.setter
    def value(self, value):
        if self.checkbox.value != value:
            self.checkbox.value = value
            if self.callback:
                self.callback(value)


class SliderProxy(object):
    def __init__(self, slider, callback=None):
        """ Offset is a fix for simplui Slider bug when min < 0 """
        self.slider = slider
        self.callback = callback
        if callback:
            self.slider.action = lambda caller: self.callback(self.value)
        self.offset = 0
        if slider._min < 0:
            self.offset = -slider._min
            slider._min = 0
            slider._max += self.offset
            slider._value += self.offset

    @property
    def value(self):
        return self.slider.value - self.offset

    @value.setter
    def value(self, value):
        self.slider.value = value + self.offset
        if self.slider.value < self.slider.min:
            self.slider.value = self.slider.min
        elif self.slider.value > self.slider.max:
            self.slider.value = self.slider.max
        if self.callback:
            self.callback(self.value)


class ButtonProxy(Switch):
    def __init__(self, button, true_text, false_text, state=False):
        self.button = button
        self.button.action = lambda caller: self.toggle()
        self.true_text = true_text
        self.false_text = false_text
        super().__init__(state=state)

    def toggle(self):
        self.value = not self.value
        self.button.text = self.true_text if self.value else self.false_text


class SwitchCycle(object):
    def __init__(self, length, state=0, cycling=True):
        self.value = state
        self.length = length
        self.cycling = Switch(cycling)

    def inc(self):
        self.value += 1
        if self.value >= self.length:
            self.value = 0 if self.cycling else self.length - 1
        return self

    def dec(self):
        self.value -= 1
        if self.value < 0:
            self.value = self.length - 1 if self.cycling else 0
        return self

    def __call__(self):
        return self.value


class PointingSwitchCycle(SwitchCycle):
    def __init__(self, parent, list_name, state=0, cycling=True):
        self.parent = parent
        self.list_name = list_name
        super().__init__(self.length, state, cycling)

    def __call__(self):
        return getattr(self.parent, self.list_name)[self.value]

    @property
    def length(self):
        return len(getattr(self.parent, self.list_name))

    @length.setter
    def length(self, value):
        """ Override SwitchCycle setting of length attribute """
        pass


class UpdatedLabel(pyglet.text.Label):
    def __init__(self, *args, **kwargs):
        if 'update_object' in kwargs:
            self.update_object = kwargs['update_object']
            del kwargs['update_object']
        else:
            self.update_object = None
        if 'update_func' in kwargs:
            self.update_func = kwargs['update_func']
            del kwargs['update_func']
        else:
            self.update_func = None
        if 'update_rate' in kwargs:
            self.update_rate = kwargs['update_rate']
            del kwargs['update_rate']
        else:
            self.update_rate = 10
        super().__init__(*args, **kwargs)
        self.update_count = self.update_rate - 1

    def update(self):
        if self.update_func and self.update_object:
            self.update_count += 1
            if self.update_count % self.update_rate == 0:
                self.update_count = 0
                text = self.update_func(self.update_object)
                if self.text != text:
                    print(self.text, text)
                    self.text = text


class Camera2D(object):
    def __init__(self, parent, x=0, y=0, target=None, locked=False,
                 min_zoom=0.25, max_zoom=2.0):
        self.parent = parent
        self._zoom_quantifier = 10.0  # 100%
        self.min_zoom = 10.0 / (min_zoom ** 0.5)
        self.max_zoom = 10.0 / (max_zoom ** 0.5)
        self.x = x
        self.y = y
        self.target = target
        self.zoom_in = Switch(False)
        self.zoom_out = Switch(False)
        self.move_left = Switch(False)
        self.move_right = Switch(False)
        self.move_up = Switch(False)
        self.move_down = Switch(False)
        if locked:
            self.update = self._update_locked
        else:
            self.update = self._update_free

    def become_locked(self):
        self.update = self._update_locked

    def become_free(self):
        self.update = self._update_free

    @property
    def zoom(self):
        return 100.0 / (self._zoom_quantifier ** 2)

    def transform_scene(self):
        zoom = self.zoom
        # move to the center of the window
        glTranslatef(self.parent.window.width / 2.0,
                     self.parent.window.height / 2.0,
                     0.0)
        glScalef(zoom, zoom, 1.0)
        glTranslatef(-self.x, -self.y, 0.0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Z:
            self.zoom_in.on()
        elif symbol == key.X:
            self.zoom_out.on()
        elif symbol == key.A:
            self.move_left.on()
        elif symbol == key.D:
            self.move_right.on()
        elif symbol == key.W:
            self.move_up.on()
        elif symbol == key.S:
            self.move_down.on()
        elif symbol == key.F:
            self.become_locked()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.Z:
            self.zoom_in.off()
        elif symbol == key.X:
            self.zoom_out.off()
        elif symbol == key.A:
            self.move_left.off()
        elif symbol == key.D:
            self.move_right.off()
        elif symbol == key.W:
            self.move_up.off()
        elif symbol == key.S:
            self.move_down.off()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == mouse.RIGHT:
            self._drag_move(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._zoom_scroll(scroll_x, scroll_y)

    def _drag_move(self, dx, dy):
        self.x -= 2.0 * dx / self.zoom
        self.y -= 2.0 * dy / self.zoom
        self.become_free()

    def _zoom_scroll(self, scroll_x, scroll_y):
        self._zoom_quantifier -= scroll_y / 5.0
        self._check_bounds()

    def _check_bounds(self):
        if self._zoom_quantifier < self.max_zoom:
            self._zoom_quantifier = self.max_zoom
        elif self._zoom_quantifier > self.min_zoom:
            self._zoom_quantifier = self.min_zoom

    def _update_free(self):
        if self.zoom_in:
            self._zoom_quantifier += 0.25
        if self.zoom_out:
            self._zoom_quantifier -= 0.25
        if self.move_left:
            self.x -= 20.0 / self.zoom
        if self.move_right:
            self.x += 20.0 / self.zoom
        if self.move_up:
            self.y += 20.0 / self.zoom
        if self.move_down:
            self.y -= 20.0 / self.zoom
        self._check_bounds()

    def _update_locked(self):
        if self.zoom_in:
            self._zoom_quantifier += 0.25
        if self.zoom_out:
            self._zoom_quantifier -= 0.25
        if self.target:
            x, y = self.target.position
            self.x = round(max(min(self.x, x + 75.0), x - 75.0))
            self.y = round(max(min(self.y, y + 75.0), y - 75.0))
        if self.move_left or self.move_right or self.move_up or self.move_down:
            self.become_free()
        self._check_bounds()
