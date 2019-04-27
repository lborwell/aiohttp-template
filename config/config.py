from importlib import import_module


class Config(object):

    @classmethod
    def load(cls, module_):
        config = {}
        if isinstance(module_, str):
            module_ = import_module(module_)
        for k in dir(module_):
            config[k] = getattr(module_, k)
        return config
