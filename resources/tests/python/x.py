class X:
    def __str__(self):
        return '<X object>'

    def __eq__(self, other):
        return isinstance(other, self.__class__)
