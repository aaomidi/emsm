#!/usr/bin/python3

# Extendable Minecraft Server Manager - EMSM
# Copyright (C) 2013-2014 Benedikt Schmitt <benedikt@benediktschmitt.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
About
=====
This plugin provides a user interface for the server wrapper. It can handle
the server files and their configuration parameters easily.


Configuration
=============
[server]
update_message = The server is going down for an update.

Where
-----
* update_message
    Is a string, printed before stopping a world for an update.


Arguments
=========
* --configuration
* --update
* --force-update
* --uninstall
"""


# Modules
# ------------------------------------------------
import os

# local
import world_wrapper
import server_wrapper
from base_plugin import BasePlugin
from app_lib import downloadreporthook
from app_lib import userinput


# Data
# ------------------------------------------------
PLUGIN = "Server"

    
# Classes
# ------------------------------------------------
class MyServer(object):
    """
    Wraps an application server wrapper. :)
    """

    def __init__(self, app, server):
        self.app = app
        self.server = server
        return None

    def print_configuration(self):
        """
        Prints the configuration of the server.
        """
        print("{} - configuration:".format(self.server.name))
        for option in self.server.conf:
            print("\t", option, "=", self.server.conf[option])
        return None

    def update(self, force_stop=True, stop_message=str()):
        """
        Updates the server.

        Before the server will be updated, all worlds that are currently
        online with this server, will be stopped.
        """
        print("{} - update: ...".format(self.server.name))
        
        # Get all worlds, that are currently running the server.
        worlds = self.app.worlds.get_by_pred(
            lambda w: w.server is self.server and w.is_online())

        # Stop those worlds.
        try:
            for world in worlds:
                print("{} - update: Stopping the world '{}' ..."\
                      .format(self.server.name, world.name))
                world.send_command("say {}".format(stop_message))
                world.stop(force_stop)
        # Do not continue if a world could not be stopped.
        except world_wrapper.WorldStopFailed as error:
            print("{} - update: failure: The world '{}' could not be stopped."\
                  .format(self.server.name, error.world.name))
        # Continue with the server update if all worlds are offline.
        else:
            reporthook = downloadreporthook.Reporthook(
                url=self.server.url,
                target=self.server.server
                )
            print("{} - update: Downloading the server ..."\
                  .format(self.server.name))
            try:
                self.server.update(reporthook)
            except server_wrapper.ServerUpdateFailure as error:
                print("{} - update: failure: {}"\
                      .format(self.server.name, error))
            else:
                print("{} - update: Download is complete."\
                      .format(self.server.name))
        # Restart the worlds.
        finally:
            for world in worlds:
                try:
                    world.start()
                except world_wrapper.WorldIsOnlineError:
                    pass
                except world_wrapper.WorldStartFailed:
                    print("{} - update: failure: The world '{} could not be "\
                          "restarted.".format(self.server.name, world.name))
                else:
                    print("{} - update: The world '{}' has been restated."\
                          .format(self.server.name, world.name))
        return None

    def uninstall(self):
        """
        Uninstalls the server.

        Before the server will be uninstalled, there will be some checks to
        make sure the server can be uninstalled without any side effects.
        """
        # We need a server that could replace this one.
        avlb_server = self.app.server.get_names()
        avlb_server.pop( avlb_server.index(self.server.name) )

        # Break if there is no other server available.
        if not avlb_server:
            print("{} - uninstall: failure: There's no other server that "\
                  "could replace this one.".format(self.server.name))
            return None
        
        # Make sure, that the server should be removed.
        question = "{} - uninstall: Are you sure, that you want to "\
                   "uninstall the server? ".format(self.server.name)
        if not userinput.ask(question):
            return None
        
        # Get the name of the server that should replace this one.
        replacement = userinput.get_value(
            prompt=("{} - uninstall: Which server should replace this one?\n\t"
                    "(Chose from: {}) ".format(self.server.name, avlb_server)),
            check_func=lambda server: server in avlb_server,
            )
        replacement = self.app.server.get(replacement)        
        
        # Remove the server.
        try:
            self.server.uninstall(replacement)
        except server_wrapper.ServerIsOnlineError as error:
            print("{} - uninstall: The server is still running. ",
                  "\n\t'{}'".format(self.server.name, error))
        return None

    
class Server(BasePlugin):
    """
    Public interface for the server wrapper.    
    """

    version = "2.0.0"
    
    def __init__(self, application, name):
        BasePlugin.__init__(self, application, name)

        self.setup_conf()
        self.setup_argparser()
        return None

    def setup_conf(self):
        self.update_message = self.conf.get(
            "update_message", "The server is going down for an update.")

        self.conf["update_message"] = self.update_message
        return None

    def setup_argparser(self):
        self.argparser.description = (
            "This plugin provides methods to manage the server files "
            "and the server configuration.")
                
        self.argparser.add_argument(
            "--configuration",
            action = "count",
            dest = "conf",
            help = "Prints the configuration of the server."
            )

        update_group = self.argparser.add_mutually_exclusive_group()
        update_group.add_argument(
            "--update",
            action = "count",
            dest = "update",
            help = "Updates the selected server."
            )
        update_group.add_argument(
            "--force-update",
            action = "count",
            dest = "force_update",
            help = "Forces the stop of a world before the update begins."
            )
        
        self.argparser.add_argument(
            "--uninstall",
            action = "count",
            dest = "uninstall",
            help = "Removes the server."
            )
        return None

    def run(self, args):
        server = self.app.server.get_selected()
        for s in server:            
            s = MyServer(self.app, s)
            
            if args.conf:
                s.print_configuration()

            if args.update:
                s.update(False, self.update_message)
            elif args.force_update:
                s.update(True, self.update_message)
                
            if args.uninstall:
                s.uninstall()
        return None
