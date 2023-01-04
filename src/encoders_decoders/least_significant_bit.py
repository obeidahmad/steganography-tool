import math

from numpy import ndarray

from utils.utilities import int_to_binary, binary_to_int


def _define_header_length(image_width: int, image_height: int, nb_channels: int) -> int:
    """
    Defines the length of the header depending on the image width and height

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image
    nb_channels: Number of channels in the image

    Returns
    -------
    The length of the header (number of bits it needs)

    """
    image_dimension: int = image_width * image_height
    max_data_size: int = image_dimension * nb_channels
    header_length: int = len(int_to_binary(max_data_size))
    return header_length


def _define_equidistant_space(
    image_width: int, image_height: int, nb_channels: int, data_length: int, header_length: int
) -> int:
    """
    Calculates the space between each bit for Equi_Distribution LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#equi-distribution-lsb
        for more info about Equi_Distribution LSB

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image
    nb_channels: Number of channels in the image
    data_length: Length of binary data to hide
    header_length: Calculated Length of the header

    Returns
    -------
    The number of bits between each bit of the data to hide

    """
    image_dimension: int = image_width * image_height
    max_data_length: int = (image_dimension * nb_channels) - header_length
    space_between_bits: int = max_data_length // data_length
    return space_between_bits


def _get_midpoint_circle_positions(image_width: int, image_height: int, clockwise: bool = True) -> list[tuple[int, int]]:
    """
    Generates the positions of the pixel where data will be hidden using Midpoint Circle LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#midpoint-circle-lsb
        for more info about Midpoint Circle LSB

    Parameters
    ----------
    image_width: Width of the image
    image_height: Height of the image

    Returns
    -------
    The list of positions (x,y) of the pixels where data will be hidden sorted clockwise or counter-clockwise

    """
    x_center: int = (image_width - 1) // 2
    y_center: int = (image_height - 1) // 2
    radius: int = min(x_center, y_center)

    positions: set[tuple[int, int]] = set()

    x: int = radius
    y: int = 0
    positions.add((x + x_center, y + y_center))
    if radius > 0:
        positions.add((x + x_center, -y + y_center))
        positions.add((y + x_center, x + y_center))
        positions.add((-y + x_center, x + y_center))

    perimeter: int = 1 - radius
    while x > y:
        y += 1
        if perimeter <= 0:
            perimeter = perimeter + 2 * y + 1
        else:
            x -= 1
            perimeter = perimeter + 2 * y - 2 * x + 1
        if x < y:
            break
        positions.add((x + x_center, y + y_center))
        positions.add((-x + x_center, y + y_center))
        positions.add((x + x_center, -y + y_center))
        positions.add((-x + x_center, -y + y_center))
        if x != y:
            positions.add((y + x_center, x + y_center))
            positions.add((-y + x_center, x + y_center))
            positions.add((y + x_center, -x + y_center))
            positions.add((-y + x_center, -x + y_center))

    direction: int = 1 if clockwise else -1
    positions: list[tuple[int, int]] = list(positions)
    positions.sort(key=lambda pos: direction * math.atan2(pos[1] - x_center, pos[0] - y_center))
    return positions


def inline_encode(cover_image: ndarray, data_to_hide: str):
    """
    Hides data in cover image using Inline LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#inline-lsb
        for more info about Inline LSB

    Parameters
    ----------
    cover_image: Cover Image in numpy array format
    data_to_hide: Data to hide in binary string format

    Returns
    -------
    Stego Image in numpy array format

    """
    width, height, channels = cover_image.shape

    flattened_image: ndarray = cover_image.flatten()

    positions: list[int] = list(range(len(flattened_image)))

    for index in positions:
        flattened_image[index] = flattened_image[index] & ~1 | int(data_to_hide[index])

    return flattened_image.reshape((width, height, channels))


def inline_decode(stego_image: ndarray) -> str:
    """
    Extracts hidden data from stego image using Inline LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#inline-lsb
        for more info about Inline LSB

    Parameters
    ----------
    stego_image: Stego image in numpy array format

    Returns
    -------
    The hidden data in string format

    """
    flattened_image: ndarray = stego_image.flatten()

    positions: list[int] = list(range(len(flattened_image)))

    hidden_data: str = ""
    for index in positions:
        hidden_data += str(flattened_image[index] & 1)

    return hidden_data


