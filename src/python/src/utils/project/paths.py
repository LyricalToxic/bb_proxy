from pathlib import Path
import inspect

import cmd


def get_root_path():
    return Path(__file__).parents[2]
