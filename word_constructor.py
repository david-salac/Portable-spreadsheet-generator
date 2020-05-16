import copy
from typing import Optional, Dict, Set

from grammars import GRAMMARS

from cell_indices import CellIndices
from cell_type import CellType

T_word = Dict[str, str]


class WordConstructor(object):

    def __init__(self, *,
                 words: T_word = None,
                 languages: Set[str] = None,
                 cell_indices: CellIndices
                 ):
        if words is not None:
            self.words: T_word = words
        else:
            self.words: T_word = {key: "" for key in GRAMMARS.keys()}
        if languages is not None:
            self.languages: Set[str] = languages
        else:
            self.languages: Set[str] = set([key for key in GRAMMARS.keys()])

        self.cell_indices: CellIndices = cell_indices

    @staticmethod
    def brackets(other: 'WordConstructor', /) -> 'WordConstructor':
        words: T_word = {key: other.words[key] for key in GRAMMARS.keys()}
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
        words: T_word = {key: self.words[key] for key in GRAMMARS.keys()}
        for language in other.languages:
            pref = GRAMMARS[language]['operations'][operation]['prefix']
            suff = GRAMMARS[language]['operations'][operation]['suffix']
            sp = GRAMMARS[language]['operations'][operation]['separator']
            words[language] = pref + self.words[language] + sp \
                + other.words[language] + suff
        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def add(self, other: 'WordConstructor', /) -> 'WordConstructor':
        return self._binary_operation(other, "add")

    def subtract(self, other: 'WordConstructor', /) -> 'WordConstructor':
        return self._binary_operation(other, "subtract")

    def multiply(self, other: 'WordConstructor', /) -> 'WordConstructor':
        return self._binary_operation(other, "multiply")

    def divide(self, other: 'WordConstructor', /) -> 'WordConstructor':
        return self._binary_operation(other, "divide")

    def power(self, other: 'WordConstructor', /) -> 'WordConstructor':
        return self._binary_operation(other, "power")

    def constant(self, number: float, /) -> 'WordConstructor':
        words: T_word = {key: self.words[key] for key in GRAMMARS.keys()}
        for language in self.languages:
            prefix = GRAMMARS[language]['cells']['constant']['prefix']
            suffix = GRAMMARS[language]['cells']['constant']['suffix']
            words[language] = prefix + str(number) + suffix
        return WordConstructor(words=words,
                               languages=self.languages,
                               cell_indices=self.cell_indices)

    def parse(self, cell_type: CellType, *, constant_value=None) -> T_word:
        if cell_type == CellType.value_only:
            return copy.deepcopy(self.constant(constant_value).words)
        elif cell_type == CellType.computational:
            words: T_word = copy.deepcopy(self.words)
            for language in self.languages:
                prefix = GRAMMARS[language]['cells']['operation']['prefix']
                suffix = GRAMMARS[language]['cells']['operation']['suffix']
                words[language] = prefix + words[language] + suffix
            return words
