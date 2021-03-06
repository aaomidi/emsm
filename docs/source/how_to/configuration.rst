Configuration
=============

The :file:`configuration/` directory contains all configuration files.
   
main.conf
---------

The :file:`main.conf` file contains the configuration of the EMSM and the
plugins.

.. code-block:: ini

   [emsm]
   # User that should run all of your minecraft worlds.
   user = minecraft
   # The log level (see also: https://docs.python.org/3/howto/logging.html)
   loglevel = "WARNING"
   # Maximum time that is waited until another EMSM instance releases
   # the file lock. 
   # -1 means no timeout, wait if necessairy an infinite time.
   timeout = -1
   
Each plugin has its own section with its name. E.g.:

.. code-block:: ini

   [backups]
   archive_format = bztar
   restore_message = This world is about to be resetted to an earlier state.
   restore_delay = 5
   auto_sync = yes
   max_storage_size = 30
   mirrors = 
   
Please take a look at the documentation of the plugins [#plugins_doc]_ for
further information.

server.conf
-----------

The EMSM needs the server executables to run the minecraft worlds. 
You can declare them into the :file:`server.conf` configuration file:

.. code-block:: ini

   [servername_in_the_application]
   server = `filename of the executable`
   url = `download url of the executable`
   start_cmd = `The bash commmand to start the server."`

*  **server**

   This is the name of the executable in the directory ``emsm_root/server``.
   
*  **url**

   The EMSM will try to download the server from this url. Furthermore, it 
   is used for updates.
   
   .. note:: **Download error**

      Try http if https does not work.
      
*  **start_cmd**

   This command is executed to start the server. The EMSM changes the current
   working directory to the directory of the world, that should be started 
   and executes this command. You have to use ``'{server}'`` as placeholder
   for the path of the server executable:
   
   .. code-block:: ini
      
      [vanilla]
      ...
      server = minecraft_server.jar
      # start_cmd is expanded to:
      #   'java -jar /path/to/emsm/server/minecraft_server.jar nogui.'
      start_cmd = java -jar {server} nogui.
      
   .. note:: Escaping **{}**
   
      If you need a ``'{}'`` in the *start_cmd* option, escape ``'{'`` 
      with ``'{{'`` and ``'}'`` with ``'}}'``.   

If you declare a new server, the EMSM will try to **download** it the next time 
you invoke the application.

Here's a simple example for a configuration, that uses multiple server versions:

.. code-block:: ini

   # The mojang minecraft server (also called vanilla) in version 1.6
   [vanilla_1.6]
   server = minecraft_server_1.6.jar
   # If *https* does not work, use *http* instead.
   url = https://s3.amazonaws.com/Minecraft.Download/versions/1.6.2/minecraft_server.1.6.2.exe
   start_cmd = java -jar {server} nogui.
   
   # If you want another version of the vanilla server:
   [vanilla_1.5]
   server = minecraft_server_1.5.jar
   url = http://assets.minecraft.net/1_5_2/minecraft_server.jar
   start_cmd = java -jar {server} nogui. 
   
   # For the bukkit server, use:
   [bukkit_latest]
   server = craftbukkit_latest.jar
   url = http://dl.bukkit.org/latest-rb/craftbukkit.jar
   start_cmd = java -jar {server}
   
   # Only a beta, when I wrote this:
   [bukkit_1.6]
   server = craftbukkit_1.6.jar
   url = http://cbukk.it/craftbukkit-beta.jar
   start_cmd = java -jar {server}
   
worlds.conf
-----------

The worlds managed by the EMSM have to be declared in the :file:`worlds.conf` 
configuration file. Each section represents another world.

The section name is also the name of the world in the application.

.. code-block:: ini

   [the world's name]
   # Port of the world. If <auto>, the EMSM will search an unused 
   # port and save it. 
   port = <auto> | int
   # Seconds until a smooth stop is considered as failed.
   stop_timeout = int
   # Message printed before stopping the world.
   stop_message = string
   # Seconds between sending the stop_message and the stop command.
   stop_delay = int
   # The name of the server in the server.conf, that should run the world.
   server = a server in server.conf
   
Here's an example that uses the *DEFAULT* section and configures the
worlds *foo* and *bar*:

.. code-block:: ini
   
   # This section contains the default values for all worlds.
   # It's not a world named: DEFAULT
   [DEFAULT]
   stop_delay = 5
   stop_timeout = 10
   stop_message = The server is going down.
      Hope to see you soon.
   port = <auto>
   server = vanilla_1.6

   [foo]
   # This ok, when all default values are set and valid.
   
   [bar]
   stop_delay = 0
   stop_timeout = 20
   stop_message = See you later aligator.
   port = 25565
   server = bukkit_1.6
   
.. [#plugins_doc] :ref:`plugins`, :ref:`core_plugins`