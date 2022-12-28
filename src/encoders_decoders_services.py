import os

import cv2
from numpy import ndarray

from encoders_decoders import f5, least_significant_bit as lsb
from encoders_decoders.least_significant_bit import EncodeType
from utils.custom_exceptions import IncorrectFileTypeException, MissingParameterException, DataTooLongException
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


def f5_encode(cover_path: str, data: str, stego_path: str, block_size: int = 8, file: bool = True):
    image: ndarray = cv2.imread(cover_path)
    if not image:
        raise IncorrectFileTypeException(f"'{cover_path}' is not an image")
    if block_size <= 0:
        raise MissingParameterException(f"Block size should be bigger than 0")
    max_size_data: int = (image.shape[0] // block_size) * (image.shape[1] // block_size) * image.shape[2]

    if file:
        if not os.path.exists(data):
            raise FileNotFoundError(f"'{data}' not found")
        binary_data = file_to_binary(data)
    else:
        binary_data = string_to_binary(data)

    if len(binary_data) >= max_size_data:
        raise DataTooLongException("Stego data length is bigger than cover image capacity for F5 Algorithm.")
    binary_data = str(int(file)) + binary_data.zfill(max_size_data - 1)

    if not stego_path.endswith(".png"):
        raise IncorrectFileTypeException("Stego File name should be a png")
    os.makedirs(os.path.dirname(stego_path), exist_ok=True)

    stego_image: ndarray = f5.encode(cover_image=image, data_to_hide=binary_data, block_size=block_size)

    cv2.imwrite(stego_path, stego_image)


def f5_decode(stego_path: str, block_size: int = 8, result_file_path: str = None) -> str | None:
    image: ndarray = cv2.imread(stego_path)
    if not image:
        raise IncorrectFileTypeException(f"'{stego_path}' is not an image")
    if block_size <= 0:
        raise MissingParameterException(f"Block size should be bigger than 0")

    binary_data = f5.decode(stego_image=image, block_size=block_size)

    if binary_data.startswith("0"):
        binary_data = binary_data[1:].lstrip("0")
        while len(binary_data) % 8:
            binary_data = "0" + binary_data
        return binary_to_string(binary=binary_data)
    else:
        if not result_file_path:
            raise MissingParameterException("Please provide path for result file")
        binary_to_file(file_path=result_file_path, binary=binary_data[1:].lstrip("0"))
