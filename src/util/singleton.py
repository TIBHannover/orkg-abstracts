from typing import Type


def singleton(_):
    """
    This decorator can only be used above the __new__ function of a class. It's responsible for returning a pre-created
    instance of the respective class or create a new one, if not have happened before.

    :param _: The __new__ function.
    :return:
    """

    def apply_pattern(cls: Type, *args, **kwargs):
        # attention: *args and **kwargs must be included even if not used!
        if not hasattr(cls, 'instance'):
            cls.instance = super(cls.__class__, cls).__new__(cls)
        return cls.instance

    return apply_pattern


class SingletonService:
    """
    The SingletonService is intended to be inherited by any service that follows the singleton pattern.
    """
    @singleton
    def __new__(cls, *args, **kwargs):
        pass
