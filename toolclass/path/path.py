import os

class Path:
    @staticmethod
    def append_path(*args):
        return os.path.join(os.getcwd(), *args)