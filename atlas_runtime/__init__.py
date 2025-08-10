from __future__ import annotations

import os, sys, platform, importlib

__all__ = ['atlas_occ']

_RT = os.getenv('ATLAS_RUNTIME')


def _rt() -> str:
    if _RT: return _RT
    s = platform.system()
    if s == 'Windows': return 'win_x64'
    if s == 'Linux':   return 'linux_x64'
    # if s == 'Darwin':  return 'mac_universal'  # adjust if needed
    raise RuntimeError(f'Unsupported OS: {s}')


_dlldir = os.path.join(os.path.dirname(__file__), 'runtime', _rt())

if _dlldir not in sys.path:
    sys.path.insert(0, _dlldir)

if platform.system() == 'Windows':
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(_dlldir)
    else:
        os.environ['PATH'] = _dlldir + os.pathsep + os.environ.get('PATH', '')
else:
    os.environ['LD_LIBRARY_PATH'] = (
            _dlldir + os.pathsep + os.environ.get('LD_LIBRARY_PATH', ''))

atlas_occ = importlib.import_module('atlas_occ')
