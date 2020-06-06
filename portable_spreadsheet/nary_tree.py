import copy
from typing import Set, Tuple, List, Optional


class NaryTree(object):
    """Single node of the tree with arity n >= 0 (n-ary tree).

    Attributes:
        children (Set[NaryTree]): Children (sub-nodes) of the current node.
        index_row (Optional[int]): Row index of the node or None for
            the computational nodes.
        index_col (Optional[int]): Column index of the node or None for
            the computational nodes.
    """

    def __init__(self,
                 index_row: Optional[int] = None,
                 index_col: Optional[int] = None):
        """Initialize the new node.

        Args:
            index_row (Optional[int]): Row index of the node or None for
                the computational nodes.
            index_col (Optional[int]): Column index of the node or None for
                the computational nodes.
        """
        self.children: Set[NaryTree] = set([])
        self.coordinates = (index_row, index_col)

    @property
    def coordinates(self) -> Tuple[int, int]:
        """Returns the coordinates of the cell.

        Returns:
            Tuple[int, int]: 1) row index, 2) column index
        """
        return self.index_row, self.index_col

    @coordinates.setter
    def coordinates(self, new_coordinates: Tuple[int, int]) -> None:
        """Set the coordinates of the cell.

        Args:
            new_coordinates (Tuple[int, int]): 1) row index, 2) column index
        """
        set_coordinates = None
        if new_coordinates[0] is None and new_coordinates[1] is None:
            set_coordinates = (-1, -1)
        elif (new_coordinates[0] is not None and new_coordinates[0] >= 0
              and new_coordinates[1] is not None and new_coordinates[1] >= 0):
            set_coordinates = new_coordinates
        if set_coordinates is None:
            raise ValueError("Both coordinates has to be either none "
                             "or non-negative integers.")
        self.index_row, self.index_col = set_coordinates

    def _delete_recursion(
            self,
            tree_root: 'NaryTree',
            index_row: int,
            index_col: int,
            delete_row: bool = False,
            delete_col: bool = False,
            depth: int = 0
    ) -> List[Tuple[bool, int, Tuple[int, int]]]:
        """Recursively walks (in-depth) through the tree and returns indices
            of cells that has to be updated. Also update current tree

        Args:
            tree_root (NaryTree): Not that is the subject of deletion.
            index_row (int): Cell's integer position of deleted row.
            index_col (int): Cell's integer position of deleted column.
            delete_row (bool): True if the user wants to delete row.
            delete_col (bool): True if the user wants to delete column.
            depth (int): Depth of the current call.

        Returns:
            List[Tuple[bool, int, Tuple[int, int]]]: List of indices of the
                current tree. In the tuple, first: is deleted/modified(?),
                second: arity of the node, third: tuple(row index,
                column index).
        """
        # Prepare empty output
        list_of_children: List[Tuple[bool, int, Tuple[int, int]]] = []

        # True if anything in the branch is deleted (or node itself is deleted)
        cell_mod = (tree_root.index_row == index_row and
                    tree_root.index_col == index_col) or \
                   (delete_col and tree_root.index_col == index_col) or \
                   (delete_col and tree_root.index_col == index_col)

        # Delete leaf from children
        nodes_to_delete = []
        # Probe all children of the current node
        for child in tree_root.children:
            # Recursive step
            child_out = self._delete_recursion(child,
                                               index_row, index_col,
                                               delete_row, delete_col,
                                               depth + 1)
            child_mod = []
            # Back-propagate change
            for child_series in child_out:
                if child_series[0]:
                    cell_mod = True
                    child_mod.append(child_series)

            # Ask to delete cell from the tree
            if (child.index_col == index_col and
                    child.index_row == index_row) or \
                    (delete_col and child.index_col == index_col) or \
                    (delete_row and child.index_row == index_row):
                nodes_to_delete += [child]

            # Append to the list
            list_of_children += child_mod

        # Delete leaf from the tree
        for node_to_delete in nodes_to_delete:
            tree_root.children.discard(node_to_delete)

        # Move indices if deleted index is set and greater than current one
        indices_move = [int(delete_row and tree_root.index_row > index_row),
                        int(delete_col and tree_root.index_col > index_col)]
        tree_root -= tuple(indices_move)  # Numerically moves indices

        list_of_children += [(cell_mod, depth,
                              (tree_root.index_row, tree_root.index_col))]

        return list_of_children

    def delete(
            self,
            index_row: int,
            index_col: int,
            *,
            _delete_row: bool = False,
            _delete_col: bool = False
    ) -> Tuple[Tuple[int, int]]:
        """Delete row or column and return the list of cell indices
            be updated sorted from lower (leaves) priority -> upper (root)
            priority.

        Args:
            index_row (int): Cell's integer position of deleted row.
            index_col (int): Cell's integer position of deleted column.
            _delete_row (bool): True if the whole row is deleted.
            _delete_col (bool): True if the whole column is deleted.

        Returns:
            Tuple[Tuple[int, int]]: Tuple of tuples with indices of
                cell to be updated in the driving sheet.
        """
        # Return all the indices of cells that has to be updated and skip
        #   the index of the cell that is being deleted
        return tuple([cell_i[2] for cell_i in self._delete_recursion(
            self, index_row, index_col, _delete_row, _delete_col
        )
                      if cell_i[2] != (index_row, index_col)
                      ])

    def _add_children(self, child: 'NaryTree') -> None:
        """Add the new child to current node.

        Args:
            child (NaryTree): new child to be added.

        Raises:
            ValueError: In the case that 'child' parameter is not None type.
        """
        if not isinstance(child, NaryTree):
            raise ValueError("The argument 'child' must be of NaryTree type!")
        self.children.add(copy.deepcopy(child))

    def delete_row(self, row_index: int) -> None:
        """Delete whole row.

        Args:
            row_index (int): Position (integer indexed from zero) of row.
        """
        # 2 ^ 30 is the arbitrary big constant (sheet cannot have 2^30 cells)
        self.delete(row_index, 2 ** 30, _delete_row=True)

    def delete_column(self, column_index: int) -> None:
        """Delete whole column.

        Args:
            column_index (int): Position (integer indexed from zero) of column.
        """
        # 2 ^ 30 is the arbitrary big constant (sheet cannot have 2^30 cells)
        self.delete(2 ** 30, column_index, _delete_col=True)

    # ======================= OVERLOADED OPERATORS ============================
    def __len__(self) -> int:
        """Overload the len(OBJ) operator. Result equals to the number of
            children of the current node.

        Returns:
            int: The number of children of this node.
        """
        return len(self.children)

    def __lshift__(self, child: 'NaryTree') -> None:
        """Overload operator '<<' for adding the child to the node.

        Args:
            child (NaryTree): new child to be added.
        """
        self._add_children(child)
        return self

    def __imatmul__(self, index_tuple: Tuple[int, int]):
        """Add the child to the tree based on its indices (always a leaf).
            Works with operator '@='.

        Args:
            index_tuple (Tuple[int, int]): Accepts the row index and the
                column index of the leaf that is to be appended.

        Usage:
            >>> tree @= (row_idx, col_idx)
            >>> tree @= (3, 5)
            where the variable 'tree' is the NaryTree object.
        """
        self.children.add(NaryTree(index_row=index_tuple[0],
                                   index_col=index_tuple[1]))
        return self

    def __str__(self) -> str:
        """Return human-readable string representation of the tree.

        Returns:
            str: human-readable string representation of the tree.
        """
        output = ""
        queue = [self, None]
        while len(queue) > 0:
            appending = False
            for idx in range(len(queue)):
                in_queue = queue[idx]
                if in_queue == 'SEP_START':
                    output += '['
                    continue
                elif in_queue == 'SEP_END':
                    output += '], '
                    continue
                elif in_queue is None:
                    break
                if len(in_queue.children) > 0:
                    queue += ['SEP_START']
                    appending = True
                    for child in in_queue.children:
                        queue += [child]
                    queue += ['SEP_END']
                # Modify string
                output += str(in_queue.coordinates) + ','

            if appending:
                queue += [None]

            for idx in range(len(queue)):
                in_queue = queue[0]
                # Delete from the queue
                del queue[0]
                if in_queue is None:
                    break
            # Append the end of the line at the end
            if len(queue) > 0:
                output += '\n'
        return output

    def __isub__(self, subtrahend: Tuple[int, int]):
        """Subtract the row and column index from the current position.
            Overloads the operator '-=' to commit the position subtraction.

        Args:
            subtrahend (Tuple[int, int]): Row and Column (in this order)
                indices to be subtracted.
        """
        # Sanity check
        if not (isinstance(subtrahend, tuple) and
                len(subtrahend) == 2 and
                isinstance(subtrahend[0], int) and
                isinstance(subtrahend[1], int) and
                subtrahend[0] >= 0 and subtrahend[1] >= 0):
            raise ValueError("Only tuple of non-negative integers is "
                             "acceptable!")
        # Subtract the row position
        self.index_row -= subtrahend[0]
        # Subtract the column position
        self.index_col -= subtrahend[1]
        return self

    def __getitem__(self, child_coordinates: Tuple[int, int]) -> 'NaryTree':
        """Return the sub tree with the index of children equal to the
            parameter.

        Args:
            child_coordinates (Tuple[int, int]): What children based on index
                should be returned.

        Returns:
            NaryTree: Sub-tree (child) of the current tree in given position.

        Raises:
            KeyError: if the index is not in children's indices.
        """
        for child in self.children:
            if child.coordinates == child_coordinates:
                return child
        raise KeyError("Index is not in the list!")
    # =========================================================================

    @staticmethod
    def construct(*cells) -> 'NaryTree':
        """Factory for constructing a tree from cells as operators.

        Args:
            *cells (List[Cell]): List of cells that figures as operands.

        Returns:
            NaryTree: Construction of the tree for given operands.
        """
        tree = NaryTree()
        for cell in cells:
            tree << cell.operations_tree
        return tree
