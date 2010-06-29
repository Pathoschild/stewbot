# empty __init__ to ensure Python treats the directory as a package namespace.

# directory for third-party modules, used if they're not present on the system
import os, sys;
sys.path.append(os.path.dirname(__file__) + '/modules')