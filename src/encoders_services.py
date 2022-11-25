import os

from encoders_decoders import least_significant_bit as lsb
from utils.utilities import file_to_binary, string_to_binary


def least_significant_bit_encode(cover_path: str, data: str, stego_path: str, file: bool = True):
    if file:
        if not os.path.exists(data):
            raise FileNotFoundError(f"'{data}' not found")
        binary_data = file_to_binary(data)
    else:
        binary_data = string_to_binary(data)

    # Todo: check stego_path if it ends with ".png"
    lsb.encode(cover_path, binary_data, stego_path)


def least_significant_bit_decode(stego_path: str):
    binary = lsb.decode(stego_path)
    # Todo: transform binary into message or file depending on the need

