import abc


class SerializationInterface(abc.ABC):
    @abc.abstractmethod
    def to_excel(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def to_dictionary(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def to_json(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def generate_json_schema(*args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def to_string_of_values(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def to_list(self, *args, **kwargs):
        raise NotImplementedError
