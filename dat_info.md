To start with, the canvas minimum x and y value (which should correspond to the lower left corner of the image) will be equal to the bytes at 0x000 and 0x002 respectively. The max x and y pixel value (upper right corner of the image) will be in 0x004 and 0x006 respectively. There will also be 'magic numbers' at 0x008 and 0x010 respectively, but those don't need to be drawn. 

Then comes the body of the dat file. Starting at index 0x200, there are bytes corresponding to the red values for all colors used in the image, at 0x300 are the blue values for all colors (same order) and at 0x400 are the green colors. Basically that means that at 0x200 would be the red, 0x300 would be the green, and 0x400 would be the blue of the ‘first’ rgb color, and so on until the end of the colors used. Keep in mind that python will need to bitflip these because the values from .dat are in little endian and it’s expecting big endian.

Then we have the position data about where to draw each color, which is based on RLE encoding starting at 0x600. These are again sections of 2 bytes (not like colors which are 1 byte). This format follows the pattern where the first byte represents the index of a color in the initial set (for example it would mean index i  of all of the r, g, and b colors such as the values at 0x200, 0x300, and 0x400. The second byte is a repeat count which basically says how many consecutive pixels should be colored with the color pointed to by the index. The index starts at x=0, y=0 (x is width, y height). Then, if x exceeds the width of the image, it wraps around such that the excess value of x (x % width) becomes the new x, and the y index (height) is incremented by 1 so it moves to the next row up. If y exceeds the height of the image, the process stops, as the entire image has been filled.

As an example of this RLE, if the first two bytes in the raster data are 3 and 5, this means that the color at index 3 in the palette should be used for the next 5 pixels in the image.