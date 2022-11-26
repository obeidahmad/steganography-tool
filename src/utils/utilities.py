def int_to_binary(integer: int, binary_length: int = None) -> str:
    if not binary_length:
        binary = format(integer, 'b')
    else:
        # Todo: should we raise an Exception ?
        binary = format(integer, f'0{binary_length}b')
        if len(binary) > binary_length:
            print(f"Warning: The binary string is longer than precised binary_length={binary_length}")
            print("Proceeding anyway!")
    return binary


def binary_to_int(binary: str) -> int:
    return int(binary, 2)


def string_to_binary(string: str) -> str:
    binary = ""
    for c in string:
        binary = binary + int_to_binary(ord(c), 8)
    return binary


def binary_to_string(binary) -> str:
    message = ""
    for c in [binary[i:i + 8] for i in range(0, len(binary), 8)]:
        ascii_c = int(c, 2)
        message += chr(ascii_c)
    return message


def file_to_binary(file_path: str) -> str:
    with open(file_path, "rb") as f:
        bin_data: bytes = f.read()
        hex_dump: str = bin_data.hex()
        integer: int = int(hex_dump, 16)
        return bin(integer)


def binary_to_file(file_path: str, binary: str):
    with open(file_path, "wb") as f:
        integer: int = int(binary, 2)
        hex_dump: str = hex(integer)[2:]
        bin_data: bytes = bytes.fromhex(hex_dump)
        f.write(bin_data)
