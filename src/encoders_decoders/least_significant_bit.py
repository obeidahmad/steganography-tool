from enum import Enum

from PIL import Image

from utils.custom_exceptions import DataTooLongException
from utils.utilities import int_to_binary, binary_to_int


class EncodeType(str, Enum):
    SIMPLE = "inline"
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
            case EncodeType.SIMPLE:
                positions: list[tuple] = _get_positions(
                    image_width=width,
                    data_length=data_length,
                    header_length=header_length,
                    final_data=final_data,
                )
            case EncodeType.EQUI_DISTRIBUTION:
                positions: list[tuple] = _get_positions(
                    image_width=width,
                    data_length=data_length,
                    header_length=header_length,
                    final_data=final_data,
                    space_between_bits=_define_equidistant_space(
                        image_width=width, image_height=height, data_length=data_length, header_length=header_length
                    ),
                )

        for w, h, rgb, b in positions:
            pixel = img.getpixel((w, h))
            pixel[rgb] = pixel[rgb] & ~1 | b
            img.putpixel((w, h), tuple(pixel))

        img.save(stego_path, "PNG")


def decode(stego_path: str) -> str:
    """
    Decode hidden data in image using simple LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md for
        more info about simple LSB

    Parameters
    ----------
    stego_path: The path of the (stego) image containing the hidden data

    Returns
    -------
    Returns the decoded data in binary format

    """
    data = ""
    header = ""
    with Image.open(stego_path) as img:
        width, height = img.size
        header_length: int = _define_header_length(width, height)
        data_length: int = 0

        i = 0
        j = 0
        for x in range(width):
            for y in range(height):
                pixel = list(img.getpixel((x, y)))
                for n in range(3):
                    if i < header_length:
                        header = header + str(pixel[n] & 1)
                        i += 1
                        if i == header_length:
                            data_length = binary_to_int(header)
                    elif j < data_length:
                        data += str(pixel[n] & 1)
                        j += 1
                    else:
                        return data


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
    image_dimension: int = image_width * image_height
    max_data_length: int = (image_dimension * 3) - header_length
    space_between_bits: int = max_data_length // data_length
    return space_between_bits + 1


def _get_positions(
    image_width: int, data_length: int, header_length: int, final_data: str, space_between_bits: int = 1
) -> list[tuple[int, int, int, int]]:
    positions: list[int] = list(range(header_length))
    positions.extend(
        range(header_length, header_length + (space_between_bits * (data_length - 1)) + 1, space_between_bits)
    )
    height_positions: list[int] = [p // (image_width * 3) for p in positions]
    width_rgb_positions: list[int] = [abs(p - (image_width * 3 * h)) for p, h in zip(positions, height_positions)]
    width_positions: list[int] = [w // 3 for w in width_rgb_positions]
    rgb_positions: list[int] = [w % 3 for w in width_rgb_positions]
    final_data: list[int] = [int(x) for x in final_data]

    return list(zip(width_positions, height_positions, rgb_positions, final_data))
