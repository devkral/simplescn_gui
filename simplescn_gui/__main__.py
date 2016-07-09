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
import json

# don't load different module
if __name__ == "__main__":
    ownpath = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.dirname(ownpath))

from simplescn import config
from simplescn._common import scnparse_args, loglevel_converter

guiclient_instance = None


_is_init_already = False
def _init_scn():
    """ initialize once and only in mainthread """
    global _is_init_already
    if not _is_init_already and threading.current_thread() == threading.main_thread():
        _is_init_already = True
        logging.basicConfig(level=loglevel_converter(config.default_loglevel), format=config.logformat)
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

def client_gtk(argv=sys.argv[1:]):
    """ gtk gui """
    _init_scn()
    from simplescn_gui.guigtk.clientmain import _init_method_gtkclient
    from simplescn_gui.common import pluginmanager, configmanager
    from simplescn_gui.client import client_paramhelp, overwrite_client_args, default_client_args

    default_client_args2 = default_client_args.copy()
    del default_client_args2["nocmd"]
    default_client_args["backlog"] = [str(200), int, "length of backlog"]
    pluginpathes = [os.path.join(sharedir, "plugins")]
    pluginpathes += scnparse_args(argv, client_paramhelp, default_client_args2, overwrite_client_args)
    configpath = overwrite_client_args["config"][0]
    configpath = os.path.expanduser(configpath)
    if configpath[-1] == os.sep:
        configpath = configpath[:-1]
    overwrite_client_args["config"][0] = configpath
    pluginpathes.insert(1, os.path.join(configpath, "plugins"))
    configpath_plugins = os.path.join(configpath, "config", "plugins")
    os.makedirs(os.path.join(configpath, "config"), 0o750, True)
    os.makedirs(configpath_plugins, 0o750, True)
    # uses different configuration file than rawclient
    #confm = configmanager(os.path.join(configpath, "config", "clientgtkgui{}".format(confdb_ending)))
    #confm.update(default_client_args, overwrite_client_args)
    #if not confm.getb("noplugins"):
    #    pluginm = pluginmanager(pluginpathes, configpath_plugins, "client")
    #    if confm.getb("webgui"):
    #        pluginm.interfaces += ["web",]
    #    pluginm.interfaces += ["cmd", "gtk"]
    #else:
    #    pluginm = None
    #_init_method_gtkclient(confm, pluginm)



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

if __name__ == "__main__":
    pass
