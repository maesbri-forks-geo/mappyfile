from collections import OrderedDict, Callable
import copy

from mappyfile.validator import Validator


validator = Validator()


class CaseSensitiveKeyError(KeyError):
    pass


class CaseInsensitveOrderedDict(OrderedDict):
    """
    Used for storing components properties
    """
    def __init__(self):
        super(CaseInsensitveOrderedDict, self).__init__()

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError as ex:
            possible_matches = []
            for k in self.keys():
                if k.lower().replace("'", "") == key.lower():
                    possible_matches.append(k)
            msg = str(ex)
            if possible_matches:
                msg = u'Key {} not found. Did you mean {}?'.format(msg, ",".join(possible_matches))

            raise CaseSensitiveKeyError(msg)


class DefaultOrderedDict(OrderedDict):
    """
    Used for storing components
    Source: http://stackoverflow.com/a/6190500/562769
    http://code.activestate.com/recipes/523034-emulate-collectionsdefaultdict/
    """

    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and not isinstance(default_factory, Callable)):
            raise TypeError('First argument must be callable')

        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        key = key.lower()  # all keys should be lowercase to make editing easier
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key, v):
        if "__type__" in self.keys():
            # validator.validate(self, self["__type__"])
            pass
        super(self.__class__, self).__setitem__(key, v)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'DefaultOrderedDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))
