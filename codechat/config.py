from core.system.config import load_config

config = load_config('codechat')

config.setdefault(
    'Files',
    'always_exclude',
    ','.join([
        '__pycache__',
        '.idea',
        '.git',
        '.DS_Store',
        'r:^.aider.*',
        'r:.bin$',
        'r:.pyc$',
    ])
)
