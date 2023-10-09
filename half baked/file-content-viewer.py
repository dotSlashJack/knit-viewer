import argparse
from PIL import Image
import os

# display the contents of a .dat file in a more human-readable format (color codes and header with coordinates)
def parse_dat(file_path):
    with open(file_path, 'rb') as file:
        # Header information
        minX = int.from_bytes(file.read(2), byteorder='little')
        minY = int.from_bytes(file.read(2), byteorder='little')
        maxX = int.from_bytes(file.read(2), byteorder='little')
        maxY = int.from_bytes(file.read(2), byteorder='little')
        
        magicA = int.from_bytes(file.read(2), byteorder='little')
        file.seek(6, 1)  # Skip 6 bytes to adjust for JS offset difference (0x10 vs 0x1C, not sure exactly why it is at 0x100)
        magicB = int.from_bytes(file.read(2), byteorder='little')
    
        
        if magicA != 1000 or magicB != 1000:
            raise ValueError(f"Unknown magic numbers ({magicA}, {magicB}).")
        
        width = maxX - minX + 1
        height = maxY - minY + 1
        
        # Palette information
        file.seek(0x200)  # Seek to offset 0x200
        paletteR = bytearray(file.read(0x100))
        paletteG = bytearray(file.read(0x100))
        paletteB = bytearray(file.read(0x100))
        
        # Byte swap function
        def byte_swap(arr):
            ret = bytearray(len(arr))
            for i in range(0, len(arr), 2):
                ret[i] = arr[i + 1]
                ret[i + 1] = arr[i]
            return ret
        
        paletteR = byte_swap(paletteR)
        paletteG = byte_swap(paletteG)
        paletteB = byte_swap(paletteB)

        print("Palette:")
        print(paletteR)
        print()
        print(paletteG)
        print()
        print(paletteB)
        print("---")
        
        # go through the palette and convert the RGB values to hex
        palette = []
        for i in range(256):
            red = paletteR[i]
            green = paletteG[i]
            blue = paletteB[i]
            
            # convert the RGB values to a hexadecimal color string
            # (this is weird code but basically it formats the RGB values into a 2-character hex string), I could not write this from scratch
            hex_color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
            
            palette.append(hex_color)
        
        # Raster information
        raster_data = bytearray(file.read())
        raster = bytearray(width * height)
        
        x, y = 0, 0
        i = 0
        while i < len(raster_data):
            index = raster_data[i]
            repeat = raster_data[i + 1]
            for r in range(repeat):
                raster[y * width + x] = index
                x += 1
                if x >= width:
                    x = 0
                    y += 1
                    if y >= height:
                        break  # ran out of raster to fill
            if y >= height:
                break
            i += 2
        
    return {
        'width': width,
        'height': height,
        'palette': palette,
        'paletteR': paletteR,
        'paletteG': paletteG,
        'paletteB': paletteB,
        'data': raster
    }


# display the contents of a .dat file in their straight up bytes
def extract_raw_data(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(0x012)  # reading up to 0x012 to include all the header data (last magic number at 0x010)
        
        """
        0x000 to 0x011 is for header information.
        0x200 is for the red palette data.
        0x300 is for the green palette data.
        0x400 is for the blue palette data.
        """
        file.seek(0x200)
        
        # Extract raw RGB values
        paletteR = file.read(0x100)
        paletteG = file.read(0x100)
        paletteB = file.read(0x100)
    
    return {
        'header': header,
        'paletteR': paletteR,
        'paletteG': paletteG,
        'paletteB': paletteB
    }


def draw_image(parsed_data):
    width = parsed_data['width']
    height = parsed_data['height']
    paletteR = parsed_data['paletteR']
    paletteG = parsed_data['paletteG']
    paletteB = parsed_data['paletteB']
    raster_data = parsed_data['data']
    
    # create blank image and get a list of its pixels
    img = Image.new('RGB', (width, height))
    pixels = list(raster_data)
    rgb_data = []

    # then convert the pixels to RGB values
    for index in pixels:
        r = paletteR[index]
        g = paletteG[index]
        b = paletteB[index]
        #inverted_color = invert_color((r, g, b))
        #rgb_data.append(inverted_color)
        rgb_data.append((r, g, b))
        

    img.putdata(rgb_data)
    img.show()


def extract_raw_colors(file_path):
    with open(file_path, 'rb') as file:
        #header = int.from_bytes()      
        header_byte = file.read(16)
        header = ''.join(f'{byte:02x}' for byte in header_byte)
        
        file.seek(0x200)
        
        paletteR = file.read(0x100)
        paletteG = file.read(0x100)
        paletteB = file.read(0x100)
    
    # convert raw RGB values to color tuples
    colors = [(paletteR[i], paletteG[i], paletteB[i]) for i in range(256)]
    
    return {
        'header': header,
        'colors': colors
    }

def invert_color(color): # handles weirdness that I coulndt fiture out
    r, g, b = color
    return (255 - r, 255 - g, 255 - b)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="path to the file to be parsed")
    parser.add_argument("-f", "--format", help="format with which to display the data")
    args = parser.parse_args()
    file_path = args.input
    format = args.format

    if(format == "raw" or format == "bytes"):
        data = extract_raw_data(file_path)
        print(data)
    elif(format == "draw" or format == "image" or format == "canvas"):
        data = parse_dat(file_path)
        draw_image(data)
    elif(format == "color"):
        data = extract_raw_colors(file_path)
        print("Header:", data['header'])
        for color in data['colors']:
            print(color)
    else:
        data = parse_dat(file_path)
        print(data)
 