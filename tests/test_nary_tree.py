import unittest
import copy

from portable_spreadsheet.nary_tree import NaryTree


class TestNaryTree(unittest.TestCase):
    """Test the nary tree for holding indices."""
    def setUp(self) -> None:
        self.tree = NaryTree(0, 0)
        child_a = NaryTree(1, 0)
        child_b = NaryTree(0, 1)
        # Add leafs to node B
        child_b @= (7, 8)
        child_b @= (9, 10)

        child_c = NaryTree(3, 2)
        # Add leafs to node C
        child_c @= (7, 2)
        child_c @= (8, 2)
        child_c @= (9, 2)
        child_c @= (10, 2)
        # Add node C as a child of node A
        child_a << child_c
        # Add node A to root
        self.tree << child_a
        # Add node B to root
        self.tree << child_b

    def test_add(self):
        """Check the adding to the tree."""
        # Probe the root node
        self.assertTupleEqual(self.tree.coordinates, (0, 0))

        # Probe the first degree children (depth = 1)
        node_a, node_b = [ch for ch in self.tree.children]
        coord_a, coord_b = node_a.coordinates, node_b.coordinates
        if coord_a == (0, 1):
            coord_a, coord_b = coord_b, coord_a
            node_a, node_b = node_b, node_a

        self.assertSetEqual({coord_a, coord_b}, {(1, 0), (0, 1)})
        self.assertEqual(len(node_a), 1)
        self.assertEqual(len(node_b), 2)

        # Probe second degree children (depth = 2)
        # Probe node B
        leaf_b_1, leaf_b_2 = [ch for ch in node_b.children]
        coord_l_b_1, coord_l_b_2 = leaf_b_1.coordinates, leaf_b_2.coordinates
        if coord_l_b_1 == (9, 10):
            coord_l_b_1, coord_l_b_2 = coord_l_b_2, coord_l_b_1
            leaf_b_1, leaf_b_2 = leaf_b_2, leaf_b_1
        self.assertSetEqual({coord_l_b_1, coord_l_b_2}, {(7, 8), (9, 10)})
        self.assertEqual(len(leaf_b_1), 0)
        self.assertEqual(len(leaf_b_2), 0)

        # Probe node C
        node_c = [ch for ch in node_a.children][0]
        coord_c = node_c.coordinates
        self.assertTupleEqual(coord_c, (3, 2))
        self.assertEqual(len(node_c), 4)

        # Probe leafs of node C (depth = 3
        leaf_c_1, leaf_c_2, leaf_c_3, leaf_c_4 = [ch for ch in node_c.children]
        coord_l_c_1, coord_l_c_2, coord_l_c_3, coord_l_c_4 = \
            leaf_c_1.coordinates, leaf_c_2.coordinates, leaf_c_3.coordinates, \
            leaf_c_4.coordinates
        self.assertSetEqual(
            {coord_l_c_1, coord_l_c_2, coord_l_c_3, coord_l_c_4},
            {(7, 2), (8, 2), (9, 2), (10, 2)})
        self.assertEqual(len(leaf_c_1), 0)
        self.assertEqual(len(leaf_c_2), 0)
        self.assertEqual(len(leaf_c_3), 0)
        self.assertEqual(len(leaf_c_4), 0)

    def test_delete(self):
        """Test deleting in the tree."""
        # Delete leaf
        tree = copy.deepcopy(self.tree)
        path = tree.delete(9, 2)
        self.assertTupleEqual(path, ((3, 2), (1, 0), (0, 0)))
        self.assertEqual(len(tree[1, 0]), 1)
        self.assertEqual(len(tree[1, 0][3, 2]), 3)
        self.assertSetEqual(
            {ch.coordinates for ch in tree[1, 0][3, 2].children},
            {(8, 2), (10, 2), (7, 2)}
        )

        # Delete non-leaf node
        tree = copy.deepcopy(self.tree)
        path = tree.delete(3, 2)
        self.assertTupleEqual(path, ((1, 0), (0, 0)))
        self.assertEqual(len(tree[1, 0]), 0)
        self.assertEqual(len(tree[0, 1]), 2)

    def test_delete_row_and_column(self):
        """Test deleting of the whole row and column in the tree."""
        # Delete row
        tree = copy.deepcopy(self.tree)
        # Delete arbitrary row
        tree.delete_row(1)
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0, 1].coordinates, (0, 1))
        self.assertEqual(len(tree[0, 1]), 2)
        self.assertEqual(len(tree[0, 1][6, 8]), 0)
        self.assertEqual(len(tree[0, 1][8, 10]), 0)

        # Delete column
        tree = copy.deepcopy(self.tree)
        # Delete arbitrary column
        tree.delete_column(1)
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[1, 0].coordinates, (1, 0))
        self.assertEqual(len(tree[1, 0]), 0)
