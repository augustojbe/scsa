def only_digits(value):
    return ''.join(char for char in (value or '') if char.isdigit())
