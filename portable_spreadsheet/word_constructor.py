import copy
from collections import defaultdict
from numbers import Number
from typing import Dict, Set, Tuple, List, Optional

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
        cell_indices (CellIndices): Indices in all languages.
        row_indices (Dict[str, List[int]]): Dictionary in logic language ->
            row indices (as integer position) of anchored cell in body of
            the word. Required for parsing of the words for each language.
        column_indices (Dict[str, List[int]]): Dictionary in logic language ->
            column indices (as integer position) of anchored cell in body of
            the word. Required for parsing of the words for each language.
        row_aggregation_interval (List[Tuple[int, int]]): Indices intervals of
            aggregations in row indices space of anchored cells
        column_aggregation_interval (List[Tuple[int, int]]): Indices intervals
            of aggregations in column indices space of anchored cells
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

        self.cell_indices: CellIndices = cell_indices
        self.row_indices: Dict[str, List[int]] = defaultdict(list)
        self.column_indices: Dict[str, List[int]] = defaultdict(list)
        self.row_aggregation_interval: List[Tuple[int, int]] = []
        self.column_aggregation_interval: List[Tuple[int, int]] = []

    def append_indices(
            self,
            row_indices: List[int],
            column_indices: List[int],
            language: Optional[str]
    ) -> None:
        """Append the cell indices.

        Args:
            column_indices (List[int]): New column indices to be appended.
            row_indices (List[int]): New row indices to be appended.
            language (Optional[str]): Language to what indices are appended.
                If None, append to all languages.
        """
        if language is not None:
            self.row_indices[language].extend(row_indices)
            self.column_indices[language].extend(column_indices)
        else:
            for language in self.languages:
                self.row_indices[language].extend(row_indices)
                self.column_indices[language].extend(column_indices)

    def affect_aggregation(self,
                           row_index: Optional[int] = None,
                           column_index: Optional[int] = None) -> bool:
        """Test if modification of some column or row (or both) index
            affects aggregation formulas of this cell.

        Args:
            row_index (int): Probed index of the row (integer position).
            column_index (int): Probed index of the column (integer position).

        Returns:
            bool: returns true if some aggregation is affected
        """
        if row_index is not None:
            for indices_range in self.row_aggregation_interval:
                if indices_range[0] <= row_index <= indices_range[1]:
                    return True

        if column_index is not None:
            for indices_range in self.column_aggregation_interval:
                if indices_range[0] <= column_index <= indices_range[1]:
                    return True

        return False

    def affect_indices(self,
                       row_index: Optional[int] = None,
                       column_index: Optional[int] = None) -> bool:
        """Test if modification of some column or row (or both) index
            has any impact on the current cell.

        Args:
            row_index (int): Probed index of the row (integer position).
            column_index (int): Probed index of the column (integer position).

        Returns:
            bool: returns true if some index is affected (causes incosistent
                table)
        """
        if row_index is not None:
            return row_index in self.row_indices

        if column_index is not None:
            return column_index in self.column_indices

        return False

    def delete(self,
               row_index: Optional[int] = None,
               column_index: Optional[int] = None) -> None:
        """Delete row or (and) column on defined integer position.

        Args:
            row_index (int): Probed index of the row (integer position).
            column_index (int): Probed index of the row (integer position).
        """
        # For simple indices
        # Delete row
        for i in range(len(self.row_indices)):
            if self.row_indices[i] > row_index:
                self.row_indices[i] -= 1
        # Delete column
        for i in range(len(self.column_indices)):
            if self.row_indices[i] > row_index:
                self.row_indices[i] -= 1

        # For aggregation
        # Delete row
        if row_index is not None:
            for i in len(self.row_aggregation_interval):
                if self.row_aggregation_interval[i][0] > row_index:
                    self.row_aggregation_interval[i] = (
                        self.row_aggregation_interval[i][0] - 1,
                        self.row_aggregation_interval[i][1] - 1
                    )
        # Delete column
        if column_index is not None:
            for i in len(self.column_aggregation_interval):
                if self.column_aggregation_interval[i][0] > column_index:
                    self.column_aggregation_interval[i] = (
                        self.column_aggregation_interval[i][0] - 1,
                        self.column_aggregation_interval[i][1] - 1
                    )

    def indices_for_languages(self) -> Dict[str, Tuple[List[str], List[str]]]:
        """Get the indices string representation in each language.

        Returns:
            Dict[str, Tuple[List[str], List[str]]]: language -> (row indices,
                column indices)
        """
        indices: Dict[str, Tuple[List[str], List[str]]] = {}

        for language in self.languages:
            indices_row: List[str] = []
            indices_col: List[str] = []
            for row_i in self.row_indices[language]:
                indices_row.append(
                    self.cell_indices.rows[language][row_i]
                )

            for col_i in self.column_indices[language]:
                indices_col.append(self.cell_indices.columns[language][col_i])
            indices[language] = (indices_row, indices_col)

        return indices

    @staticmethod
    def init_from_new_cell(cell, /) -> 'WordConstructor':  # noqa: E999, E225
        """Initialise the words when the new cell is created.

        Args:
            cell (Cell): just created cell.

        Returns:
            WordConstructor: words for the new cell.
        """
        if cell.value is not None:
            # Value type cell
            new_cell = WordConstructor.constant(cell, new_cell=True)
        else:
            # Empty cell
            new_cell = WordConstructor.empty(cell, new_cell=True)

        # Initialise the position
        if cell.anchored:
            new_cell.append_indices([cell.row], [cell.column], language=None)
        return new_cell

    @staticmethod
    def _binary_operation(first,
                          second,
                          operation: str) -> 'WordConstructor':
        """General binary operation.

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.
            operation (str): Definition of the operation (in grammar).

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        instance = WordConstructor(cell_indices=first.cell_indices)
        first_words = first.word.words
        second_word = second.word.words
        for language in instance.languages:
            pref = GRAMMARS[language]['operations'][operation]['prefix']
            suff = GRAMMARS[language]['operations'][operation]['suffix']
            sp = GRAMMARS[language]['operations'][operation]['separator']
            instance.words[language] = pref + first_words[language] + sp \
                + second_word[language] + suff

            instance.append_indices(
                first.constructing_words.row_indices[language],
                first.constructing_words.column_indices[language],
                language=language
            )
            instance.append_indices(
                second.constructing_words.row_indices[language],
                second.constructing_words.column_indices[language],
                language=language
            )

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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def modulo(first, second, /) -> 'WordConstructor':  # noqa E225
        """Modulo binary operation (%).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "modulo")

    @staticmethod
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
    def logicalConjunction(first,
                           second, /) -> 'WordConstructor':  # noqa E225
        """Logical conjunction operation (and).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second,
                                                 "logical-conjunction")

    @staticmethod
    def logicalDisjunction(first,
                           second, /) -> 'WordConstructor':  # noqa E225
        """Logical disjunction operation (or).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second,
                                                 "logical-disjunction")

    @staticmethod
    def equalTo(first, second, /) -> 'WordConstructor':  # noqa E225
        """Equal to binary operation (==).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "equal-to")

    @staticmethod
    def notEqualTo(first, second, /) -> 'WordConstructor':  # noqa E225
        """Not equal to binary operation (!=).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "not-equal-to")

    @staticmethod
    def greaterThan(first,
                    second, /) -> 'WordConstructor':  # noqa E225
        """Greater than binary operation (>).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "greater-than")

    @staticmethod
    def greaterThanOrEqualTo(first,
                             second, /) -> 'WordConstructor':  # noqa E225
        """Greater than or equal to binary operation (>=).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second,
                                                 "greater-than-or-equal-to")

    @staticmethod
    def lessThan(first, second, /) -> 'WordConstructor':  # noqa E225
        """Less than binary operation (<).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second, "less-than")

    @staticmethod
    def lessThanOrEqualTo(first,
                          second, /) -> 'WordConstructor':  # noqa E225
        """Less than or equal to binary operation (<=).

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator and two
                operands.
        """
        return WordConstructor._binary_operation(first, second,
                                                 "less-than-or-equal-to")

    @staticmethod
    def concatenate(first,
                    second) -> 'WordConstructor':
        """Concatenate values as two strings and create a word.

        Args:
            first (Cell): The first cell (operand) of the operator.
            second (Cell): The second cell (operand) of the operator.

        Returns:
            WordConstructor: Word constructed using binary operator concatenate
                and two operands.
        """
        # Inline function for appending context to inputs
        def _generate_word_string_concatenate(in_cell) -> T_word:
            """Generate word for each operand.

            Returns:
                T_word: Words for each language.
            """
            if in_cell.anchored:
                return WordConstructor.reference(in_cell).words
            else:
                if in_cell.cell_type == CellType.computational:
                    return in_cell._constructing_words.words
                elif in_cell.cell_type == CellType.value_only:
                    words: T_word = {}
                    for language in instance.languages:
                        if isinstance(in_cell.value, str):
                            pref = GRAMMARS[language]['operations'][
                                'concatenate']['string-value']['prefix']
                            suff = GRAMMARS[language]['operations'][
                                'concatenate']['string-value']['suffix']
                            words[language] = pref + str(in_cell.value) + suff
                        if isinstance(in_cell.value, Number):
                            pref = GRAMMARS[language]['operations'][
                                'concatenate']['numeric-value']['prefix']
                            suff = GRAMMARS[language]['operations'][
                                'concatenate']['numeric-value']['suffix']
                            words[language] = pref + str(in_cell.value) + suff
                    return words

        instance = WordConstructor(cell_indices=first.cell_indices)
        first_words = _generate_word_string_concatenate(first)
        second_word = _generate_word_string_concatenate(second)
        for language in instance.languages:
            pref = GRAMMARS[language]['operations']['concatenate']['prefix']
            suff = GRAMMARS[language]['operations']['concatenate']['suffix']
            sp = GRAMMARS[language]['operations']['concatenate']['separator']
            instance.words[language] = pref + first_words[language] + sp \
                + second_word[language] + suff
            # Append indices
            instance.append_indices(
                first.constructing_words.row_indices[language],
                first.constructing_words.column_indices[language],
                language=language
            )
            instance.append_indices(
                second.constructing_words.row_indices[language],
                second.constructing_words.column_indices[language],
                language=language
            )
        return instance

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
        # Does the language include the last cell?
        #   if yes, offset of size 1 has to be included.
        offset = 0
        if GRAMMARS[
            language
        ]['cells']['aggregation']['include_last_cell']:
            offset = 1

        start_idx_r = cell.cell_indices.rows[language][start_idx[0]]
        start_idx_c = cell.cell_indices.columns[language][start_idx[1]]
        end_idx_r = cell.cell_indices.rows[language][end_idx[0] + offset]
        end_idx_c = cell.cell_indices.columns[language][end_idx[1] + offset]

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

        Args:
            cell (Cell): The cell that is the subject of parsing.

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
            lang_idx = cell.constructing_words.indices_for_languages()
            # Computational type
            words: T_word = defaultdict(str)
            for language in cell.constructing_words.languages:
                prefix = GRAMMARS[language]['cells']['operation']['prefix']
                suffix = GRAMMARS[language]['cells']['operation']['suffix']
                body = cell.constructing_words.words[language]
                body = body.replace("‹Č›", '{}').format(
                    *(lang_idx[language][1])
                )
                body = body.replace('‹Ř›', '{}').format(
                    *(lang_idx[language][0])
                )
                words[language] = prefix + body + suffix
            return words

    @staticmethod
    def raw(cell, words: T_word, /) -> 'WordConstructor':  # noqa: E225
        """Returns the raw statement string.

        Args:
            cell (Cell): Some cell.
            words (T_word): Custom word definition

        Returns:
            WordConstructor: Defined word.
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            instance.words[language] = words[language]

        # Create references to the columns/rows - skipped for raw statement
        return instance

    @staticmethod
    def empty(cell, /, *,  # noqa: E225
              new_cell: bool = False) -> 'WordConstructor':
        """Returns the empty string.

        Args:
            cell (Cell): Empty cell (without any value or computation)
            new_cell (bool): If true, new constant cell is created, if
                false, standard constant cell is returned.

        Returns:
            WordConstructor: Word with empty string.
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            content = GRAMMARS[language]['cells']['empty']['content']
            instance.words[language] = content

            if not new_cell:
                # Technically deep copy indices
                instance.append_indices(
                    cell.constructing_words.row_indices[language],
                    cell.constructing_words.column_indices[language],
                    language=language
                )
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
            body = prefix + '‹Č›' + separator + '‹Ř›' + suffix
            if row_first:
                body = prefix + '‹Ř›' + separator + '‹Č›' + suffix
            instance.words[language] = body

            # Technically deep copy indices
            instance.append_indices(
                cell.constructing_words.row_indices[language],
                cell.constructing_words.column_indices[language],
                language=language
            )
        return instance

    @staticmethod
    def constant(cell, /, *,  # noqa: E225
                 new_cell: bool = False) -> 'WordConstructor':
        """Return the value of the cell.

        Args:
            cell (Cell): The cell which value is considered.
            new_cell (bool): If true, new constant cell is created, if
                false, standard constant cell is returned.

        Returns:
            WordConstructor: Word with value.
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            prefix = GRAMMARS[language]['cells']['constant']['prefix']
            suffix = GRAMMARS[language]['cells']['constant']['suffix']
            instance.words[language] = prefix + str(cell.value) + suffix

            if not new_cell:
                # Technically deep copy indices
                instance.append_indices(
                    cell.constructing_words.row_indices[language],
                    cell.constructing_words.column_indices[language],
                    language=language
                )
        return instance

    @staticmethod
    def variable(cell, /) -> 'WordConstructor':  # noqa E225
        """Return the cell as a variable.

        Args:
            cell (Cell): The cell which is considered as a variable.

        Returns:
            WordConstructor: Word with variable.
        """
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            prefix = GRAMMARS[language]['cells']['variable']['prefix']
            suffix = GRAMMARS[language]['cells']['variable']['suffix']
            # Now add the value as a suffix if required
            value_word = ""
            value_grammar = GRAMMARS[language]['cells']['variable']['value']
            if value_grammar['include']:
                value_word += value_grammar['prefix']
                value_word += str(cell.value)
                value_word += value_grammar['suffix']
            # Construct the whole word
            instance.words[language] = (prefix + cell.variable_name
                                        + value_word + suffix)

            # Technically deep copy indices
            instance.append_indices(
                cell.constructing_words.row_indices[language],
                cell.constructing_words.column_indices[language],
                language=language
            )
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
        instance = WordConstructor(cell_indices=cell.cell_indices)
        for language in instance.languages:
            prefix = GRAMMARS[language]
            for path_item in prefix_path:
                prefix = prefix[path_item]
            suffix = GRAMMARS[language]
            for path_item in suffix_path:
                suffix = suffix[path_item]
            body = cell.word.words[language]
            instance.words[language] = prefix + body + suffix

            # Technically deep copy indices
            instance.append_indices(
                cell.constructing_words.row_indices[language],
                cell.constructing_words.column_indices[language],
                language=language
            )
        return instance

    @staticmethod
    def brackets(cell, /) -> 'WordConstructor':  # noqa E225
        """Add brackets around the cell.

        Args:
            cell (Cell): The cell around which brackets are added.

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
            cell (Cell): The cell around which logarithm context is added.

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
            cell (Cell): The cell around which exponential context is added.

        Returns:
            WordConstructor: Word with exponential context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'exponential', 'prefix'],
            suffix_path=['operations', 'exponential', 'suffix']
        )

    @staticmethod
    def ceil(cell, /) -> 'WordConstructor':  # noqa E225
        """Add ceiling function definition context around the cell.

        Args:
            cell (Cell): The cell around which ceiling fn. context is added.

        Returns:
            WordConstructor: Word with ceiling function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'ceil', 'prefix'],
            suffix_path=['operations', 'ceil', 'suffix']
        )

    @staticmethod
    def floor(cell, /) -> 'WordConstructor':  # noqa E225
        """Add floor function definition context around the cell.

        Args:
            cell (Cell): The cell around which floor fn. context is added.

        Returns:
            WordConstructor: Word with floor function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'floor', 'prefix'],
            suffix_path=['operations', 'floor', 'suffix']
        )

    @staticmethod
    def round(cell, /) -> 'WordConstructor':  # noqa E225
        """Add rounding function definition context around the cell.

        Args:
            cell (Cell): The cell around which rounding fn. context is added.

        Returns:
            WordConstructor: Word with rounding function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'round', 'prefix'],
            suffix_path=['operations', 'round', 'suffix']
        )

    @staticmethod
    def abs(cell, /) -> 'WordConstructor':  # noqa E225
        """Add absolute value definition context around the cell.

        Args:
            cell (Cell): The cell around which absolute value context is added.

        Returns:
            WordConstructor: Word with absolute value function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'abs', 'prefix'],
            suffix_path=['operations', 'abs', 'suffix']
        )

    @staticmethod
    def sqrt(cell, /) -> 'WordConstructor':  # noqa E225
        """Add square root value definition context around the cell.

        Args:
            cell (Cell): The cell around which square root context is added.

        Returns:
            WordConstructor: Word with square root function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'sqrt', 'prefix'],
            suffix_path=['operations', 'sqrt', 'suffix']
        )

    @staticmethod
    def signum(cell, /) -> 'WordConstructor':  # noqa E225
        """Add signum value definition context around the cell.

        Args:
            cell (Cell): The cell around which signum context is added.

        Returns:
            WordConstructor: Word with signum function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'signum', 'prefix'],
            suffix_path=['operations', 'signum', 'suffix']
        )

    @staticmethod
    def logicalNegation(cell, /) -> 'WordConstructor':  # noqa E225
        """Add logical negation definition context around the cell.

        Args:
            cell (Cell): The cell around which logical negation context is
                added.

        Returns:
            WordConstructor: Word with logical negation function context.
        """
        return WordConstructor._unary_operator(
            cell=cell,
            prefix_path=['operations', 'logical-negation', 'prefix'],
            suffix_path=['operations', 'logical-negation', 'suffix']
        )

    @staticmethod
    def conditional(condition,
                    consequent,
                    alternative, /) -> 'WordConstructor':  # noqa E225
        """Construct the word for the conditional statement (if-then-else).

        Args:
            condition (Cell): condition statement.
            consequent (Cell): value if the condition is true.
            alternative (Cell): value if the condition is false.

        Returns:
            WordConstructor: Word for the conditional statement
        """
        instance = WordConstructor(cell_indices=condition.cell_indices)

        w_condition = condition.word.words
        w_consequent = consequent.word.words
        w_alternative = alternative.word.words

        for language in instance.languages:
            conditional_prefix = GRAMMARS[language]['conditional']['prefix']
            conditional_suffix = GRAMMARS[language]['conditional']['suffix']

            condition_prefix = GRAMMARS[language][
                'conditional']['condition']['prefix']
            condition_suffix = GRAMMARS[language][
                'conditional']['condition']['suffix']
            condition_word = condition_prefix + w_condition[language] + \
                condition_suffix

            consequent_prefix = GRAMMARS[language][
                'conditional']['consequent']['prefix']
            consequent_suffix = GRAMMARS[language][
                'conditional']['consequent']['suffix']
            consequent_word = consequent_prefix + w_consequent[language] + \
                consequent_suffix

            alternative_prefix = GRAMMARS[language][
                'conditional']['alternative']['prefix']
            alternative_suffix = GRAMMARS[language][
                'conditional']['alternative']['suffix']
            alternative_word = alternative_prefix + w_alternative[language] + \
                alternative_suffix

            # Swap the words to desired sequence
            clausules_order = GRAMMARS[language]['conditional']['order']
            prefered_order = ('condition', 'consequent', 'alternative')
            words_in_prefered_order = (condition_word, consequent_word,
                                       alternative_word)
            row_idx_in_prefered_order = (
                condition.constructing_words.row_indices[language],
                consequent.constructing_words.row_indices[language],
                alternative.constructing_words.row_indices[language],
            )
            col_idx_in_prefered_order = (
                condition.constructing_words.column_indices[language],
                consequent.constructing_words.column_indices[language],
                alternative.constructing_words.column_indices[language],
            )

            words_in_correct_order = ["", "", ""]
            row_idx_in_correct_order = [[], [], []]
            col_idx_in_correct_order = [[], [], []]
            # Do the permutation and construct the word:
            for clausule_idx, clausule in enumerate(prefered_order):
                # Words
                clausule_permutated_idx = clausules_order.index(clausule)
                words_in_correct_order[clausule_permutated_idx] = \
                    words_in_prefered_order[clausule_idx]
                # Rows/column indices
                row_idx_in_correct_order[clausule_permutated_idx] = \
                    row_idx_in_prefered_order[clausule_idx]
                col_idx_in_correct_order[clausule_permutated_idx] = \
                    col_idx_in_prefered_order[clausule_idx]

            # Merge words into one word
            final_word = "".join(words_in_correct_order)

            instance.words[language] = conditional_prefix + final_word + \
                conditional_suffix
            for i in range(len(col_idx_in_correct_order)):
                instance.append_indices(row_idx_in_correct_order[i],
                                        col_idx_in_correct_order[i],
                                        language=language)
        return instance

    @staticmethod
    def offset(reference,
               row_skip,
               column_skip, /) -> 'WordConstructor':  # noqa E225
        """Construct the word for the offset statement (skip n rows and m
            columns from the referential position).

        Args:
            reference (Cell): Reference cell from that the position is
                computed.
            row_skip (Cell): How many rows (down) should be skipped.
            column_skip (Cell): How many columns (left) should be skipped.

        Returns:
            WordConstructor: Word for the offset statement.
        """
        instance = WordConstructor(cell_indices=reference.cell_indices)

        ref_row_skip = row_skip.word.words
        ref_col_skip = column_skip.word.words

        for language in instance.languages:
            offset_prefix = GRAMMARS[language]['cells']['offset']['prefix']
            offset_suffix = GRAMMARS[language]['cells']['offset']['suffix']

            ref_row_prefix = GRAMMARS[language]['cells']['offset'][
                'reference-cell-row']['prefix']
            ref_row_suffix = GRAMMARS[language]['cells']['offset'][
                'reference-cell-row']['suffix']
            ref_row_word = (ref_row_prefix +
                            '‹Ř›' +
                            ref_row_suffix)

            ref_col_prefix = GRAMMARS[language]['cells']['offset'][
                'reference-cell-column']['prefix']
            ref_col_suffix = GRAMMARS[language]['cells']['offset'][
                'reference-cell-column']['suffix']
            ref_col_word = (ref_col_prefix +
                            '‹Č›' +
                            ref_col_suffix)
            # HERE USING REFERENCE
            skip_row_prefix = GRAMMARS[language]['cells']['offset'][
                'skip-of-rows']['prefix']
            skip_row_suffix = GRAMMARS[language]['cells']['offset'][
                'skip-of-rows']['suffix']
            skip_row_word = (skip_row_prefix +
                             ref_row_skip[language] +
                             skip_row_suffix)

            skip_col_prefix = GRAMMARS[language]['cells']['offset'][
                'skip-of-columns']['prefix']
            skip_col_suffix = GRAMMARS[language]['cells']['offset'][
                'skip-of-columns']['suffix']
            skip_col_word = (skip_col_prefix +
                             ref_col_skip[language] +
                             skip_col_suffix)

            # Swap the words to desired sequence
            clausules_order = GRAMMARS[language]['cells']['offset']['order']
            prefered_order = ('reference-cell-row', 'reference-cell-column',
                              'skip-of-rows', 'skip-of-columns')
            words_in_prefered_order = (ref_row_word, ref_col_word,
                                       skip_row_word, skip_col_word)
            row_idx_in_prefered_order = (
                reference.constructing_words.row_indices[language],
                reference.constructing_words.row_indices[language],
                row_skip.constructing_words.row_indices[language],
                column_skip.constructing_words.row_indices[language],
            )
            col_idx_in_prefered_order = (
                reference.constructing_words.column_indices[language],
                reference.constructing_words.column_indices[language],
                row_skip.constructing_words.column_indices[language],
                column_skip.constructing_words.column_indices[language],
            )

            words_in_correct_order = ["", "", "", ""]
            row_idx_in_correct_order = [[], [], [], []]
            col_idx_in_correct_order = [[], [], [], []]
            # Do the permutation and construct the word:
            for clausule_idx, clausule in enumerate(prefered_order):
                # Words
                clausule_permutated_idx = clausules_order.index(clausule)
                words_in_correct_order[clausule_permutated_idx] = \
                    words_in_prefered_order[clausule_idx]
                # Rows/column indices
                if clausule == 'reference-cell-row':
                    row_idx_in_correct_order[clausule_permutated_idx] = \
                        row_idx_in_prefered_order[clausule_idx]
                elif clausule == 'reference-cell-column':
                    col_idx_in_correct_order[clausule_permutated_idx] = \
                        col_idx_in_prefered_order[clausule_idx]
                else:
                    row_idx_in_correct_order[clausule_permutated_idx] = \
                        row_idx_in_prefered_order[clausule_idx]
                    col_idx_in_correct_order[clausule_permutated_idx] = \
                        col_idx_in_prefered_order[clausule_idx]

            # Merge words into one word
            final_word = "".join(words_in_correct_order)

            instance.words[language] = offset_prefix + final_word + \
                offset_suffix
            # Add row/column indices
            for i in range(len(col_idx_in_correct_order)):
                instance.append_indices(row_idx_in_correct_order[i],
                                        col_idx_in_correct_order[i],
                                        language=language)
        return instance
