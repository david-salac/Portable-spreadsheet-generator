import numpy as np
import operator

class DD(object):

    class _TT:
        def __init__(self, outer_instance, var):
            self.outer = outer_instance
            self.var = var
        def __setitem__(self, index, val):
            operator.setitem(getattr(self.outer, self.var), index, val)

    def __init__(self):
        self.x = np.zeros((10, 10))
        self.tt = DD._TT(self, 'x')

x = DD()
x.tt[7,8] = 9
print(x.x)

print(np.log(2.71))