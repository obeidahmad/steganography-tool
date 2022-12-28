import cv2
import einops
import numpy as np
from numpy import ndarray

from utils.utilities import string_to_binary, binary_to_string


def encode(cover_image: ndarray, data_to_hide: str, block_size: int = 8) -> ndarray:
    """
    Encode data into image using F5 algorithm

    Parameters
    ----------
    cover_image: Image loaded with OpenCV
    data_to_hide: Data to hide in binary string format
    block_size: Size of block

    Returns
    -------
    Stego image in ndarray format (to be saved using OpenCV imwrite)

    """
    # Initialization
    nb_channels: int = cover_image.shape[2]

    # Crop image to be able to decompose later.
    block_shape: ndarray = np.array((block_size, block_size, nb_channels))
    nb_blocks: ndarray = np.array(cover_image.shape) // block_shape
    crop_r, crop_c, crop_ch = nb_blocks * block_shape
    cropped_image: ndarray = cover_image[:crop_r, :crop_c, :crop_ch]

    # Split the image channels
    splat_cropped_image = cv2.split(cropped_image)

    # Decompose each channel into blocks
    channel_blocks = [
        np.array([x for y in blocks for x in y])
        for blocks in [
            einops.rearrange(channel_image, "(x dx) (y dy) -> x y dx dy", dx=block_size, dy=block_size)
            for channel_image in splat_cropped_image
        ]
    ]

    # Merge each channel block into 1D array of blocks
    blocks = [x for y in zip(*channel_blocks) for x in y]

    # Encode the message in the blocks using the F5 algorithm
    for block_index, bit in zip(range(len(blocks)), data_to_hide):
        dct = cv2.dct(np.float32(blocks[block_index]))
        dct[-1][-1] = int(bit) * 15
        blocks[block_index] = cv2.idct(dct)

    # Split 1D array of blocks back into blocks for each of the 3 channels
    n_channel_blocks = [[] for _ in range(nb_channels)]
    for index in range(0, len(blocks), nb_channels):
        for i in range(0, nb_channels):
            n_channel_blocks[i].append(blocks[index + i])
    nb_blocks_height = cropped_image.shape[1] // block_size
    n_channel_blocks = [
        np.array([blocks[i : i + nb_blocks_height] for i in range(0, len(blocks), nb_blocks_height)])
        for blocks in n_channel_blocks
    ]

    # Assemble the modified blocks back into an image
    modified_image = cv2.merge(
        [einops.rearrange(channel_block, "x y dx dy -> (x dx) (y dy)") for channel_block in n_channel_blocks]
    )

    # Restore cropped parts
    stego_image = cover_image.copy()
    stego_image[0 : cropped_image.shape[0], 0 : cropped_image.shape[1]] = modified_image

    return stego_image

def decode(stego_image: ndarray, block_size: int = 8) -> str:
    """
    Decode data into image using F5 algorithm

    Parameters
    ----------
    stego_image: Stego image loaded with OpenCV
    block_size: Size of block

    Returns
    -------
    The hidden data in string format

    """
    # Initialization
    nb_channels: int = stego_image.shape[2]

    # Crop image to be able to decompose later.
    block_shape: ndarray = np.array((block_size, block_size, nb_channels))
    nb_blocks: ndarray = np.array(stego_image.shape) // block_shape
    crop_r, crop_c, crop_ch = nb_blocks * block_shape
    cropped_image: ndarray = stego_image[:crop_r, :crop_c, :crop_ch]

    # Split the image channels
    splat_cropped_image = cv2.split(cropped_image)

    # Decompose each channel into blocks
    channel_blocks = [
        np.array([x for y in blocks for x in y])
        for blocks in [
            einops.rearrange(channel_image, "(x dx) (y dy) -> x y dx dy", dx=block_size, dy=block_size)
            for channel_image in splat_cropped_image
        ]
    ]

    # Merge each channel block into 1D array of blocks
    blocks = [x for y in zip(*channel_blocks) for x in y]

    hidden_data: str = ""
    for block in blocks:
        dct = cv2.dct(np.float32(block))
        num = float(dct[-1][-1])
        if float(dct[-1][-1]) < 7.5:
            hidden_data += '0'
        else:
            hidden_data += '1'

    return hidden_data

stego = encode(
    cv2.imread("/home/meeddoh/PycharmProjects/steganography-tool/test_files/clean.png"), string_to_binary("Coucou")
)
cv2.imwrite("/home/meeddoh/PycharmProjects/steganography-tool/test_files/stego_f5.png", stego)

message = binary_to_string(decode(cv2.imread("/home/meeddoh/PycharmProjects/steganography-tool/test_files/stego_f5.png")))

print(message)
