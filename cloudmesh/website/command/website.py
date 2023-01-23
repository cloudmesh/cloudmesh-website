from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from pathlib import Path
import os

class WebsiteCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_website(self, args, arguments):
        """
        ::

          Usage:
                website chmod [--recursive] [--parallel] [DIRECTORY] [--dryrun]
                website broken links [DIRECTORY] [--dryrun]

          This command introduces some convenient website manipulation programs.

          Arguments:
              DIRECTORY  The directory on which the command works [default=.]

          Options:
              --dryrun     Dryrun the command and do not execute [default=False].
              --recursive  Run recursively in the directory tree [default=False].
              --parallel   Run in parallel in the background [default=False].

          Description:

            chmod  --recursive .
                changes recursivly all permissions in the given directory . with
                  chmod 0755 for directories (drwxr-xr-x) chmod a+xr cmod u+rw
                  chmod 0644 for files       (-rw-r--r--)  chmod a+r cmod u+rw

                if --recursive is omitted, only the given directory is changed
                The two chmod processes can also run in parallel and in the background

        """

        variables = Variables()
        variables["debug"] = True

        map_parameters(arguments, "recursive", "dryrun", "parallel")
        arguments.DIRECTORY = os.path.abspath(arguments.DIRECTORY)

        VERBOSE(arguments)

        from cloudmesh.website.website import Website

        w = Website()

        if arguments.chmod:
            w.permissions(dryrun=arguments.dryrun,
                          directory=arguments.DIRECTORY,
                          recursive=arguments.recursive,
                          parallel=arguments.parallel)
        elif arguments.broken and arguments.links:
            w.broken_links(directory=arguments.DIRECTORY, dryrun=arguments.dryrun)

        return ""
