class SkippedLabel(object):
    """This label of columns or rows are intended to be skipped when exported.

    Attributes:
        label: the label that is used for selection.
        empty_entity: if true, row or column is intended to be empty
            and are skipped for some types of exports.
    """

    def __init__(self,
                 label: str = None,
                 empty_entity: bool = False):
        """Initialise skipped label.

        Args:
            label: the label that is used for selection.
            empty_entity: if true, row or column is intended to be empty
                and are skipped for some types of exports.
        """
        self.label: str = label
        self.empty_entity: bool = empty_entity

    def replace(self, old, new, count: int = -1):
        """Replace the characters inside the label.
        Args:
            old: old string to be replaced.
            new: new string that is inserted instead of old one.
            count: how many times should be repeated.
        """
        if self.label is None:
            return
        self.label = self.label.replace(old, new, count)

    def __str__(self):
        """Overload to string method."""
        if self.label is None:
            return None
        return self.label
