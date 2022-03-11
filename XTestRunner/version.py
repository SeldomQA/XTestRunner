import re
import os
import ast

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INIT_FILE = os.path.join(BASE_DIR, "__init__.py")


# ---------------------------
# Read version number
# ---------------------------
def get_version():
    _version_re = re.compile(r'__version__\s+=\s+(.*)')
    with open(INIT_FILE, 'rb') as f:
        version = str(ast.literal_eval(_version_re.search(
            f.read().decode('utf-8')).group(1)))

    return version
