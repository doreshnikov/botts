def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    encrypted_message = ''
    for letter in message:
        if letter.isalpha():
            if letter.isupper():
                encrypted_message += chr((ord(letter) + n - 65) % 26 + 65)
            else:
                encrypted_message += chr((ord(letter) + n - 97) % 26 + 97)
        else:
            encrypted_message += letter
    return encrypted_message
