import copy
from typing import Optional, Dict, Set, Tuple

from .grammars import GRAMMARS

from .cell_indices import CellIndices
from .cell_type import CellType

# ==== TYPES ====
# Type for the word of some language, logic: key: language, value: word
T_word = Dict[str, str]
# ===============


class WordConstructor(object):

    def __init__(self, *,
                 words: T_word = None,
                 languages: Set[str] = None,
                 cell_indices: CellIndices
                 ):
        if languages is not None:
            self.languages: Set[str] = languages
        else:
            self.languages: Set[str] = set(cell_indices.languages)

        if words is not None:
            self.words: T_word = words
        else:
            self.words: T_word = {key: "" for key in self.languages}

        self.cell_indices: CellIndices = cell_indices

    @staticmethod
    def brackets(other: 'WordConstructor', /) -> 'WordConstructor':  # noqa E225
        words: T_word = {key: other.words[key] for key in other.languages}
        for language in other.languages:
            prefix = GRAMMARS[language]['brackets']['prefix']
            suffix = GRAMMARS[language]['brackets']['suffix']
            words[language] = prefix + words[language] + suffix

        return WordConstructor(words=words,
                               languages=other.languages,
                               cell_indices=other.cell_indices)

    @staticmethod
    def init_from_values(col: Optional[int],
                         row: Optional[int],
                         cell_indices: CellIndices,
                         cell_type: CellType,
                         value: Optional[float] = None) -> 'WordConstructor':
        instance = WordConstructor(cell_indices=cell_indices)
        if col is None or row is None:
            if cell_type == CellType.value_only:
                return instance.constant(value)
            return instance
        for language in instance.languages:
            prefix = GRAMMARS[language]['cells']['reference']['prefix']
            separator = GRAMMARS[language]['cells']['reference']['separator']
            suffix = GRAMMARS[language]['cells']['reference']['suffix']
            row_first = GRAMMARS[language]['cells']['reference']['row_first']
            # Parse the position to the text of the column and row
            col_parsed = cell_indices.columns[language][col]
            row_parsed = cell_indices.rows[language][row]
            body = prefix + col_parsed + separator + row_parsed + suffix
            if row_first:
                body = prefix + row_parsed + separator + col_parsed + suffix
            instance.words[language] = body
        return instance

    def _binary_operation(self,
                          other: 'WordConstructor',
                          operation: str) -> 'WordConstructor':
        words: T_word = {key: self.words[key] for key in self.languages}
        for language in other.languages:
            pref = GRAMMARS[language]['operations'][operation]['prefix']
            suff = GRAMMARS[language]['operations'][operation]['suffix']
            sp = GRAMMARS[language]['operations'][operation]['separator']
            words[language] = pref + self.words[language] + sp \
                + other.words[language] + suff
        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def add(self, other: 'WordConstructor', /) -> 'WordConstructor':  # noqa E225
        return self._binary_operation(other, "add")

    def subtract(self, other: 'WordConstructor', /) -> 'WordConstructor':  # noqa E225
        return self._binary_operation(other, "subtract")

    def multiply(self, other: 'WordConstructor', /) -> 'WordConstructor':  # noqa E225
        return self._binary_operation(other, "multiply")

    def divide(self, other: 'WordConstructor', /) -> 'WordConstructor':  # noqa E225
        return self._binary_operation(other, "divide")

    def power(self, other: 'WordConstructor', /) -> 'WordConstructor':  # noqa E225
        return self._binary_operation(other, "power")

    def constant(self, number: float, /) -> 'WordConstructor':  # noqa E225
        words: T_word = {key: self.words[key] for key in self.languages}
        for language in self.languages:
            prefix = GRAMMARS[language]['cells']['constant']['prefix']
            suffix = GRAMMARS[language]['cells']['constant']['suffix']
            words[language] = prefix + str(number) + suffix
        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def _aggregation_parse_cell(self,
                                start_idx: Tuple[int, int],
                                end_idx: Tuple[int, int],
                                language: str
                                ):
        start_idx_r = self.cell_indices.rows[language][start_idx[0]]
        start_idx_c = self.cell_indices.columns[language][start_idx[1]]

        end_idx_r = self.cell_indices.rows[language][end_idx[0]]
        end_idx_c = self.cell_indices.columns[language][end_idx[1]]

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
        # ----------------------------
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

        return cell_start, cell_end

    def aggregation(self,
                    start_idx: Tuple[int, int],
                    end_idx: Tuple[int, int],
                    grammar_method: str) -> 'WordConstructor':
        words: T_word = {key: self.words[key] for key in self.languages}
        for language in self.languages:
            prefix = GRAMMARS[language]['cells']['aggregation']['prefix']
            separator = GRAMMARS[language]['cells']['aggregation']['separator']
            suffix = GRAMMARS[language]['cells']['aggregation']['suffix']

            cell_start, cell_end = self._aggregation_parse_cell(start_idx,
                                                                end_idx,
                                                                language)
            # Methods
            m_prefix = GRAMMARS[language]['operations'][grammar_method][
                'prefix'
            ]
            m_suffix = GRAMMARS[language]['operations'][grammar_method][
                'suffix'
            ]

            words[language] = (m_prefix + prefix + cell_start + separator +
                               cell_end + suffix + m_suffix)
        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def logarithm(self, value: float):
        words: T_word = {key: "" for key in self.languages}
        for language in self.languages:
            prefix = GRAMMARS[language]['operations']['logarithm']['prefix']
            suffix = GRAMMARS[language]['operations']['logarithm']['suffix']

            words[language] = (prefix + str(value) + suffix)

        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def exponential(self, value: float):
        words: T_word = {key: "" for key in self.languages}
        for language in self.languages:
            prefix = GRAMMARS[language]['operations']['exponential']['prefix']
            suffix = GRAMMARS[language]['operations']['exponential']['suffix']

            words[language] = (prefix + str(value) + suffix)

        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def parse(self, cell_type: CellType, *,
              constant_value: Optional[float] = None) -> T_word:
        if cell_type == CellType.value_only:
            return copy.deepcopy(self.constant(constant_value).words)
        elif cell_type == CellType.computational:
            words: T_word = copy.deepcopy(self.words)
            for language in self.languages:
                prefix = GRAMMARS[language]['cells']['operation']['prefix']
                suffix = GRAMMARS[language]['cells']['operation']['suffix']
                words[language] = prefix + words[language] + suffix
            return words
