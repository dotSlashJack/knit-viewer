"""Generate a grid (list of lists) of color indices from a .dat image or png"""

from PIL import Image
import colors

def generate_dat_from_color_indices(color_indices: list, output_file_path: str) -> None:
    """
    Generates and save a .dat file from a list of color indices where each index represents the index of that color in the r/g/b lists.

    :param color_indices: A list of lists color indices in the format where each list corresponds to a row with the first being the bottom row of the dat canvas.
    :param output_file_path: The path to the output file, ending in .dat.
    """

    #0,0 is bottom left corner pixel of raster thus why decremented to start at 0 index
    dat_width = len(color_indices[0]) - 1
    print(f'dat_width: {dat_width}')
    dat_height = len(color_indices) - 1
    print(f'dat_height: {dat_height}')


    with open(output_file_path, 'wb') as output_file:
        # write header with width at 0x004, height at 0x006, and 1000 (magic #) at 0x008 and 0x010
        output_file.seek(0x004)
        output_file.write(dat_width.to_bytes(2, byteorder='little'))
        output_file.seek(0x006)
        output_file.write(dat_height.to_bytes(2, byteorder='little'))
        output_file.seek(0x008)
        output_file.write((1000).to_bytes(2, byteorder='little'))
        output_file.seek(0x010)
        output_file.write((1000).to_bytes(2, byteorder='little'))

        # write color chunk
        output_file.seek(0x200)
        output_file.write(colors.red_color_bytes)
        
        output_file.seek(0x300)
        output_file.write(colors.green_color_bytes)

        output_file.seek(0x400)
        output_file.write(colors.blue_color_bytes)

        # write RLE encoded data (color index from rgb part of color chunk, then number of repeats)
        output_file.seek(0x600)
        repeats = 0

        for y in range(dat_height, -1, -1):
            row = color_indices[y]
            for x in range(dat_width + 1):
                repeats += 1
                if x == dat_width or row[x] != row[x+1]: # if end of row or next color is different, write out
                    output_file.write(row[x].to_bytes())
                    output_file.write(repeats.to_bytes())
                    repeats = 0
    
    output_file.close()


def find_matching_color_index(pixel_rgb: list) -> int:
    """
    Find the index of the given RGB value in the color list (color list from color.py is list of colors used in the .dat file).

    :param pixel_rgb: A list containing a red, green, and blue value
    :return: The index of the RGB value in the color list, or -1 if not found.
    """
    try:
        index = colors.color_list.index(pixel_rgb)
        #print(f"Color: {pixel_rgb} -> Index: {index}")  # Debugging line
        return index
    except ValueError:
        return -1


def find_matching_pixels(image_path: str) -> list:
    """
    Gets the indices in the color list of each pixel (e.g., ith element of red, green, and blue chunks of color info in .dat file).

    :param image_path: Path to the image.
    :param rgb_values_set: A set of RGB values to search for.
    :return: A list of pixel coordinates (x, y) that match the RGB values.
    """
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    print(f'width: {width}, height: {height}')
    matching_pixel_grid = []

    # generate grid of color indices that match grid of image pixels
    # each row is a list of pixel colors going across
    for y in range(height):
        row_color_indices = []
        for x in range(width):
            pixel_rgb = img.getpixel((x, y))[:3]
            color_index = find_matching_color_index(pixel_rgb)
            row_color_indices.append(color_index)

            if color_index < 0:
                raise ValueError(f"Color {pixel_rgb} not found in the valid color list.")
        matching_pixel_grid.append(row_color_indices)

    return matching_pixel_grid

def generate_image_from_pixel_list(pixel_list: list, output_file_path: str) -> None:
    """
    Generates and save a .png file from a list of pixels where each pixel is a list of RGB values, starting from the bottom row and moving up.

    :param pixel_list: A list of lists of indices where the RGB values live in the color list, where each sublist corresponds to a row with the first being the bottom row of the image.
    :param output_file_path: The path to the output file ending in .png.
    """
    
    width = len(pixel_list[0])
    height = len(pixel_list)

    img = Image.new('RGB', (width, height))
    for y in range(height):
        for x in range(width): # x is the index of the pixel in the row, not the color index
            color_index = pixel_list[y][x]
            img.putpixel((x, y), colors.color_list[color_index])

    img.save(output_file_path)


if __name__ == "__main__":
    image_path = "stst_10.dat.png"
    matching_pixels = find_matching_pixels(image_path)
    generate_image_from_pixel_list(matching_pixels, "test03.png")
    generate_dat_from_color_indices(matching_pixels, "test02.dat")
