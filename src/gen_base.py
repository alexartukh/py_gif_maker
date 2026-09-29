import random
import os
import time
import uuid
import shutil
from PIL import Image, ImageDraw

# project root : one level above the "src" folder
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# shared code and fields for all generators
class GifGeneratorBase:

    def __init__(self, settings):
        self.hex_color = "#FF0000"
        self.hex_color_bg = "#000000"
        self.hex_color_line = "#FFFFFF"

        self.num_frames = 20
        self.width = 50
        self.height = 50
        self.sz = 10
        self.png_files = []

        # unique folder for frames of this generator instance,
        # so parallel requests do not overwrite frames of each other
        self.frame_dir = os.path.join(PROJECT_DIR, "frames", str(uuid.uuid4()))

        # try to override default settings by data from 'settings'
        for line in settings.split("\n"):
            line = line.strip()
            if line == "":
                continue

            # skip lines without "key=value" format
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # skip lines with an empty key or an empty value
            if key == "" or value == "":
                continue

            if key == "hex_color":
                self.hex_color = value
                print("hex_color was replaced by " + value)
            if key == "hex_color_bg":
                self.hex_color_bg = value
                print("hex_color_bg was replaced by " + value)
            if key == "hex_color_line":
                self.hex_color_line = value
                print("hex_color_line was replaced by " + value)
            if key == "sz":
                try:
                    sz = int(value)
                except ValueError:
                    print("sz is not an integer: " + value)
                    continue

                # a cell smaller than 2 pixels can not be drawn inside the grid
                if sz < 2:
                    print("sz is too small: " + value)
                    continue

                self.sz = sz
                print("sz was replaced by " + value)

    @staticmethod
    def get_hint_for_settings():
        a = [
            "It is possible to override such settings as:",
            "- hex_color",
            "- hex_color_bg",
            "- hex_color_line",
            "- sz",
            "Everything else will be ignored",
        ]
        return "<br>".join(a)

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
        os.makedirs(self.frame_dir, exist_ok=True)
        png_file = os.path.join(self.frame_dir, "frame_" + str(frame_number) + ".png")
        img.save(png_file)
        self.png_files.append(png_file)

    def create_gif_file(self, uid, digest):
        os.makedirs(PROJECT_DIR + "/static/" + str(uid), exist_ok=True)
        frames = [ Image.open(f) for f in self.png_files ]
        basename = str(int(time.time())) + "_" + str(self.type) + "_" + digest.hex() + ".gif"
        gif_filename = PROJECT_DIR + "/static/" + str(uid) + "/" + basename
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )

        # close frame files first : on Windows an open file can not be deleted
        for frame in frames:
            frame.close()

        # frames are not needed after the GIF is built
        shutil.rmtree(self.frame_dir, ignore_errors=True)

        return "/static/" + str(uid) + "/" + basename
        