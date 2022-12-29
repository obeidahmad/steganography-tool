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
    Returns the length of the header (number of bits it needs)

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
        for more info about equidistant LSB

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


def inline_encode(cover_image: ndarray, data_to_hide: str):
    """
    Hides data in cover image using Inline LSB technics
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#inline-lsb
        for more info about Inline LSB

    Parameters
    ----------
    cover_image: Image loaded with OpenCV
    data_to_hide: Data to hide in binary string format

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
    stego_image: Stego image loaded with OpenCV

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
    Hides data in cover image using Equi-Distribution LSB technics
    Refer to https://github.com/obeidahmad/steganography-tool/blob/main/src/reports/Least%20Significant%20Bit.md/#equi-distribution-lsb
        for more info about Equi-Distribution LSB

    Parameters
    ----------
    cover_image: Image loaded with OpenCV
    data_to_hide: Data to hide in binary string format

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
    stego_image: Stego image loaded with OpenCV

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
