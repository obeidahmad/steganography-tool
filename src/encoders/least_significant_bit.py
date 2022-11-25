from PIL import Image


def string_to_binary(string) -> str:
    binary = ""
    for c in string:
        print(ord(c))
        binary = binary + format(ord(c), '08b')
    return binary


i = 0
message = "ledger"
data = string_to_binary(message)
with Image.open("../../test_images/01.png") as img:
    width, height = img.size
    for x in range(0, width):
        for y in range(0, height):
            pixel = list(img.getpixel((x, y)))
            for n in range(0, 3):
                if i < len(data):
                    pixel[n] = pixel[n] & ~1 | int(data[i])
                    i += 1
            img.putpixel((x, y), tuple(pixel))
    img.save("../../test_images/01_stego.png", "PNG")

