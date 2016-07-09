
def client(argv=sys.argv[1:]):
    """ gui client """
    try:
        client_gtk(argv)
    except Exception as exc:
        logging.error(exc)
        rawclient(argv)
        return

def client_gtk(argv=sys.argv[1:]):
    """ gtk gui """
    init_scn()
    from simplescn.guigtk.clientmain import _init_method_gtkclient
    from simplescn.common import pluginmanager, configmanager
    from simplescn.client import client_paramhelp, overwrite_client_args, default_client_args

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
    confm = configmanager(os.path.join(configpath, "config", "clientgtkgui{}".format(confdb_ending)))
    confm.update(default_client_args, overwrite_client_args)
    if not confm.getb("noplugins"):
        pluginm = pluginmanager(pluginpathes, configpath_plugins, "client")
        if confm.getb("webgui"):
            pluginm.interfaces += ["web",]
        pluginm.interfaces += ["cmd", "gtk"]
    else:
        pluginm = None
    _init_method_gtkclient(confm, pluginm)



def config_plugin(argv=sys.argv[1:]):
    """ func: configure plugin without starting gui (useful for server plugins)
        plugin: plugin name
        key: unspecified: list keys
        value: unspecified: get value, else: set value """
    init_scn()
    from simplescn.common import overwrite_plugin_config_args, plugin_config_paramhelp, pluginmanager
    pluginpathes = [os.path.join(sharedir, "plugins")]
    pluginpathes += scnparse_args(argv, plugin_config_paramhelp, overwrite_args=overwrite_plugin_config_args)
    configpath = overwrite_plugin_config_args["config"][0]
    configpath = os.path.expanduser(configpath)
    if configpath[-1] == os.sep:
        configpath = configpath[:-1]
    overwrite_plugin_config_args["config"][0] = configpath
    # path  to plugins in config folder
    pluginpathes.insert(1, os.path.join(configpath, "plugins"))
    # path to config folder of plugins
    configpath_plugins = os.path.join(configpath, "config", "plugins")
    os.makedirs(os.path.join(configpath, "config"), 0o750, True)
    os.makedirs(configpath_plugins, 0o750, True)
    pluginm = pluginmanager(pluginpathes, configpath_plugins, "config_direct")
    #pluginm.init_plugins()
    config = pluginm.load_pluginconfig(overwrite_plugin_config_args["plugin"][0])
    if config is None:
        logging.error("No such plugin: %s", overwrite_plugin_config_args["plugin"][0])
        return
    if overwrite_plugin_config_args["key"][0] == "":
        lres = config.list()
        if not isinstance(lres, (tuple, list)):
            return
        for key, val, cls, default, doc, perm in lres:
            print("* key: {}\n  * type: {}\n  * perm: {}\n  * val: {}\n  * default: {}\n  * doc: {}".format(key, type(cls).__name__, perm, val, default, doc))
    elif overwrite_plugin_config_args["value"][0] == "":
        key = overwrite_plugin_config_args["key"][0]
        res1 = config.get_meta(key)
        if not isinstance(res1, (tuple, list)):
            return
        val = config.get(key)
        default = config.get_default(key)
        cls, doc, perm = res1
        print("# key: {}\n  * type: {}\n  * perm: {}\n  * val: {}\n  * default: {}\n  * doc: {}".format(key, type(cls).__name__, perm, val, default, doc))
    else:
        print(config.set(overwrite_plugin_config_args["key"][0], overwrite_plugin_config_args["value"][0]))

if __name__ == "__main__":
    pass
