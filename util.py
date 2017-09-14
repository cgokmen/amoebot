import numpy as np


class HashableArray(object):
    def __init__(self, data):
        self.data = np.array(data)
        self.data.flags.writeable = False
        self.hash = hash(self.data.data)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        if not isinstance(other, HashableArray):
            return False

        return np.all(self.data == other.data)
