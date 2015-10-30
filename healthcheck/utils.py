import errno
import os


def file_exists(path):
    """Return True if a file exists at `path`, False if it definitely
    doesn't.

    If some other error occurs when trying to see the file this will be
    raised. In particular it will raise an error if it doesn't have
    permission to list the file, whereas os.path.isfile and
    os.path.exists would simply return False.
    """
    try:
        os.stat(path)
        return True
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
        raise
