#! /usr/bin/env python3

"""
start file for simplescn
license: MIT, see LICENSE.txt
"""

import sys
import os
import logging
import threading
import signal
#import json

from simplescn.tools import loglevel_converter
from simplescn import config

confdb_ending = ".confdb"

# don't load different module
if __name__ == "__main__":
    ownpath = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.dirname(ownpath))

from simplescn_gui import scnparse_args, parsepath


guiclient_instance = None
default_loglevel = "DEBUG"
logformat = '%(levelname)s::%(filename)s:%(lineno)d::%(funcName)s::%(message)s'

_is_init_already = False
def _init_scn():
    """ initialize once and only in mainthread """
    global _is_init_already
    if not _is_init_already and threading.current_thread() == threading.main_thread():
        _is_init_already = True
        logging.basicConfig(level=loglevel_converter(default_loglevel), format=logformat)
        signal.signal(signal.SIGINT, _signal_handler)

def _signal_handler(_signal, frame):
    """ handles signals; shutdown properly """
    guiclient_instance.quit()
    logging.shutdown()
    sys.exit(0)


def client(argv=sys.argv[1:]):
    """ gui client """
    try:
        client_gtk(argv)
    except Exception as exc:
        logging.error(exc)
        return

default_client_config = \
{
    "backlog": [str(200), int, "length of backlog"],
    "config": [config.default_configdir, parsepath, "<path>: path to config dir"],
    "loglevel": [str(config.default_loglevel), loglevel_converter, "<int/str>: loglevel"]
}
def client_gtk(argv=sys.argv[1:]):
    """ gtk gui """
    _init_scn()
    from simplescn_gui.guigtk.clientmain import _init_method_gtkclient
    from simplescn_gui.common import configmanager #pluginmanager
    from simplescn.client import client_paramhelp

    #overwrite_client_args2 = argv
    #pluginpathes = [os.path.join(sharedir, "plugins")]
    overkwargs = scnparse_args(argv, client_paramhelp, default_client_config)
    configpath = overkwargs["config"][1](overkwargs["config"][0])
    overkwargs["config"][0] = configpath
    #pluginpathes.insert(1, os.path.join(configpath, "plugins"))
    #configpath_plugins = os.path.join(configpath, "config", "plugins")
    os.makedirs(os.path.join(configpath, "config"), 0o750, True)
    #os.makedirs(configpath_plugins, 0o750, True)
    # uses different configuration file than rawclient
    confm = configmanager(os.path.join(configpath, "config", "clientgtkgui{}".format(confdb_ending)))
    confm.update(default_client_config, overkwargs)
    #if not confm.getb("noplugins"):
    #    pluginm = pluginmanager(pluginpathes, configpath_plugins, "client")
    #    if confm.getb("webgui"):
    #        pluginm.interfaces += ["web",]
    #    pluginm.interfaces += ["cmd", "gtk"]
    #else:
    #    pluginm = None
    _init_method_gtkclient(confm, None) #pluginm



#def config_plugin(argv=sys.argv[1:]):
#    """ func: configure plugin without starting gui (useful for server plugins)
#        plugin: plugin name
#        key: unspecified: list keys
#        value: unspecified: get value, else: set value """
#    init_scn()
#    from simplescn.common import overwrite_plugin_config_args, plugin_config_paramhelp, pluginmanager
#    pluginpathes = [os.path.join(sharedir, "plugins")]
#    pluginpathes += scnparse_args(argv, plugin_config_paramhelp, overwrite_args=overwrite_plugin_config_args)
#    configpath = overwrite_plugin_config_args["config"][0]
#    configpath = os.path.expanduser(configpath)
#    if configpath[-1] == os.sep:
#        configpath = configpath[:-1]
#    overwrite_plugin_config_args["config"][0] = configpath
#    # path  to plugins in config folder
#    pluginpathes.insert(1, os.path.join(configpath, "plugins"))
#    # path to config folder of plugins
#    configpath_plugins = os.path.join(configpath, "config", "plugins")
#    os.makedirs(os.path.join(configpath, "config"), 0o750, True)
#    os.makedirs(configpath_plugins, 0o750, True)
#    pluginm = pluginmanager(pluginpathes, configpath_plugins, "config_direct")
#    #pluginm.init_plugins()
#    config = pluginm.load_pluginconfig(overwrite_plugin_config_args["plugin"][0])
#    if config is None:
#        logging.error("No such plugin: %s", overwrite_plugin_config_args["plugin"][0])
#        return
#    if overwrite_plugin_config_args["key"][0] == "":
#        lres = config.list()
#        if not isinstance(lres, (tuple, list)):
#            return
#        for key, val, cls, default, doc, perm in lres:
#            print("* key: {}\n  * type: {}\n  * perm: {}\n  * val: {}\n  * default: {}\n  * doc: {}".format(key, type(cls).__name__, perm, val, default, doc))
#    elif overwrite_plugin_config_args["value"][0] == "":
#        key = overwrite_plugin_config_args["key"][0]
#        res1 = config.get_meta(key)
#        if not isinstance(res1, (tuple, list)):
#            return
#        val = config.get(key)
#        default = config.get_default(key)
#        cls, doc, perm = res1
#        print("# key: {}\n  * type: {}\n  * perm: {}\n  * val: {}\n  * default: {}\n  * doc: {}".format(key, type(cls).__name__, perm, val, default, doc))
#    else:
#        print(config.set(overwrite_plugin_config_args["key"][0], overwrite_plugin_config_args["value"][0]))

def _init_method_main(argv=sys.argv[1:]):
    """ starter method """
    if len(argv) > 0:
        toexe = globals().get(argv[0].strip("_"), None)
        if callable(toexe):
            toexe(argv[1:])
        else:
            print("Not available", file=sys.stderr)
            print("Available: client", file=sys.stderr)
    else:
        print("Available: client", file=sys.stderr)

if __name__ == "__main__":
    _init_method_main()
