import os
import sys

def fix_paths():
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
        os.environ['PYTHONPATH'] = application_path
        sys.path.insert(0, application_path)
        
        base_dir = os.path.dirname(sys.executable)
        
        data_dirs = [
            'data',
            'data/uploads',
            'data/projects',
            'data/models',
            'data/simulations',
            'data/temp',
            'docs',
            'docs/templates',
            'docs/generated',
            'frontend/static',
            'frontend/templates',
        ]
        
        for dir_name in data_dirs:
            dir_path = os.path.join(base_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

fix_paths()
