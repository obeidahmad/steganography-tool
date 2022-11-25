def string_to_binary(string: str) -> str:
    binary = ""
    for c in string:
        binary = binary + format(ord(c), '08b')
    return binary


def file_to_binary(file_path: str) -> str:
    with open(file_path, "rb") as f:
        bin_data = f.read()
        hex_dump = bin_data.hex()
        return bin(int(hex_dump, 16))


def binary_to_string(binary) -> str:
    message = ""
    for c in [binary[i:i + 8] for i in range(0, len(binary), 8)]:
        ascii_c = int(c, base=2)
        message = message + chr(ascii_c)
    return message
