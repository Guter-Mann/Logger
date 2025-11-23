
import string


# TODO: ПЕРЕДЕЛАТЬ!!!


class SafeLogger:
    def __init__(self, message: str):
        self.message = message
        self.words = []

        while True:
            start_index = self.message.find('|')
            end_index = self.message.find('|', start_index+1)
            type_protect = self.message[start_index+1]

            if start_index == -1 or end_index == -1:
                break

            match type_protect:
                case 'N':
                    self._protect_phone_nummder(start_index, end_index)
                case 'E':
                    self._protect_email(start_index, end_index)

    def protect(self):
        return self.message

    def _protect_phone_nummder(self, start_index: int, end_index: int):
        old_phone_number = self.message[start_index:end_index+1]
        new_phone_number = old_phone_number.removeprefix('|N').removesuffix('|')
        for digit in string.digits:
            new_phone_number = new_phone_number.replace(digit, 'X')
        new_phone_number = new_phone_number.replace('+XXX', '+380')
        self.message = self.message.replace(old_phone_number, new_phone_number)

    def _protect_email(self, start_index: int, end_index: int):
        old_email = self.message[start_index:end_index+1]
        email = old_email.removeprefix('|E').removesuffix('|').split('@')
        name_email = email[0]
        index_email = email[1]
        for digit in string.digits + string.ascii_letters:
            name_email = name_email.replace(digit, 'X')
        self.message = self.message.replace(old_email, name_email + '@' + index_email)
