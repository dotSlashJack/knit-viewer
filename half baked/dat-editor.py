import pygame
import tkinter as tk
from tkinter import colorchooser
import sys

pygame.init()

# Colors
BLACK = (0, 0, 0)


def get_mac_color_picker_color():
    import subprocess
    script = """
    set chosenColor to choose color
    return chosenColor
    """

    result = subprocess.check_output(["osascript", "-e", script]).decode('utf-8').strip()
    colors = list(map(int, result.split(", ")))

    rgb_colors = [round(color / 65535 * 255) for color in colors[:3]]

    return tuple(rgb_colors)

class PixelCanvas:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.scale = scale  # Scaling factor
        self.window = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption("Paint Canvas Emulator")
        self.canvas_data = [[BLACK for _ in range(height)] for _ in range(width)]
        self.current_color = (255, 255, 255)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    x //= self.scale  # Adjust mouse coordinates based on scale
                    y //= self.scale
                    self.canvas_data[y][x] = self.current_color
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.change_color()
                    elif event.key == pygame.K_s:
                        self.save_canvas_to_file(self.canvas_data, 'output.dat')
                        print("saved to dat")
                    elif event.key == pygame.K_p:
                        self.save_to_png()
                        print("saved to png")

            self.draw_canvas()
            pygame.display.flip()

    def draw_canvas(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(self.window, self.canvas_data[y][x], (x * self.scale, y * self.scale, self.scale, self.scale))


    def change_color(self):
        # if on macos use subprocess to call the color picker
        if sys.platform == 'darwin':
            self.current_color = get_mac_color_picker_color()
        else:
            root = tk.Tk()
            root.withdraw()
            color = colorchooser.askcolor(title="Choose color")
            if color[1]:
                self.current_color = tuple(int(color[1][i:i+2], 16) for i in (1, 3, 5))

    def save_to_png(self):
        # Create a blank surface to render the canvas
        canvas_surface = pygame.Surface((self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(canvas_surface, self.canvas_data[x][y], (x, y, 1, 1))

        # Save the canvas as a PNG image
        pygame.image.save(canvas_surface, 'output.png')

    def canvas_to_file_format(self, canvas_data):
        unique_colors = [BLACK] + list(set([color for row in canvas_data for color in row if color != BLACK]))
        if len(unique_colors) > 256:
            raise ValueError("More than 256 unique colors in canvas.")

        #paletteR = bytearray(256)
        #paletteG = bytearray(256)
        #paletteB = bytearray(256)
        # Initialize palette with a distinguishable color (e.g., bright magenta, jk)
        paletteR = bytearray([255] * 256)
        paletteG = bytearray([0] * 256)
        paletteB = bytearray([255] * 256)


        for idx, color in enumerate(unique_colors):
            paletteR[idx] = color[0]
            paletteG[idx] = color[1]
            paletteB[idx] = color[2]

        # convert image data to palette indices
        raster_data = bytearray()
        prev_idx = None
        repeat_count = 0

        for y in range(self.height):
            for x in range(self.width):
                pixel = canvas_data[y][x]
                idx = unique_colors.index(pixel)
                if prev_idx is None:
                    prev_idx = idx
                if idx == prev_idx:
                    repeat_count += 1
                    if repeat_count == 256:
                        raster_data.append(prev_idx)
                        raster_data.append(255)
                        repeat_count = 1
                else:
                    raster_data.append(prev_idx)
                    raster_data.append(repeat_count)
                    repeat_count = 1
                    prev_idx = idx
        if repeat_count > 0:
            raster_data.append(prev_idx)
            raster_data.append(repeat_count)

        return paletteR, paletteG, paletteB, raster_data

    def save_canvas_to_file(self, canvas_data, file_path):
        paletteR, paletteG, paletteB, raster_data = self.canvas_to_file_format(canvas_data)
        with open(file_path, 'wb') as f:
            # writing the header information
            f.write((0).to_bytes(2, byteorder='little'))  # minX
            f.write((0).to_bytes(2, byteorder='little'))  # minY
            f.write((len(canvas_data[0]) - 1).to_bytes(2, byteorder='little'))  # maxX
            f.write((len(canvas_data) - 1).to_bytes(2, byteorder='little'))  # maxY
            f.write((1000).to_bytes(2, byteorder='little'))  # magicA
            f.write(bytes(6))  # 6 bytes padding
            f.write((1000).to_bytes(2, byteorder='little'))  # magicB
            
            # writing RBG palette data
            f.seek(0x200)
            f.write(paletteR)
            f.write(paletteG)
            f.write(paletteB)

            f.write(raster_data)


if __name__ == "__main__":
    canvas = PixelCanvas(25, 25, 20)  # width, height, scale
    canvas.run()