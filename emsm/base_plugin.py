#!/usr/bin/python3

# The MIT License (MIT)
# 
# Copyright (c) 2014 Benedikt Schmitt <benedikt@benediktschmitt.de>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Modules
# ------------------------------------------------

# std
import os
import logging
import shutil

# emsm
from . import argparse_
from .app_lib import userinput


# Data
# ------------------------------------------------

__all__ = [
    "BasePlugin"
    ]

log = logging.getLogger(__file__)


# Classes
# ------------------------------------------------
    
class BasePlugin(object):
    """
    This is the base class for all plugins.
    """

    # Integer with the init priority of the plugin.
    # A higher value results in a later initialisation.
    INIT_PRIORITY = 0

    # Integer with the finish priority of the plugin.
    # A higher value results in a later call of the finish method.
    FINISH_PRIORITY = 0

    # The EMSM version number of the EMSM version that worked correctly
    # with that plugin.
    VERSION = "0.0.0"

    # The plugin can be downloaded from this resource.
    DOWNLOAD_URL = None

    # This string is displayed when the ``--long-help`` argument is used.
    DESCRIPTION = None

    def __init__(self, app, name):
        """
        Initialises the configuration and the storage of the plugin.

        Override:
            * Extend, but do not override.
        """
        self.__app = app
        self.__name = name

        # Get the argparser for this plugin and set it up.
        self.__argparser = app.argparser.plugin_parser(name)  
        self.__argparser.add_argument(
            "--long-help",
            action = argparse_.LongHelpAction,
            description = type(self).DESCRIPTION
            )

        log.debug("initialised BasePlugin for '{}'.".format(name))
        return None

    def app(self):
        """
        Returns the parent EMSM Application that owns this plugin.
        """
        return self.__app

    def name(self):
        """
        Returns the name of the plugin.
        """
        return self.__name

    def conf(self):
        """
        Returns a dictionary like object that contains the configuration
        of the plugin.
        """
        # Make sure the configuration section exists.
        main_conf = self.__app.conf.main()
        if not self.__name in main_conf:
            main_conf.add_section(self.__name)
            log.info("created configuration section for '{}'."\
                     .format(self.__name))
        
        return main_conf[self.__name]

    def data_dir(self, create=True):
        """
        Returns the directory that contains all data created by the plugin
        to manage its EMSM job.

        Parameters:
            * create
                If the directory does not exist, it will be created.

        Example:
            * The *backups* plugin stores all backups here.
        """
        data_dir = self._app.paths.plugin_data_dir(self._name)

        # Make sure the directory exists.
        if not os.path.exists(data_dir) and create:
            os.makedirs(data_dir)
            log.info("created data directory for '{}'.".format(self.__name))
        
        return data_dir
        
    def argparser(self):
        """
        Returns the argparse.ArgumentParser that is used by this plugin.

        See also:
            * ArgumentParser.plugin_parser()
        """
        return self.__argparser
        
    def uninstall(self):
        """
        Called when the plugin should be uninstalled. This method
        is interactive and requires the user to confirm which data
        should be removed.

        The base class method removes:
            * The plugin module (the *.py* file in *plugins*)
            * The plugin data directory
            * The plugin configuration
            
        Exceptions:
            * KeyboardInterrupt
                when the user aborts the uninstallation.

        See also:
            * data_dir()
            * conf()
        """
        log.info("uninstalling '{}' ...".format(self.__name))

        # Make sure the user really wants to uninstall the plugin.        
        if not userinput.ask("Do you really want to remove this plugin?"):
            # I did not want to implement a new exception type for this case.
            # I think KeyboardInterrupt is good enough.
            log.info("cancelled uninstallation of '{}'.".format(self.__name))
            raise KeyboardInterrupt

        # Remove the python module that contains the plugin.
        plugin_module = self.__app.plugins.get_module(self.name)
        if plugin_module:
            os.remove(plugin_module.__file__)
            
            log.info("removed '{}' module at '{}'."\
                     .format(self.__name, plugin_module.__file__)
                     )

        # Remove the plugin data directory.
        if userinput.ask("Do you want to remove the data directory?"):
            shutil.rmtree(self.data_dir(), True)
            
            log.info("removed '{}' plugin data directory at '{}'."\
                     .format(self.__name, self.data_dir(create=False))
                     )

        # Remove the configuration.
        if userinput.ask("Do you want to remove the configuration?"):
            self.__app.conf.main().remove_section(self.__name)
            
            log.info("removed '{}' configuration section."\
                     .format(self.__name))
        return None

    def run(self, args):
        """
        The *main* method of the plugin. This method is called if the plugin
        has been invoked by the command line arguments.

        Parameters:
            * args
                is an argparse.Namespace instance that contains the values
                of the parsed command line arguments.

        Override:
            * You may override this method.

        See also:
            * argparser()
            * ArgumentParser.args()
            * PluginManager.run()
        """
        return None

    def finish(self):
        """
        Called when the EMSM application is about to finish. This method can
        be used for background jobs or clean up stuff.

        Override:
            * You may override this method.
            
        See also:
            * PluginManager.finish()
        """
        return None
