import random
import os
import time
from PIL import Image, ImageDraw

# shared code and fields for all generators
class GifGeneratorBase:

    def __init__(self):
        self.hex_color = "#FF0000"
        self.hex_color_bg = "#000000"
        self.hex_color_line = "#FFFFFF"

        self.num_frames = 20
        self.width = 50
        self.height = 50
        self.sz = 10
        self.png_files = []

    def setup(self):
        pass

    def init_matrix_50_50(self, a):
        for i in range(self.height):
            line_a = []
            for j in range(self.width):
                if random.random() > 0.5:
                    v = 1
                else:
                    v = 0
                line_a.append(v)
            a.append(line_a)

    def init_matrix_zeros(self, a):
        for i in range(self.height):
            line_a = []
            for j in range(self.width):
                line_a.append(0)
            a.append(line_a)

    def draw_frame(self, a):
        img = Image.new("RGB", (self.width * self.sz + 1, self.height * self.sz + 1), color=self.hex_color_bg)
        draw = ImageDraw.Draw(img)

        # draw grid
        for i in range(self.height + 1):
            draw.line([(0, i * self.sz), (self.width * self.sz + 1, i * self.sz)], fill=self.hex_color_line, width=1)

        for j in range(self.width + 1):
            draw.line([(j * self.sz, 0), (j * self.sz, self.height * self.sz + 1)], fill=self.hex_color_line, width=1)

        # draw filled cells
        for i in range(self.height):
            for j in range(self.width):
                if a[i][j]:
                    draw.rectangle(
                        [(i * self.sz + 1, j * self.sz + 1), ((i + 1) * self.sz - 1, (j + 1) * self.sz - 1)],
                        fill=self.hex_color,
                    )
        return img

    def save_frame(self, img, frame_number):
        png_file = os.path.dirname(__file__) + "/frames/frame_" + str(frame_number) + ".png"
        os.makedirs(os.path.dirname(__file__) + "/frames", exist_ok=True)
        img.save(png_file)
        self.png_files.append(png_file)

    def create_gif_file(self, uid, digest):
        os.makedirs(os.path.dirname(__file__) + "/static/" + str(uid), exist_ok=True)
        frames = [Image.open(f) for f in self.png_files]
        basename = str(int(time.time())) + "_" + str(self.type) + "_" + digest.hex() + ".gif"
        gif_filename = os.path.dirname(__file__) + "/static/" + str(uid) + "/" + basename
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        return "/static/" + str(uid) + "/" + basename
        