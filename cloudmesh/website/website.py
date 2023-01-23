import textwrap
import os
from cloudmesh.common.util import banner
class Website:

    def permissions(self,
                    directory=".",
                    recursive=True,
                    dryrun=False,
                    parallel=False):
        commands = textwrap.dedent(f"""
        find {directory} -type d -exec chmod 0755 {{}} \\;
        find {directory} -type f -exec chmod 0644 {{}} \\;
        """).strip().splitlines()
        background = ""
        if parallel:
            background = " &"
        for command in commands:
            execute = command + background
            print("#", execute)
            if not dryrun:
                os.system(execute)

    def broken_links(self,
                     directory=".",
                     dryrun=False):
        banner("Broken links")
        execute = f'find "{directory}" -type l ! -exec test -e {{}} \\; -print'
        print ("#", execute)
        if not dryrun:
                os.system(execute)
