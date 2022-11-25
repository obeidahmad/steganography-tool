from PIL import Image


def binary_to_string(binary) -> str:
    message = ""
    for c in [binary[i:i + 8] for i in range(0, len(binary), 8)]:
        ascii_c = int(c, base=2)
        message = message + chr(ascii_c)
    return message


extracted_bin = []
with Image.open("../../test_images/01_stego.png") as img:
    width, height = img.size
    byte = []
    for x in range(0, width):
        for y in range(0, height):
            pixel = list(img.getpixel((x, y)))
            for n in range(0, 3):
                extracted_bin.append(pixel[n] & 1)

data = "".join([str(x) for x in extracted_bin])
