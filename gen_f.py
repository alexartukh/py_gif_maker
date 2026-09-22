import hashlib
import os
import time
from PIL import Image, ImageDraw

class FGenerator:

    def __init__(self, t):
        self.type = t

    def f(self, y, x):
        if self.type == 1:
            return ((((x ^ y) & ((x - 350) >> 3)) ** 2) >> 12) & 1
        if self.type == 2:
            return (((x ^ y) & (x + y)) >> ((x + y) % 10)) & 1
        if self.type == 3:
            return (((x ^ y) & (x + y)) >> (y % 10)) & 1
        if self.type == 4:
            return bin(x & y).count("1") % 2
        if self.type == 5:
            a = ((((x ^ y) & ((x - 350) >> 3)) ** 2) >> 12) & 1
            b = ((((x + y) & (x - y)) ** 3) >> 9) & 1
            return a ^ b

        return 0

    def get_description(self):
        return [
            "Сложная булевая функция от двух переменных",
            "2 байта из MD5 влияют на начальную позицию окна",
        ]

    def make_gif(self, text, uid):

        frame_dir = "frames"
        num_frames = 20 
        width = 50 # width in cells 
        height = 50 # height in cells
        sz = 10
        png_files = []
        a = []
        bits = []

        for i in range(height):
            line = []
            for j in range(width):
                line.append(0)
            a.append(line)

        # get MD5 digest in a non-hex form, just an array of bytes
        digest = hashlib.md5(text.encode('utf-8')).digest()

        hex_color = "#FF0000"
        hex_color_bg = "#000000"
        hex_color_line = "#FFFFFF"

        # окно будет перемещаться от этой левой верхней точки
        ii = digest[6]
        jj = digest[7]

        for bytes in range(6, 16): # byes with indexes 6-15
            for offset in range(1,9): # 1-8
                v = (digest[6] >> offset) & 1
                bits.append(v)

        for k in range(num_frames):
            img = Image.new("RGB", (width * sz + 1, height * sz + 1), color=hex_color_bg)
            draw = ImageDraw.Draw(img)

            # draw grid
            for i in range(height + 1):
                draw.line([(0, i * sz), (width * sz + 1, i * sz)], fill=hex_color_line, width=1)

            for j in range(width + 1):
                draw.line([(j * sz, 0), (j * sz, height * sz + 1)], fill=hex_color_line, width=1)

            # calculate values 
            for i in range(height):
                for j in range(width):
                    # просто передаем оставшиеся байты внутрь функции
                    # возможно, что не все эти параметры будут использованны
                    a[i][j] = self.f(ii + i, jj + j)

            # draw filled cells
            for i in range(height):
                for j in range(width):
                    if a[i][j]:
                        draw.rectangle(
                            [(i * sz + 1, j * sz + 1), ((i + 1) * sz - 1, (j + 1) * sz - 1)],
                            fill=hex_color,
                        )
            
            png_file = os.path.join(frame_dir, "frame_" + str(k) + ".png")
            img.save(png_file)
            png_files.append(png_file)

            # up-down
            jj += 1
            # left-right
            ii += 1

        # append almost all (except first and last) reversed array to itself
        last_idx = len(png_files) - 1
        for idx in range(last_idx - 1, 1, -1):
            png_files.append(png_files[idx])

        os.makedirs("static/" + str(uid), exist_ok=True)
                                
        frames = [Image.open(f) for f in png_files]
        basename = str(int(time.time())) + "_" + text + ".gif"
        gif_filename = os.path.dirname(__file__) + "/static/" + str(uid) + "/" + basename
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )

        return "/static/" + str(uid) + "/" + basename

if __name__ == "__main__":
    generator = FGenerator()
    generator.make_gif("TESTING", 0)
