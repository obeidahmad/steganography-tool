from enum import Enum

from PIL import Image

from utils.custom_exceptions import DataTooLongException, MissingParameterException
from utils.utilities import int_to_binary, binary_to_int


class EncodeType(str, Enum):
    INLINE = "inline"
    EQUI_DISTRIBUTION = "equi_distribution"


def encode(cover_path: str, data_to_hide: str, stego_path: str, encode_type: EncodeType):
    """
    Hides data in cover image using one of the LSB technics
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md for
        more info about LSB

    Parameters
    ----------
    cover_path: Path of the cover image
    data_to_hide: Data to hide in binary string format
    stego_path: Path of the output (stego) image
    encode_type: Type of encoding

    """
    with Image.open(cover_path) as img:
        width, height = img.size
        header_length: int = _define_header_length(image_width=width, image_height=height)
        data_length: int = len(data_to_hide)
        if not _is_data_length_allowed(
            image_width=width, image_height=height, data_length=data_length, header_length=header_length
        ):
            raise DataTooLongException("Stego data length is bigger than cover image capacity")
        header: str = int_to_binary(data_length, header_length)
        final_data: str = header + data_to_hide

        match encode_type:
            case EncodeType.INLINE:
                positions: list[tuple] = _get_positions(
                    image_width=width,
                    image_height=height,
                    header_length=header_length,
                    with_header=True,
                    original_data_length=data_length,
                    final_data=final_data,
                )
            case EncodeType.EQUI_DISTRIBUTION:
                positions: list[tuple] = _get_positions(
                    image_width=width,
                    image_height=height,
                    header_length=header_length,
                    with_header=True,
                    original_data_length=data_length,
                    final_data=final_data,
                    space_between_bits=_define_equidistant_space(
                        image_width=width, image_height=height, data_length=data_length, header_length=header_length
                    ),
                )
        for w, h, rgb, b in positions:
            pixel = list(img.getpixel((w, h)))
            pixel[rgb] = pixel[rgb] & ~1 | b
            img.putpixel((w, h), tuple(pixel))

        img.save(stego_path, "PNG")


def decode(stego_path: str, encode_type: EncodeType) -> str:
    """
    Extracts hidden data from stego image using LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md for
        more info about LSB

    Parameters
    ----------
    stego_path: Path of the (stego) image containing the hidden data
    encode_type: Type of encoding

    Returns
    -------
    Returns the extracted data in binary format

    """
    with Image.open(stego_path) as img:
        width, height = img.size
        header_length: int = _define_header_length(width, height)

        header_in_binary: str = ""
        header_positions: list[tuple] = _get_positions(
            image_width=width, image_height=height, header_length=header_length, with_header=True
        )
        for w, h, rgb in header_positions:
            pixel = img.getpixel((w, h))
            header_in_binary += str(pixel[rgb] & 1)
        data_length: int = binary_to_int(header_in_binary)

        data_in_binary: str = ""
        match encode_type:
            case EncodeType.INLINE:
                data_positions: list[tuple] = _get_positions(
                    image_width=width,
                    image_height=height,
                    header_length=header_length,
                    with_header=False,
                    original_data_length=data_length,
                )
            case EncodeType.EQUI_DISTRIBUTION:
                data_positions: list[tuple] = _get_positions(
                    image_width=width,
                    image_height=height,
                    header_length=header_length,
                    with_header=False,
                    original_data_length=data_length,
                    space_between_bits=_define_equidistant_space(
                        image_width=width, image_height=height, data_length=data_length, header_length=header_length
                    ),
                )
        for w, h, rgb in data_positions:
            pixel = img.getpixel((w, h))
            data_in_binary += str(pixel[rgb] & 1)
        return data_in_binary


def _define_header_length(image_width: int, image_height: int) -> int:
    """
    Defines the length of the header depending on the image width and height

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image

    Returns
    -------
    Returns the length of the header (number of bits it needs)

    """
    image_dimension: int = image_width * image_height
    max_data_size: int = image_dimension * 3
    header_length: int = len(int_to_binary(max_data_size))
    return header_length


def _is_data_length_allowed(image_width: int, image_height: int, data_length: int, header_length: int) -> bool:
    """
    Checks if the data to hide length in binary can fit in the image

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image
    data_length: Length of binary data to hide
    header_length: Calculated Length of the header

    Returns
    -------
    True if data fits, False otherwise

    """
    image_dimension: int = image_width * image_height
    max_data_length: int = (image_dimension * 3) - header_length
    return data_length <= max_data_length


def _define_equidistant_space(image_width: int, image_height: int, data_length: int, header_length: int) -> int:
    # todo: change link below to equidistant
    """
    Calculates the space between each bit for Equi_Distribution LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md for
        more info about equidistant LSB

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image
    data_length: Length of binary data to hide
    header_length: Calculated Length of the header

    Returns
    -------
    The number of bits between each bit of the data to hide

    """
    image_dimension: int = image_width * image_height
    max_data_length: int = (image_dimension * 3) - header_length
    space_between_bits: int = max_data_length // data_length
    return space_between_bits


def _get_positions(
    image_width: int,
    image_height: int,
    header_length: int,
    with_header: bool,
    original_data_length: int = 0,
    final_data: str = "",
    space_between_bits: int = 1,
) -> list[tuple]:
    """
    Create a list of positional values to be used for looping on each pixel of the cover image

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image
    header_length: Calculated Length of the header
    with_header: Boolean to specify if the position of the header bit are to be returned
    original_data_length (optional): Length of binary data to hide (without header)
    final_data (optional): Data to hide
    space_between_bits: Calculated space between each bit from data t be hidden

    Returns
    -------
    The positional values in a tuple format (column, row, rgb_position, bit_to_hide_in_that_position)
    bit_to_hide_in_that_position is not included if final_data is not included

    """
    if not header_length:
        raise MissingParameterException("header_length cannot be 0.")

    if final_data and len(final_data) - header_length != original_data_length:
        raise MissingParameterException(
            "The length of final_data, the original_data_length and the header_length do not add up"
        )

    positions: list[int] = []
    if with_header:
        positions.extend(range(header_length))
    if original_data_length > 0:
        positions.extend(
            range(header_length, (image_height * image_width * 3) + 1, space_between_bits)[:original_data_length]
        )
    if not positions:
        raise MissingParameterException("Positions empty!!! Please include with_header or/and original_data_length.")

    height_positions: list[int] = [p // (image_width * 3) for p in positions]
    width_rgb_positions: list[int] = [abs(p - (image_width * 3 * h)) for p, h in zip(positions, height_positions)]
    width_positions: list[int] = [w // 3 for w in width_rgb_positions]
    rgb_positions: list[int] = [w % 3 for w in width_rgb_positions]

    if final_data:
        final_data_int: list[int] = [int(x) for x in final_data]
        return list(zip(width_positions, height_positions, rgb_positions, final_data_int))
    return list(zip(width_positions, height_positions, rgb_positions))
