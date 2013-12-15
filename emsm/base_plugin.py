#!/usr/bin/python3
# Benedikt Schmitt <benedikt@benediktschmitt.de>


# Modules
# ------------------------------------------------
import os
import logging
import shutil

# local
from app_lib import userinput


# Data
# ------------------------------------------------
__all__ = ["BasePlugin"]


# Classes
# ------------------------------------------------
class BasePlugin(object):
    """
    This is the base class for all plugins.

    The dispatcher will call the methods when
    they are needed.
    """

    # Integer with the init priority of the plugin.
    # A higher value results in a later initialisation.
    init_priority = 0

    # Integer with the finish priority of the plugin.
    # A higher value results in a later call of the finish method.
    finish_priority = 0

    # The last compatible version of the application the
    # plugin worked.
    version = "0.0.0"

    # The plugin manager can lookup there for a new version of the plugin.
    download_url = ""

    def __init__(self, app, name):
        """
        Initialises the configuration and the storage of the plugin.

        Creates the following attributes:
            * self.app
            * self.name
            * self.log
            * self.conf
            * self.data_dir
            * self.argparser

        Extend but do not overwrite.
        """
        self.app = app
        self.name = name
        self.log = logging.getLogger(name)

        # Set the configuration up.
        main_conf = app.conf.main
        if name not in main_conf:
            main_conf.add_section(name)
        self.conf = main_conf[name]

        # Get the directories of the plugin.
        self.data_dir = app.paths.get_plugin_data_dir(name)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Create a new argparser for this plugin.
        self.argparser = app.argparser.plugin_parsers.add_parser(name)
        return None      

    def uninstall(self):
        """
        Called if the plugin should be uninstalled. It should
        remove all files and configuration options that it made.

        Raises: KeyboardInterrupt when the user aborts the uninstallation.
        """        
        if not userinput.ask("Do you really want to remove this plugin?"):
            # I did not want to implement a new exception type for this case.
            # I think KeyboardInterrupt is good enough.
            raise KeyboardInterrupt

        real_module = self.app.plugins.get_module(self.name)
        if real_module:
            os.remove(real_module.__file__)
        
        if userinput.ask("Do you want to remove the data directory?"):
            shutil.rmtree(self.data_dir, True)
            
        if userinput.ask("Do you want to remove the configuration?"):
            self.app.conf.main.remove_section(self.name)
        return True


    # EMSM plugin runlevel
    # --------------------------------------------

    def embedded_run(self, args):
        """
        Can be called from other plugins, if they want to use a plugins feature.
        args is a string, that contains the parameters of the plugin.    
        """
        args = self.argparser.parse_args(args.split())
        self.run(args)
        return None
    
    def run(self, args):
        """
        Called from the dispatcher if the plugin is invoked and
        the application is ready to run.

        Consider this method as the main method of the plugin.

        args is an argparse.Namespace instance that contains the values
        of the parsed arguments of the argparser.
        """
        return None

    def finish(self):
        """
        Called after the run method, but this time for all plugins.

        Can be used for clean up stuff or background jobs.
        """
        return None
