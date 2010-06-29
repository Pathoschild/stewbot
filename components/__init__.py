# empty __init__ to ensure Python treats the directory as a package namespace.

# directory for third-party modules, used preferentially to ensure correct versions
import os, sys;
sys.path.insert(0, os.path.dirname(__file__) + '/modules')
