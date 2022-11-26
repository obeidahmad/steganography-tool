from PIL import Image

from utils.utilities import int_to_binary, binary_to_int


def encode(cover_path: str, data_to_hide: str, stego_path: str):
    # Todo: Option to save the bits in different positions or even in equi-distribution
    with Image.open(cover_path) as img:
        width, height = img.size
        header_length: int = _define_header_length(width, height)
        data_length: int = len(data_to_hide)
        # Todo: create custom exception for the case
        if not _is_data_length_allowed(width, height, data_length, header_length):
            raise Exception("Stego data length is bigger than cover image capacity")
        header: str = int_to_binary(data_length, header_length)

        final_data: str = header + data_to_hide
        i = 0
        for x in range(width):
            for y in range(height):
                pixel = list(img.getpixel((x, y)))
                for n in range(3):
                    if i < len(final_data):
                        pixel[n] = pixel[n] & ~1 | int(final_data[i])
                        i += 1
                    else:
                        img.save(stego_path, "PNG")
                        return
                img.putpixel((x, y), tuple(pixel))


def decode(stego_path: str) -> str:
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
    image_dimension: int = image_width * image_height
    max_data_size: int = image_dimension * 3
    header_length: int = len(int_to_binary(max_data_size))
    return header_length


def _is_data_length_allowed(image_width: int, image_height: int, data_length: int, header_length: int = None) -> bool:
    if not header_length:
        header_length = _define_header_length(image_width, image_height)
    image_dimension: int = image_width * image_height
    max_data_length: int = (image_dimension * 3) - header_length
    return data_length <= max_data_length
