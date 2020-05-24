from typing import Set

from .grammars import GRAMMAR_PATTERN, GRAMMARS


class GrammarUtils(object):
    """Utils for validating and adding user defined grammars to the system.
    """

    @staticmethod
    def _get_value_at_path(grammar: dict, path: list):
        """Get the value on the path in the dictionary of logic defined in the
            path ['a', 'b'].

        Args:
            grammar (dict): Grammar dictionary.
            path (list): Path inside the grammar (1D array)

        Returns:
            object: value inside
        """
        if len(path) == 0:
            return grammar
        else:
            start, *rest = path
            return GrammarUtils._get_value_at_path(grammar[start], rest)

    @staticmethod
    def _check_dictionary(grammar: dict, key: list = []):
        """Walk across all values in the grammar and check if types of all
            words definitions matches.

        Args:
            grammar (dict): Probed grammar.
            key (list): The path to the probed entity.
        """
        # Possibly dictionary, possibly value:
        _pos_dict = GrammarUtils._get_value_at_path(grammar, key)
        if isinstance(_pos_dict, dict):
            _keys = _pos_dict.keys()
            for _key in _keys:
                GrammarUtils._check_dictionary(grammar, key + [_key])
        else:
            # Expected type
            ex_type = GrammarUtils._get_value_at_path(GRAMMAR_PATTERN, key)
            if isinstance(_pos_dict, ex_type):
                pass
            else:
                raise ValueError(f"Input grammar is not valid at path {key}!")

    @staticmethod
    def validate_grammar(grammar: dict, raise_exception: bool = False) -> bool:
        """Validate the input grammar.

        Args:
            grammar (dict): Grammar definition.
            raise_exception (bool): If True, error is raised when occurs.

        Returns:
            bool: True, if the grammar is valid, False otherwise.

        Raises:
            ValueError: If grammar is invalid and argument raise_exception.
        """
        try:
            GrammarUtils._check_dictionary(grammar)
        except ValueError as ve:
            if raise_exception:
                raise ve
            else:
                return False
        except KeyError as ke:
            if raise_exception:
                raise ValueError("Invalid keys in input!") from ke
            else:
                return False
        return True

    @staticmethod
    def add_grammar(grammar_definition: dict, language_name: str) -> None:
        """Add the grammar to the system.

        Args:
            grammar_definition (dict): Definition of the grammar.
            language_name (str): Name of the language (like 'excel', 'python')
        """
        # Check the grammar and raise exception if it is invalid
        GrammarUtils.validate_grammar(grammar_definition, True)
        # Add the grammar
        if language_name not in GRAMMARS.keys():
            GRAMMARS[language_name] = grammar_definition
        else:
            raise ValueError(f"Language {language_name} is already in the "
                             "system.")

    @staticmethod
    def remove_grammar(language_name: str) -> None:
        """Remove the grammar from the system.

        Args:
            language_name (str): Name of the language (like 'excel', 'python')
        """
        # Add the grammar
        if language_name in GRAMMARS.keys():
            del GRAMMARS[language_name]
        else:
            raise ValueError(f"Language {language_name} is not in the "
                             "system.")

    @staticmethod
    def get_languages() -> Set[str]:
        """Returns the set of included languages.

        Returns:
            Set[str]: Set of all languages included in the system.
        """
        return set([str(lang) for lang in GRAMMARS.keys()])

    @staticmethod
    def check_system_consistency() -> bool:
        """Check if the system contains all neccessary grammars.

        Returns:
            bool: True if system is consistent, False otherwise
        """
        languages_in_system = GrammarUtils.get_languages()
        if len({'excel', 'python_numpy'} & languages_in_system) != 2:
            return False
        validation = GrammarUtils.validate_grammar(GRAMMARS['excel']) \
            and GrammarUtils.validate_grammar(GRAMMARS['python_numpy'])
        return validation
