from cell import Cell


class CellSlice(object):
    def __init__(self):
        pass

    def sum(self) -> Cell:
        pass

    def product(self) -> Cell:
        pass

    def min(self) -> Cell:
        pass

    def max(self) -> Cell:
        pass

    def mean(self) -> Cell:
        pass

    def average(self):
        return self.mean()

    # Set to scalar:
    def set(self, other):
        pass

    def __ilshift__(self, other):
        self.set(other)
