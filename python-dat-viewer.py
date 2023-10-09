"""
Read in .dat files for shima knitting machines to image format, but more than that hopefully understand how the heck they are structured
some useful .dat file structure info is in the dat_info.md file
by Jack Hester
"""
from PIL import Image

def byte_swap(arr): # TODO: put this in a shared file because grid generator uses
    ret = bytearray(len(arr))
    for i in range(0, len(arr), 2):
        ret[i] = arr[i+1]
        ret[i+1] = arr[i]
    return ret

def read_short(file, offset):
    file.seek(offset)
    return int.from_bytes(file.read(2), 'little')

def read_byte(file, offset):
    file.seek(offset)
    return int.from_bytes(file.read(1), 'little')

def decode_dat_to_image(file_path):
    with open(file_path, 'rb') as file:
        # canvas dimensions come from header
        min_x = read_short(file, 0x000)
        min_y = read_short(file, 0x002)
        max_x = read_short(file, 0x004)
        max_y = read_short(file, 0x006)

        magic_A = read_short(file, 0x008)
        magic_B = read_short(file, 0x010)
        print(f'magic_A: {magic_A}, magic_B: {magic_B}')
        if(magic_A != 1000 or magic_B!=1000):
            print("something is wrong with the magic nubmers, check your file")
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
 
        
        # get colors
        #colors = []
        #max_colors = 256 # naively assume that there are 256 colors, but there may be less

        file.seek(0x200) # seek to beginning of colors
        # byteswap is used to convert from little endian to big endian for each r g b value
        red_values = byte_swap(file.read(0x100))
        green_values = byte_swap(file.read(0x100))
        blue_values = byte_swap(file.read(0x100))

        #red_values = file.read(0x100)
        #green_values = file.read(0x100)
        #blue_values =file.read(0x100)

        #colors.reverse()
        #print(colors)
        
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        # fill in the image based on the data starting at 0x600
        x, y = 0, 0  # start from the bottom-left corner
        offset = 0x600  # starting offset for raster data (RLE)
        while y < height:
            color_index = read_byte(file, offset)
            repeat_count = read_byte(file, offset + 1)
            
            for _ in range(repeat_count):
                pixels[x, height - 1 - y] = (red_values[color_index], green_values[color_index], blue_values[color_index])# adjust y index to start from the bottom so it's a little less weird to think about
                x += 1
                if x >= width:
                    x = 0
                    y += 1
                    if y >= height:
                        break
            
            offset += 2 # number of bytes read per color = 2
        
        img.save(file_path + '.png')
        img.show()

# main
if __name__ == '__main__':
    decode_dat_to_image('test02.dat')
