import os

from encoders_decoders import least_significant_bit as lsb
from encoders_decoders.least_significant_bit import EncodeType
from utils.custom_exceptions import IncorrectFileTypeException, MissingParameterException
from utils.utilities import file_to_binary, string_to_binary, binary_to_string, binary_to_file


def least_significant_bit_encode(
    cover_path: str, data: str, stego_path: str, encode_type: EncodeType, file: bool = True
):
    if file:
        if not os.path.exists(data):
            raise FileNotFoundError(f"'{data}' not found")
        binary_data = "1" + file_to_binary(data)
    else:
        binary_data = "0" + string_to_binary(data)

    # Todo: Study the capability of supporting other file formats
    if not stego_path.endswith(".png"):
        raise IncorrectFileTypeException("Stego File name should be a png")
    os.makedirs(os.path.dirname(stego_path), exist_ok=True)

    lsb.encode(cover_path=cover_path, data_to_hide=binary_data, stego_path=stego_path, encode_type=encode_type)


def least_significant_bit_decode(stego_path: str, encode_type: EncodeType, result_file_path: str = None) -> str | None:
    binary = lsb.decode(stego_path=stego_path, encode_type=encode_type)
    if binary.startswith("0"):
        return binary_to_string(binary[1:])
    else:
        if not result_file_path:
            raise MissingParameterException("Please provide path for result file")
        binary_to_file(result_file_path, binary[1:])
