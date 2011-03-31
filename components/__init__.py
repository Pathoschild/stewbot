# empty __init__ to ensure Python treats the directory as a package namespace.
import os;
import sys;

# directory for self-contained modules & third-party modules used preferentially
# to ensure correct versions
sys.path.insert(0, os.path.dirname(__file__) + '/modules')
sys.path.insert(0, os.path.dirname(__file__) + '/interfaces')
