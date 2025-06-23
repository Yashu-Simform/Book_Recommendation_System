class SingletonMetaClass(type):
    """
    Meta Class:
    An implementation of singleton class is carried out here.
    """

    _instance = {}

    def __call__(self, *args, **kwds):
        if self not in SingletonMetaClass._instance:
            SingletonMetaClass._instance[self] = super().__call__(*args, **kwds)

        return SingletonMetaClass._instance[self]
