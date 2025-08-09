import os, sys, platform, importlib, glob


def _rt():
    s = platform.system()
    if s == 'Windows': return 'win_x64'
    if s == 'Linux':   return 'linux_x64'
    raise RuntimeError(f'Unsupported OS: {s}')


def load_atlas_occ():
    rt = _rt()

    base_dir = os.path.dirname(__file__)  # atlas_runtime/
    dll_dir = os.path.join(base_dir, 'runtime', rt)

    # ensure the native deps + module are resolvable
    if platform.system() == 'Windows':
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(dll_dir)
        else:
            os.environ['PATH'] = (
                    dll_dir + os.pathsep + os.environ.get('PATH', ''))
    else:
        if dll_dir not in sys.path:
            sys.path.insert(0, dll_dir)
        os.environ['LD_LIBRARY_PATH'] = dll_dir + os.pathsep + os.environ.get(
            'LD_LIBRARY_PATH', '')

    # import the compiled extension; it must be named atlas_occ.*.so / .pyd
    try:
        return importlib.import_module('atlas_occ')
    except ModuleNotFoundError:
        # helpful debug if filename doesn’t match ABI
        candidates = glob.glob(os.path.join(dll_dir, 'atlas_occ*'))
        raise ModuleNotFoundError(
            f'atlas_occ not found on sys.path.\n'
            f'Checked: {dll_dir}\n'
            f'Candidates in dir: {candidates}\n'
            f'Python: {sys.version.split()[0]}  Platform: {platform.system()} {platform.machine()}'
        )
