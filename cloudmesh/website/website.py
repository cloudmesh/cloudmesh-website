import textwrap
import os
from cloudmesh.common.util import banner
from cloudmesh.common.console import Console
from pathlib import Path


class Website:

    def replace(self, directory=".", replace_file="replace.txt", find_only=False):

        exclude = ["gz", "tgz", "gif", "ppt", "pptx", "jpeg", "xsd", "java", "jar",
                   "c", "xml", "jpg", "png"]
        include = ["htm", "html", "css"]

        for p in Path(directory).rglob('*'):
            try:
                p_str = str(p)
                p_ending = os.path.basename(p_str).split(".")[1].lower()
                if Path(p).is_file() and  \
                        not p.is_symlink() and \
                        p.exists() and p_ending in include:
                    print (p, end="")
                    file = open(p, "r")
                    content = file.read()
                    file.close()
                    if "http://grids.ucs.indiana.edu" in content:
                        print ("*")
                    else:
                        print()


            except Exception as e:
                pass

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
                     dryrun=False,
                     relative=False,
                     mode="sh"):
        banner("# Broken links")
        if not relative:
            d = os.path.abspath(directory)
        else:
            d = directory
        if mode in ["sh"]:
            execute = f'find "{d}" -type l ! -exec test -e {{}} \\; -print'
            print ("#", execute)
            if not dryrun:
                    os.system(execute)
        else:
            for p in Path(d).rglob('*'):
                if p.is_symlink() and not p.exists():
                    location = os.readlink(p)
                    print(f"{p} -> {location}")


    def rsync_dir_in_parallel(self,
                              source=".",
                              destination=None,
                              parallel=False,
                              dryrun=False):
        if destination is None:
            Console.error("Destination not set properly")
            return
        elif os.path.abspath(destination) == os.path.abspath(source):
            Console.error("Destination and source must not be the same")
            return
        banner("rsync directories in parallel")
        if not parallel:
            command = f"rsync -avP --info=progress2 {source} {destination}"
            print("#", command)
            if not dryrun:
                os.system(command)
        else:
            pass
            # find_dirs_in_source
            # find files in source
            # copy all files with rsync
            # copy all dirs with rsync

    def find_subdirectories(self, directory):
        dirs = []
        for path in Path(directory).iterdir():
            if path.is_dir():
                dirs.append(path)
        return dirs

    def find_files_in_dir(self, directory):
        # list to store files
        files = []

        # Iterate directory
        for path in os.listdir(directory):
            # check if current path is a file
            if os.path.isfile(os.path.join(directory, path)):
                files.append(path)
        return