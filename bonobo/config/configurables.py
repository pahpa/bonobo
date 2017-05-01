from bonobo.config.options import Option

__all__ = [
    'Configurable',
    'Option',
]

_options_insert_order = 0

class Option:
    def __init__(self, type=None, *, required=False, positional=False, default=None):
        self.name = None
        self.type = type
        self.required = required
        self.positional = positional
        self.default = default

        global _options_insert_order
        self.order = _options_insert_order
        _options_insert_order += 1

    def __get__(self, inst, typ):
        if not self.name in inst.__options_values__:
            inst.__options_values__[self.name] = self.default() if callable(self.default) else self.default
        return inst.__options_values__[self.name]

    def __set__(self, inst, value):
        inst.__options_values__[self.name] = self.type(value) if self.type else value


class ConfigurableMeta(type):
    """
    Metaclass for Configurables that will add options to a special __options__ dict.
    """

    def __init__(cls, what, bases=None, dict=None):
        super().__init__(what, bases, dict)
        cls.__options__ = {}
        for typ in cls.__mro__:
            for name, value in typ.__dict__.items():
                if isinstance(value, Option):
                    if not value.name:
                        value.name = name
                    if not name in cls.__options__:
                        cls.__options__[name] = value


class Configurable(metaclass=ConfigurableMeta):
    """
    Generic class for configurable objects. Configurable objects have a dictionary of "options" descriptors that defines
    the configuration schema of the type.

    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.__options_values__ = {}

        missing = list()
        for name, option in type(self).__options__.items():
            if option.required and not option.name in kwargs:
                missing.append(name)

        for i in range(min(len(args), len(missing))):
            kwargs

        if len(missing):
            raise TypeError(
                '{}() missing {} required option{}: {}.'.format(
                    type(self).__name__,
                    len(missing), 's' if len(missing) > 1 else '', ', '.join(map(repr, sorted(missing)))
                )
            )

        extraneous = set(kwargs.keys()) - set(type(self).__options__.keys())
        if len(extraneous):
            raise TypeError(
                '{}() got {} unexpected option{}: {}.'.format(
                    type(self).__name__,
                    len(extraneous), 's' if len(extraneous) > 1 else '', ', '.join(map(repr, sorted(extraneous)))
                )
            )

        for name, value in kwargs.items():
            setattr(self, name, kwargs[name])
