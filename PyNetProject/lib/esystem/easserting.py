class EAssert:
    class Argument:

        @staticmethod
        def is_not_none(value, argument_name=None):
            EAssert.is_not_none(value,
                                "Argument is null." if argument_name == None else f"Argument '{argument_name}' is null.")

        @staticmethod
        def is_type(value, value_type, argument_name=None):
            EAssert.is_type(value, value_type,
                            None if argument_name is None else f"'{argument_name}' is not of required type '{value_type}'.")

        @staticmethod
        def is_true(value, argument_name=None):
            EAssert.is_true(value,
                            None if argument_name is None else f"Expression with argument '{argument_name}' must be true.")

        @staticmethod
        def is_false(value, argument_name=None):
            EAssert.is_false(value,
                             None if argument_name is None else f"Expression with argument '{argument_name}' must be false.")

        @staticmethod
        def is_nonempty_string(value: str, argument_name=None):
            EAssert.is_nonempty_string(value,
                                       None if argument_name else f"Argument '{argument_name}' must be non-empty string.")

    @staticmethod
    def equals(value_a, value_b, message="Values must be equal."):
        if not(value_a == value_b):
            raise EAssertException(message)

    @staticmethod
    def is_nonempty_string(value: str, message="Value must be non-empty string."):
        if value is None or len(value) == 0:
            raise EAssertException(message)

    @staticmethod
    def is_not_none(value, message="Value is null."):
        if value is None:
            raise EAssertException(message)

    @staticmethod
    def is_none(value, message="Value is not null."):
        if value is not None:
            raise EAssertException(message)

    @staticmethod
    def is_type(value, value_type, message=None):
        if type(value) != value_type:
            if message is None:
                raise EAssertException(f"Value is not of required type '{value_type}'.")
            else:
                raise EAssertException(message)

    @staticmethod
    def is_true(value, message=None):
        if not value:
            if message is None:
                raise EAssertException("Value must be true.")
            else:
                raise EAssertException(message)

    @staticmethod
    def is_false(value, message=None):
        if value:
            if message is None:
                raise EAssertException("Value must be false.")
            else:
                raise EAssertException(message)


class EAssertException(Exception):
    pass
