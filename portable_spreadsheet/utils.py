import abc
import numpy
import json


class ClassVarsToDict(abc.ABC):
    """Allows to export class variables to dictionary using dict(inst)
    and access them using dict(inst)[VAR].
    """

    def keys(self):
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            List[str]: List of the keys.
        """
        return [vr for vr in vars(self) if not vr.startswith("_")]

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        return getattr(self, key)


class NumPyEncoder(json.JSONEncoder):
    """Encodes the NumPy variables to export"""
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(NumPyEncoder, self).default(obj)
