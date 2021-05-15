import numpy as np

class NearestDict:
    """
    Quickly lookup the nearest value in a dictionary.
    For example, in a dict from date -> value, if the exact
    date is unavailable, will return the value from the 
    nearest date.
    """
    def __init__(self, d):
        if type(d) is not dict:
            d = dict(d)
        self.d = d
        self.keys, self.values = zip(*sorted(d.items()))
        
    def __getitem__(self, key):
        try:
            return self.d[key]
        except KeyError:
            if key > self.keys[-1]:
                return self.values[-1]
            elif key < self.keys[0]:
                return self.values[0]
            i = np.searchsorted(self.keys, key)
            i = min(len(self.keys) - 1, i)
            return self.values[i]