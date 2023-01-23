import textwrap
import os

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
            print(execute)
            if not dryrun:
                os.system(execute)