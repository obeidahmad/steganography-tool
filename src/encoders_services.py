import os

import cv2
from numpy import ndarray

from encoders_decoders import least_significant_bit as lsb
from models.least_significant_bit_technics import LSBTechnics
from utils.custom_exceptions import IncorrectFileTypeException, MissingParameterException, DataTooLongException
from utils.utilities import file_to_binary, string_to_binary, binary_to_string, binary_to_file


def least_significant_bit_encode(cover_path: str, data: str, stego_path: str, encode_type: str, file: bool = True):
    image: ndarray = cv2.imread(cover_path)
    width, height, channels = image.shape
    if image is None:
        raise IncorrectFileTypeException(f"'{cover_path}' is not an image")
    if file:
        if not os.path.exists(data):
            raise FileNotFoundError(f"'{data}' not found")
        binary_data = file_to_binary(data)
    else:
        binary_data = string_to_binary(data)

    # Todo: Study the capability of supporting other file formats
    if not stego_path.endswith(".png"):
        raise IncorrectFileTypeException("Stego File name should be a png")
    os.makedirs(os.path.dirname(stego_path), exist_ok=True)

    match LSBTechnics(encode_type):
        case LSBTechnics.INLINE:
            max_size_data: int = width * height * channels
            if len(binary_data) >= max_size_data:
                raise DataTooLongException(
                    f"Stego data length is bigger than cover image capacity for {encode_type.capitalize()} LSB Algorithm."
                )
            binary_data = str(int(file)) + binary_data.zfill(max_size_data - 1)
            stego_image: ndarray = lsb.inline_encode(cover_image=image, data_to_hide=binary_data)
        case LSBTechnics.EQUI_DISTRIBUTION:
            max_size_data: int = (width * height * channels) - lsb._define_header_length(width, height, channels)
            if len(binary_data) >= max_size_data:
                raise DataTooLongException(
                    f"Stego data length is bigger than cover image capacity for {encode_type.capitalize()} LSB Algorithm."
                )
            binary_data = str(int(file)) + binary_data
            stego_image: ndarray = lsb.equi_distribution_encode(cover_image=image, data_to_hide=binary_data)
        case LSBTechnics.MIDPOINT_CIRCLE:
            max_size_data: int = (
                len(lsb._get_midpoint_circle_positions(image_width=width, image_height=height)) * channels
            )
            if len(binary_data) >= max_size_data:
                raise DataTooLongException(
                    f"Stego data length is bigger than cover image capacity for {encode_type.capitalize()} LSB Algorithm."
                )
            binary_data = str(int(file)) + binary_data.zfill(max_size_data - 1)
            stego_image: ndarray = lsb.midpoint_circle_encode(cover_image=image, data_to_hide=binary_data)

    cv2.imwrite(stego_path, stego_image)


def least_significant_bit_decode(stego_path: str, encode_type: str, result_file_path: str = None) -> str | None:
    image: ndarray = cv2.imread(stego_path)
    if image is None:
        raise IncorrectFileTypeException(f"'{stego_path}' is not an image")

    match LSBTechnics(encode_type):
        case LSBTechnics.INLINE:
            binary_data: str = lsb.inline_decode(stego_image=image)
        case LSBTechnics.EQUI_DISTRIBUTION:
            binary_data: str = lsb.equi_distribution_decode(stego_image=image)
        case LSBTechnics.MIDPOINT_CIRCLE:
            binary_data: str = lsb.midpoint_circle_decode(stego_image=image)

    if binary_data.startswith("0"):
        binary_data = binary_data[1:].lstrip("0")
        while len(binary_data) % 8:
            binary_data = "0" + binary_data
        return binary_to_string(binary=binary_data)
    else:
        if not result_file_path:
            raise MissingParameterException("Please provide path for result file")
        binary_to_file(file_path=result_file_path, binary=binary_data[1:].lstrip("0"))
