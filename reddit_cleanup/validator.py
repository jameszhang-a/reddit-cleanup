from email import message
from prompt_toolkit.validation import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document):
        try:
            n = int(document.text)
            if n > 1000:
                raise ValidationError(
                    message="cannot exceed 1000!", cursor_position=len(document.text)
                )
        except ValueError:
            raise ValidationError(
                message="Please enter a number", cursor_position=len(document.text)
            )  # Move cursor to end


class MinimumChoice(Validator):
    def validate(self, document):
        if len(document.text) < 1:
            raise ValidationError(message="There are no selections")