def equi_distribution_encode(cover_image: ndarray, data_to_hide: str):
    """
    Hides data in cover image using Equi-Distribution LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#equi-distribution-lsb
        for more info about Equi-Distribution LSB

    Parameters
    ----------
    cover_image: Cover Image in numpy array format
    data_to_hide: Data to hide in binary string format

    Returns
    -------
    Stego Image in numpy array format

    """
    width, height, channels = cover_image.shape

    flattened_image: ndarray = cover_image.flatten()

    header_length: int = _define_header_length(image_width=width, image_height=height, nb_channels=channels)
    header_in_binary: str = int_to_binary(len(data_to_hide), header_length)
    positions: list[int] = [
        *range(header_length),
        *range(
            header_length,
            (height * width * channels) + 1,
            _define_equidistant_space(
                image_width=width,
                image_height=height,
                nb_channels=channels,
                data_length=len(data_to_hide),
                header_length=header_length,
            ),
        )[: len(data_to_hide)],
    ]
    data_to_hide = header_in_binary + data_to_hide

    for index in positions:
        flattened_image[index] = flattened_image[index] & ~1 | int(data_to_hide[index])

    return flattened_image.reshape((width, height, channels))


def equi_distribution_decode(stego_image: ndarray) -> str:
    """
    Extracts hidden data from stego image using Equi-Distribution LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#equi-distribution-lsb
        for more info about Equi-Distribution LSB

    Parameters
    ----------
    stego_image: Stego image in numpy array format

    Returns
    -------
    The hidden data in string format

    """
    width, height, channels = stego_image.shape

    flattened_image: ndarray = stego_image.flatten()

    header_length: int = _define_header_length(image_width=width, image_height=height, nb_channels=channels)
    header_positions: list[int] = list(range(header_length))
    header_in_binary: str = ""
    for index in header_positions:
        header_in_binary += str(flattened_image[index] & 1)
    data_length: int = binary_to_int(header_in_binary)
    positions: list[int] = list(
        range(
            header_length,
            (height * width * channels) + 1,
            _define_equidistant_space(
                image_width=width,
                image_height=height,
                nb_channels=channels,
                data_length=data_length,
                header_length=header_length,
            ),
        )[:data_length]
    )

    hidden_data: str = ""
    for index in positions:
        hidden_data += str(flattened_image[index] & 1)

    return hidden_data


def midpoint_circle_encode(cover_image: ndarray, data_to_hide: str):
    """
    Hides data in cover image using Midpoint Circle LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#midpoint-circle-lsb
        for more info about Midpoint Circle LSB

    Parameters
    ----------
    cover_image: Cover Image in numpy array format
    data_to_hide: Data to hide in binary string format

    Returns
    -------
    Stego Image in numpy array format

    """
    width, height, channels = cover_image.shape
    positions: set[tuple[int, int]] = _get_midpoint_circle_positions(image_width=width, image_height=height)

    stego_image: ndarray = cover_image.copy()
    index = 0
    for (x_index, y_index) in positions:
        for chn_index in range(channels):
            stego_image[x_index][y_index][chn_index] = stego_image[x_index][y_index][chn_index] & ~1 | int(
                data_to_hide[index]
            )
            index += 1

    return stego_image


def midpoint_circle_decode(stego_image: ndarray) -> str:
    """
    Extracts hidden data from stego image using Midpoint Circle LSB
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#midpoint-circle-lsb
        for more info about Midpoint Circle LSB

    Parameters
    ----------
    stego_image: Stego image in numpy array format

    Returns
    -------
    The hidden data in string format

    """
    width, height, channels = stego_image.shape
    positions: list[tuple[int, int]] = _get_midpoint_circle_positions(image_width=width, image_height=height)

    hidden_data: str = ""
    for (x_index, y_index) in positions:
        for chn_index in range(channels):
            hidden_data += str(stego_image[x_index][y_index][chn_index] & 1)

    return hidden_data
