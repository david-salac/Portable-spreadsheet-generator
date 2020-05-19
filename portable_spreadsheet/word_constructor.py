import copy
from typing import Dict, Set, Tuple

from .grammars import GRAMMARS

from .cell_indices import CellIndices
from .cell_type import CellType

# ==== TYPES ====
# Type for the word of some language, logic: key: language, value: word
T_word = Dict[str, str]
# ===============


class WordConstructor(object):
    """Provides functionality for constructing words in all supported languages
        and also serves container for keeping them.

    Attributes:
        languages (Set[str]): What languages are used.
        words (Dict[str, str]): Mapping from language name to word.
    """

    def __init__(self, *,
                 words: T_word = None,
                 languages: Set[str] = None,
                 cell_indices: CellIndices
                 ):
        """Initialise the word cunstructor.

        Args:
            languages (Set[str]): What languages are used.
            words (Dict[str, str]): Mapping from language name to word.
        """
        if languages is not None:
            self.languages: Set[str] = languages
        else:
            self.languages: Set[str] = set(cell_indices.languages)

        if words is not None:
            self.words: T_word = words
        else:
            self.words: T_word = {key: "" for key in self.languages}

    @staticmethod
    def init_from_new_cell(cell, /) -> 'WordConstructor':  # noqa E999
        """Initialise the words when the new cell is created.

        Args:
            cell (Cell): just created cell.

        Returns:
            WordConstructor: words for the new cell.
        """
        if cell.value is not None:
            # Value type cell
            return WordConstructor.constant(cell)
        else:
            # Empty cell
            return WordConstructor(cell_indices=cell.cell_indices)

    @staticmethod
    def _binary_operation(first, second, operation: str) -> 'WordConstructor':
        """General binary operation.

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.
            operation (str): Definition of the operation (in grammar).

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        instance = copy.deepcopy(first.word)
        first_words = first.word.words
        second_word = second.word.words
        for language in instance.languages:
            pref = GRAMMARS[language]['operations'][operation]['prefix']
            suff = GRAMMARS[language]['operations'][operation]['suffix']
            sp = GRAMMARS[language]['operations'][operation]['separator']
            instance.words[language] = pref + first_words[language] + sp \
                + second_word[language] + suff
        return instance

    @staticmethod
    def add(first, second, /) -> 'WordConstructor':  # noqa E225
        """Add binary operation (+).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "add")

    def subtract(first, second, /) -> 'WordConstructor':  # noqa E225
        """Subtract binary operation (-).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "subtract")

    def multiply(first, second, /) -> 'WordConstructor':  # noqa E225
        """Multiply binary operation (*).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "multiply")

    def divide(first, second, /) -> 'WordConstructor':  # noqa E225
        """Divide binary operation (/).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "divide")

    def power(first, second, /) -> 'WordConstructor':  # noqa E225
        """Power binary operation (**).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "power")

    @staticmethod
    def _aggregation_parse_cell(cell,
                                start_idx: Tuple[int, int],
                                end_idx: Tuple[int, int],
                                language: str
                                ) -> Tuple[str, str]:
        """Generates the aggregation string for a concrete language (regardless
            what aggregation method is selected).

        Args:
            cell (Cell): Any cell in the set (used for extracting indicies).
            start_idx (Tuple[int, int]): Position of the slice start.
            end_idx (Tuple[int, int]): Position of the slice end.
            language (str): What language is used.

        Returns:
            Tuple[str, str]: Definition of starting, ending cell in language.
        """
        start_idx_r = cell.cell_indices.rows[language][start_idx[0]]
        start_idx_c = cell.cell_indices.columns[language][start_idx[1]]

        end_idx_r = cell.cell_indices.rows[language][end_idx[0]]
        end_idx_c = cell.cell_indices.columns[language][end_idx[1]]

        pref_cell_start = GRAMMARS[language]['cells']['aggregation'][
            'start_cell']['prefix']
        separator_cell_start = GRAMMARS[language]['cells']['aggregation'][
            'start_cell']['separator']
        suffix_cell_start = GRAMMARS[language]['cells']['aggregation'][
            'start_cell']['suffix']

        if GRAMMARS[language]['cells']['aggregation']['start_cell'][
            'row_first'
        ]:
            cell_start = (pref_cell_start + start_idx_r +
                          separator_cell_start + start_idx_c +
                          suffix_cell_start)
        else:
            cell_start = (pref_cell_start + start_idx_c +
                          separator_cell_start + start_idx_r +
                          suffix_cell_start)

        if GRAMMARS[language]['cells']['aggregation']['start_cell'][
            'rows_only'
        ]:
            cell_start = (pref_cell_start + start_idx_r +
                          separator_cell_start + end_idx_r +
                          suffix_cell_start)
        elif GRAMMARS[language]['cells']['aggregation']['start_cell'][
            'cols_only'
        ]:
            cell_start = (pref_cell_start + start_idx_c +
                          separator_cell_start + end_idx_c +
                          suffix_cell_start)
        # ---------- ending cell -----
        pref_cell_end = GRAMMARS[language]['cells']['aggregation'][
            'end_cell']['prefix']
        separator_cell_end = GRAMMARS[language]['cells']['aggregation'][
            'end_cell']['separator']
        suffix_cell_end = GRAMMARS[language]['cells']['aggregation'][
            'end_cell']['suffix']

        if GRAMMARS[language]['cells']['aggregation']['end_cell'][
            'row_first'
        ]:
            cell_end = (pref_cell_end + end_idx_r +
                        separator_cell_end + end_idx_c +
                        suffix_cell_end)
        else:
            cell_end = (pref_cell_end + end_idx_c +
                        separator_cell_end + end_idx_r +
                        suffix_cell_end)

        if GRAMMARS[language]['cells']['aggregation']['end_cell'][
            'rows_only'
        ]:
            cell_end = (pref_cell_end + start_idx_r +
                        separator_cell_end + end_idx_r +
                        suffix_cell_end)
        elif GRAMMARS[language]['cells']['aggregation']['end_cell'][
            'cols_only'
        ]:
            cell_end = (pref_cell_end + start_idx_c +
                        separator_cell_end + end_idx_c +
                        suffix_cell_end)
        # ----------------------------
        return cell_start, cell_end

    @staticmethod
    def aggregation(cell_start, cell_end,
                    grammar_method: str) -> 'WordConstructor':
        """General aggregation function.

        Args:
            cell_start (Cell): The cell on the position of the slice start.
            cell_end (Cell): The cell on the position of slice end.
            grammar_method (str): Name of the aggregation method in a grammar.

        Returns:
            WordConstructor: World constructed from aggregation method.
        """
        if not(cell_start.anchored and cell_end.anchored):
            raise ValueError("Both starting end ending cells has to be"
                             " anchored!")

        start_idx = cell_start.coordinates
        end_idx = cell_end.coordinates

        instance = WordConstructor(cell_indices=cell_start.cell_indices)
        for language in instance.languages:
            prefix = GRAMMARS[language]['cells']['aggregation']['prefix']
            separator = GRAMMARS[language]['cells']['aggregation']['separator']
            suffix = GRAMMARS[language]['cells']['aggregation']['suffix']

            start, end = WordConstructor._aggregation_parse_cell(
                cell_start, start_idx, end_idx, language
            )
            # Methods
            m_prefix = GRAMMARS[language]['operations'][grammar_method][
                'prefix'
            ]
            m_suffix = GRAMMARS[language]['operations'][grammar_method][
                'suffix'
            ]

            instance.words[language] = (m_prefix + prefix + start +
                                        separator + end + suffix + m_suffix)
        return instance

    @staticmethod
    def parse(cell) -> T_word:
        """Parse the cell word. This function is called when the cell should
            be inserted to spreadsheet.

        Returns:
            T_word: Parsed cell.
        """
        if cell.cell_type == CellType.value_only:
            if cell.value is not None:
                # Constant value
                return copy.deepcopy(WordConstructor.constant(cell).words)
            # Empty value
            return copy.deepcopy(WordConstructor.empty(cell).words)
        elif cell.cell_type == CellType.computational:
            # Computational type
            words: T_word = copy.deepcopy(cell.constructing_words.words)
            for language in cell.constructing_words.languages:
                prefix = GRAMMARS[language]['cells']['operation']['prefix']
                suffix = GRAMMARS[language]['cells']['operation']['suffix']
                words[language] = prefix + words[language] + suffix
            return words

    @staticmethod
    def empty(cell, /) -> 'WordConstructor':  # noqa E225
        """Returns the empty string.

        Args:
            cell (Cell): Empty cell (without any value or computation)

        Returns:
            WordConstructor: Word with empty string.
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            content = GRAMMARS[language]['cells']['empty']['content']
            instance.words[language] = content
        return instance

    @staticmethod
    def reference(cell, /) -> 'WordConstructor':  # noqa E225
        """Return the reference to the cell.

        Args:
            cell (Cell): The cell to which value is referenced.

        Returns:
            WordConstructor: Word with reference
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            prefix = GRAMMARS[language]['cells']['reference']['prefix']
            separator = GRAMMARS[language]['cells']['reference']['separator']
            suffix = GRAMMARS[language]['cells']['reference']['suffix']
            row_first = GRAMMARS[language]['cells']['reference']['row_first']
            # Parse the position to the text of the column and row
            col_parsed = cell.cell_indices.columns[language][cell.column]
            row_parsed = cell.cell_indices.rows[language][cell.row]
            body = prefix + col_parsed + separator + row_parsed + suffix
            if row_first:
                body = prefix + row_parsed + separator + col_parsed + suffix
            instance.words[language] = body
        return instance

    @staticmethod
    def constant(cell, /) -> 'WordConstructor':  # noqa E225
        """Return the value of the cell.

        Args:
            cell (Cell): The cell which value is considered.

        Returns:
            WordConstructor: Word with value.
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            prefix = GRAMMARS[language]['cells']['constant']['prefix']
            suffix = GRAMMARS[language]['cells']['constant']['suffix']
            instance.words[language] = prefix + str(cell.value) + suffix
        return instance

    @staticmethod
    def _unary_operator(*,
                        cell,
                        prefix_path: Tuple[str],
                        suffix_path: Tuple[str]) -> 'WordConstructor':
        """Word creation logic for a general unary operator.

        Args:
            cell (Cell): The cell that is the body of the unary operator.
            prefix_path (Tuple[str]): The path to prefix of the unary operator.
            suffix_path (Tuple[str]): The path to suffix of the unary operator.

        Returns:
            'WordConstructor': Word constructed by the operator.
        """
        instance = copy.deepcopy(cell.word)
        for language in instance.languages:
            prefix = GRAMMARS[language]
            for path_item in prefix_path:
                prefix = prefix[path_item]
            suffix = GRAMMARS[language]
            for path_item in suffix_path:
                suffix = suffix[path_item]
            body = instance.words[language]
            instance.words[language] = prefix + body + suffix
        return instance

    @staticmethod
    def brackets(cell, /) -> 'WordConstructor':  # noqa E225
        """Add brackets around the cell.

        Args:
            cell (Cell): The cell around that brackets are added.

        Returns:
            WordConstructor: Word with brackets.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['brackets', 'prefix'],
            suffix_path=['brackets', 'suffix']
        )

    @staticmethod
    def logarithm(cell, /) -> 'WordConstructor':  # noqa E225
        """Add logarithm definition context around the cell.

        Args:
            cell (Cell): The cell around that logarithm context is added.

        Returns:
            WordConstructor: Word with logarithm context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'logarithm', 'prefix'],
            suffix_path=['operations', 'logarithm', 'suffix']
        )

    @staticmethod
    def exponential(cell, /) -> 'WordConstructor':  # noqa E225
        """Add exponential definition context around the cell.

        Args:
            cell (Cell): The cell around that exponential context is added.

        Returns:
            WordConstructor: Word with exponential context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'exponential', 'prefix'],
            suffix_path=['operations', 'exponential', 'suffix']
        )
