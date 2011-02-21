#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Widgets.

mallib: common library for mal projects
@author: Pawel Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak. All rights reserved.

'''


class Switch(object):
    def __init__(self, state=False):
        self.value = state

    def toggle(self):
        self.value = not self.value

    def off(self):
        self.value = False

    def on(self):
        self.value = True

    def __nonzero__(self):
        return self.value


class CheckboxProxy(Switch):
    def __init__(self, checkbox, state=False, callback=None):
        self.checkbox = checkbox
        self.callback = callback
        if callback:
            self.checkbox.action = lambda caller: self.callback(caller.value)
        super(CheckboxProxy, self).__init__(state=state)

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
        super(ButtonProxy, self).__init__(state=state)

    def toggle(self):
        self.value = not self.value
        self.button.text = self.true_text if self.value else self.false_text


class SwitchCycle(object):
    def __init__(self, lenght, state=0, cycling=True):
        self.value = state
        self.lenght = lenght
        self.cycling = Switch(cycling)

    def inc(self):
        self.value += 1
        if self.value >= self.lenght:
            self.value = 0 if self.cycling else self.lenght - 1

    def dec(self):
        self.value -= 1
        if self.value < 0:
            self.value = self.lenght - 1 if self.cycling else 0

    def __call__(self):
        return self.value


class PointingSwitchCycle(SwitchCycle):
    def __init__(self, parent, list_name, state=0, cycling=True):
        self.parent = parent
        self.list_name = list_name
        SwitchCycle.__init__(self, self.lenght, state, cycling)

    def __call__(self):
        return getattr(self.parent, self.list_name)[self.value]

    @property
    def lenght(self):
        return len(getattr(self.parent, self.list_name))

    @lenght.setter
    def lenght(self, value):
        """ Override SwitchCycle setting of length attribute """
        pass
