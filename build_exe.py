import PyInstaller.__main__
import os
import sys

def build_executable():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    datas = [
        (os.path.join(base_dir, 'frontend', 'templates'), 'frontend/templates'),
        (os.path.join(base_dir, 'frontend', 'static'), 'frontend/static'),
        (os.path.join(base_dir, 'config.py'), '.'),
    ]
    
    hidden_imports = [
        'flask',
        'flask_cors',
        'pandas',
        'numpy',
        'sklearn',
        'matplotlib',
        'seaborn',
        'joblib',
        'openpyxl',
        'xlrd',
        'pyarrow',
        'scipy',
        'xgboost',
        'lightgbm',
        'backend',
        'backend.modules',
        'backend.routes',
        'backend.utils',
    ]
    
    args = [
        'app.py',
        '--name=RiskControlWorkbench',
        '--onefile',
        '--windowed',
        '--clean',
        '--noupx',
    ]
    
    for src, dst in datas:
        if os.path.exists(src):
            args.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
    
    for imp in hidden_imports:
        args.extend(['--hidden-import', imp])
    
    args.extend([
        '--runtime-hook', os.path.join(base_dir, 'runtime_hook.py')
    ])
    
    print("=" * 60)
    print("  开始打包风控策略/建模/算法工程师工作系统")
    print("=" * 60)
    print(f"  命令参数: {' '.join(args)}")
    print("=" * 60)
    
    PyInstaller.__main__.run(args)
    
    print("\n" + "=" * 60)
    print("  打包完成！")
    print(f"  可执行文件位置: {os.path.join(base_dir, 'dist', 'RiskControlWorkbench.exe')}")
    print("=" * 60)

if __name__ == '__main__':
    build_executable()
