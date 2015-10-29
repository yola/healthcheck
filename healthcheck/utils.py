import errno
import os


def file_exists(path):
    """Return True if a file exists at `path` (even if it can't be read),
    otherwise False.

    This is different from os.path.isfile and os.path.exists which return
    False if a file exists but the user doesn't have permission to read it.
    """
    try:
        os.stat(path)
        return True
    except OSError as e:

        # Permission denied: someone chose the wrong permissions but it exists.
        if e.errno == errno.EACCES:
            return True

        # File doesn't exist
        elif e.errno == errno.ENOENT:
            return False

        # Unknown case
        raise
