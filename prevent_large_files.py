#!/usr/bin/env python3
"""Pre-receive hook to check if there are large files in the packages.

This hook prevents files which are larger than 5MB in size.
"""

import subprocess
import sys

# Global variables used by pre-recieve hook
ZERO_COMMIT = "0000000000000000000000000000000000000000"
MAXSIZE = int(5242880)  # 5MB limit on file size
ERROR_MSG = """Error: file larger than %.0f Mb.

    File name: '%s'
    File size: %.1f Mb

Please see Biocondcutor guidelines
https://contributions.bioconductor.org/general.html
"""


def prevent_large_files(oldrev, newrev, refname):
    """Pre-receive hook to check for large files."""

    # set oldrev properly if this is branch creation
    if oldrev == ZERO_COMMIT:
        if refname == "refs/heads/master":
            oldrev = subprocess.check_output([
                "git", "rev-list", "--max-parents=0", newrev
            ], encoding='UTF-8').split().pop().strip()
        else:
            oldrev = "HEAD"

    list_files = subprocess.check_output(["git", "diff",
                                          "--name-only",
                                          "--diff-filter=ACMRT",
                                          oldrev + ".." + newrev], encoding='UTF-8')
    for fl in list_files.splitlines():

        size = subprocess.check_output(["git", "cat-file", "-s",
                                        newrev + ":" + fl], encoding='UTF-8')
        #  Check to see if for some reason we didn't get a size
        size = int(size.strip())
        if size:
            # Compare filesize to MAXSIZE
            mb = 1024.0 * 1024.0
            if size > MAXSIZE:
                print(ERROR_MSG % (MAXSIZE / mb, fl, size / mb))
                sys.exit(1)
    return
