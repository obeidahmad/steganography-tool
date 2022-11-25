from PIL import Image


def encode(cover_path: str, data_to_hide: str, stego_path: str):
    # Todo: Get the length of data and save the length in a predefined position to be discussed.
    #  The predefined position should also be of predefined length so it be read everytime.
    #  We may also use that position to store more information, like the name of the file that is being hidden.
    #  Or at least the extension of the file.

    # Todo: Option to save the bits in different positions or even in equi-distribution
    i = 0
    with Image.open(cover_path) as img:
        width, height = img.size
        for x in range(width):
            for y in range(height):
                pixel = list(img.getpixel((x, y)))
                for n in range(3):
                    if i < len(data_to_hide):
                        pixel[n] = pixel[n] & ~1 | int(data_to_hide[i])
                        i += 1
                img.putpixel((x, y), tuple(pixel))
        img.save(stego_path, "PNG")


def decode(stego_path: str) -> str:
    extracted_bin = []
    with Image.open(stego_path) as img:
        width, height = img.size
        byte = []
        for x in range(0, width):
            for y in range(0, height):
                pixel = list(img.getpixel((x, y)))
                for n in range(0, 3):
                    extracted_bin.append(pixel[n] & 1)
    data = "".join([str(x) for x in extracted_bin])
    return data
