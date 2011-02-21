#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''iPython shell initialization code.

Malsimulation: Malleable World Simulator
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''


def interactive_shell(globals_dict):
    try:
        globals().update(globals_dict)
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed([],
                               "Starting interactive shell",
                               "Leaving interactive shell")
        ipshell(header='')
    except:
        print "Unable to enter interactive mode - could not import ipython"
