# Least Significant Bit

## What is Least Significant Bit Steganography technic?

LSB Steganography is an image steganography technique in which messages are hidden inside an image by replacing each
pixel’s least significant bit with the bits of the message to be hidden.

To understand better, let’s consider a digital image to be a 2D array of pixels.
Each pixel contains values depending on its type and depth.
We will consider the most widely used modes — RGB(3x8-bit pixels, true-color)
and RGBA(4x8-bit pixels, true-color with transparency mask).
These values range from 0–255, (8-bit values).

| ![lsb explanation](./media/lsb-explanation.png) | 
|:--:| 
| **Figure 1:** *Showing the Least Significant Bit in a pixel* |

We can convert the message into decimal values and then into binary, by using the ASCII Table.
Then, we iterate over the pixel values one by one, after converting them to binary,
we replace each least significant bit with that message bits in a sequence.

To decode an encoded image, we simply reverse the process.
Collect and store the last bits of each pixel then split them into groups of 8
and convert it back to ASCII characters to get the hidden message.

### Inline LSB _[1]_:

Our tool offers `Simple Inline LSB Steganography`.
The data to be hidden is transformed to binary then it is padded with zeros to become as big as the maximal data size
that the data can retain. We then loop on each pixel's channel to hide one bit of the data.

Decoding is the same, after the data is extracted the padding of zeros is removed.

### Equi-Distribution LSB:

The tool offers as well `Equi-Distribution LSB Steganography`.
Instead of hiding the data inline _- pixel after pixel, channel after channel -_ we distribute the data.
After figuring the space taken for the header _- always stored at the start of the image and contains the size of the data-_
we calculate the space needed for equi-distribution between each bit.
From there the position of each bit is calculated and placed in the matrix.

Same calculations are used for decoding.


### Midpoint Circle LSB _[2]_:

The tool offers as well `Midpoint Circle LSB Steganography`.
In this method, the data is hidden on a circle created using Midpoint Circle Drawing Algorithm.
The center of the image is used as the center of the circle,
the minimum distance from that center to a side of the image is the radius.

Same for decoding

## References
1. C.-K. Chan and L.M. Cheng, "Hiding data in images by simple LSB substitution," _Pattern Recognition, 37(3)_, 2004, pp. 469–474, doi: 10.1016/j.patcog.2003.08.007
2. V. Verma, Poonam and R. Chawla, "An enhanced Least Significant Bit steganography method using midpoint circle approach," _2014 International Conference on Communication and Signal Processing_, 2014, pp. 105-108, doi: 10.1109/ICCSP.2014.6949808
