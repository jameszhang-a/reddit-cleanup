from prompt_toolkit.validation import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a number", cursor_position=len(document.text)
            )  # Move cursor to end
