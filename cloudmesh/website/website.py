import textwrap
import os
from cloudmesh.common.util import banner
from cloudmesh.common.console import Console
from pathlib import Path
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
import glob

class Website:

    def _readfile(self, name):
        with open(name) as f:
            content = f.read()
        return content

    def _writefile(self, name, content):
        with open(name, "w") as f:
            f.write(content)

    def _walk_to_depth(self, path, depth):
        depth -= 1
        with os.scandir(path) as p:
            for entry in p:
                yield entry.path
                if entry.is_dir() and depth > 0:
                    yield from self._walk_to_depth(entry.path, depth)

    def find_files_at_depth(self, p, depth):
        p = Path(p)
        assert p.exists(), f'Path: {p} does not exist'
        pattern = os.path.join(p, '*/' * depth)
        return list(glob.glob(pattern))

    def _walk(self, path, depth, recursive):
        if recursive:
            return self._walk_to_depth(path, depth)
        else:
            return self.find_files_at_depth(path, depth)

    def index(self, directory=".", dironly=True, progress=False, recursive=True, depth=None,
              nopage=False):
        exclude = [".git/", "__pycache__"]
        page_start = textwrap.dedent("""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Page Title</title>
            </head>
            <body>
            <h1>{directory}</h1>
            """).strip()
        page_end = textwrap.dedent("""            
            </body>
            </html> """).strip()

        if not nopage:
            print(page_start)

        print()
        print ("<ul>")

        if depth is not None:
            location = Path(directory)
            #candidates = self.find_files_at_depth(location, depth)
            #for p in candidates:
            for p in self._walk(location, depth, recursive):
                if dironly and Path(p).is_dir():
                    pass
                elif not dironly:
                    pass
                else:
                    continue
                found = False
                for word in exclude:
                    if word in str(p):
                        found = True
                        break;
                if not found:
                    if progress:
                        print (p)
                    d = str(p)
                    url = f'<a href="{d}"> {d} </a>'
                    print(url.encode("utf-8"))
        elif recursive:
            for p in Path(directory).rglob('*'):
                if dironly and Path(p).is_dir():
                    pass
                elif not dironly:
                    pass
                else:
                    continue
                found = False
                for word in exclude:
                    if word in str(p):
                        found = True
                        break;
                if not found:
                    if progress:
                        print (p)
                    d = str(p)
                    url = f'<a href="{d}"> {d} </a>'
                    print(url.encode("utf-8"))
        else:
            for p in Path(directory).glob('*'):
                if dironly and Path(p).is_dir():
                    pass
                elif not dironly:
                    pass
                else:
                    continue
                found = False
                for word in exclude:
                    if word in str(p):
                        found = True
                        break;
                if not found:
                    if progress:
                        print (p)
                    d = str(p)
                    url = f'<a href="{d}"> {d} </a>'
                    print(url)
        print ("</ul>")
        print()
        if not nopage:
            print(page_end)


    def replace(self, directory=".", replace_file="replace.txt", find_only=False):

        r_content = readfile(replace_file)
        content = r_content.splitlines()

        exclude = Shell.cm_grep(content, "exclude=")[0].replace("exclude=", "").strip().split(" ")

        include = Shell.cm_grep(content, "include=")[0].replace("include=", "").strip().split(" ")

        content = Shell.find_lines_between(content, "# begin replace", "# en replace")[1:-1]
        replace_data = []
        for line in content:
            if not line.startswith("#"):
                (text_from, text_to) = line.split(" ", 1)
                replace_data.append((text_from, text_to))

        banner("BEGIN REPLACE SETUP")
        print (r_content)
        banner("END REPLACE SETUP")
        print()
        for p in Path(directory).rglob('*'):
            if Path(p).is_symlink():
                kind = "l"
            elif Path(p).is_file():
                kind = "f"
            elif Path(p).is_dir():
                kind = "d"
            if kind not in ["d"]:
                try:
                    info = [f"Replace {p}"]
                    p_str = str(p)
                    p_ending = os.path.basename(p_str).split(".")[1].lower()
                    if Path(p).is_file() and  \
                            not p.is_symlink() and \
                            p.exists() and \
                            p_ending in include and \
                            p_ending not in exclude:
                        content = self._readfile(p_str)
                        changed = False
                        for replace_from, replace_to in replace_data:
                            if replace_from in content:
                                info.append(f"{p}: " + replace_from + " -> " + replace_to)
                                content = content.replace(replace_from, replace_to)
                                changed = True
                        # banner(f"REPLACE {p}")
                        # print(content)
                        if changed:
                            banner(info[0])
                            print("\n".join(info[1:]))
                            print()
                            self._writefile(p_str, content)
                        else:
                            print("-", kind, p, flush=True)
                except Exception as e:
                    print("?", kind, p)
            else:
                print("-", kind, p)

        print()
        print()

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