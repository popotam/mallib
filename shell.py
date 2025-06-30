#!/usr/bin/env python
"""iPython shell initialization code.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""

from distutils.version import LooseVersion


def interactive_shell(namespace):
    try:
        import IPython

        if LooseVersion(IPython.__version__) >= LooseVersion('0.11'):
            IPython.embed(
                user_ns=namespace,
                banner1="Starting interactive shell",
                exit_msg="Leaving interactive shell",
            )
        else:
            from IPython.Shell import IPShellEmbed

            ipshell = IPShellEmbed(
                banner="Starting interactive shell",
                exit_msg="Leaving interactive shell",
                user_ns=namespace,
            )
            ipshell()
    except ImportError:
        print("Unable to enter interactive mode - could not import ipython")
