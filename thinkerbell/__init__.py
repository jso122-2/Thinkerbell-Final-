
# Bridge top-level thinkerbell package to implementation in Thinkerbell_template_pipeline
import os, sys, pkgutil
_repo_root = '/home/black-cat/Documents/Thinkerbell/Thinkerbell_template_pipeline'
_pkg_path = os.path.join(_repo_root, 'thinkerbell')
# Ensure implementation root is on sys.path for direct module imports
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
# Extend package path so submodule imports resolve under implementation package
__path__ = [p for p in (__path__ if isinstance(globals().get("__path__", []), list) else [])]
if _pkg_path not in __path__:
    __path__.append(_pkg_path)
