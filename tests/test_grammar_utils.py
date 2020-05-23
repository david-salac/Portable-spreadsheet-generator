import unittest
import copy

from portable_spreadsheet.grammar_utils import GrammarUtils
from portable_spreadsheet.grammars import GRAMMARS


class TestGrammarUtils(unittest.TestCase):
    """Tests of the class GrammarUtils"""

    def test_get_languages(self):
        """Test the getter for system languages."""
        expected = set([str(lang) for lang in GRAMMARS.keys()])
        computed = GrammarUtils.get_languages()
        self.assertSetEqual(expected, computed)

    def test_validate_grammar(self):
        """Test the validator of the grammar."""
        wrong_new_grammar = {'test': 'value'}
        with self.assertRaises(ValueError):
            GrammarUtils.validate_grammar(wrong_new_grammar, True)
        self.assertFalse(GrammarUtils.validate_grammar(wrong_new_grammar,
                                                       False))

        correct_grammar = copy.deepcopy(GRAMMARS['native'])
        self.assertTrue(GrammarUtils.validate_grammar(correct_grammar, True))

    def test_add_remove_grammar(self):
        """Tests if adding and removing of grammars works."""
        # Test if exception is raised when incorrect grammar is added
        wrong_new_grammar = {'test': 'value'}
        with self.assertRaises(ValueError):
            GrammarUtils.validate_grammar(wrong_new_grammar, "wrong")
        # Test adding and removing
        grammars_before: set = copy.deepcopy(GrammarUtils.get_languages())
        new_grammar = GRAMMARS['native']
        language_for_new_grammar = "newly-added"
        # Test adding
        GrammarUtils.add_grammar(new_grammar, language_for_new_grammar)
        grammars_after = copy.deepcopy(grammars_before)
        grammars_after.add(language_for_new_grammar)
        set_after_adding = GrammarUtils.get_languages()
        self.assertSetEqual(set_after_adding, grammars_after)
        # Testing removing
        GrammarUtils.remove_grammar(language_for_new_grammar)
        set_after_deleting = GrammarUtils.get_languages()
        self.assertSetEqual(set_after_deleting, grammars_before)

    def test_system_consistency(self):
        """Check the method for probing system consistency."""
        self.assertTrue(GrammarUtils.check_system_consistency())
