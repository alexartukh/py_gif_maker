import hashlib
import os
import random
from PIL import Image, ImageDraw 

# f(x,y) pseudo random function

class FGenerator:

    def f(self, y, x):
        return ((((x ^ y) & ((x - 350) >> 3)) ** 2) >> 12) & 1

    def make_gif(self, text):

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

        # colors from hash
        red = digest[0]
        green = digest[1]
        blue = digest[2]

        red2 = 255 - digest[0]
        green2 = 255 - digest[1]
        blue2 = 255 - digest[2]

        red3 = digest[3]
        green3 = digest[4]
        blue3 = digest[5]

        hex_color = f"#{red:02X}{green:02X}{blue:02X}"
        hex_color_inv = f"#{red2:02X}{green2:02X}{blue2:02X}"
        hex_color_line = f"#{red3:02X}{green3:02X}{blue3:02X}"

        for bytes in range(6, 16): # byes with indexes 6-15
            for offset in range(1,9): # 1-8
                v = (digest[6] >> offset) & 1
                bits.append(v)

        ii = 200
        jj = 250

        for k in range(num_frames):
            img = Image.new("RGB", (width * sz + 1, height * sz + 1), color=hex_color)
            draw = ImageDraw.Draw(img)

            # draw grid
            for i in range(height + 1):
                draw.line([(0, i * sz), (width * sz + 1, i * sz)], fill=hex_color_line, width=1)

            for j in range(width + 1):
                draw.line([(j * sz, 0), (j * sz, height * sz + 1)], fill=hex_color_line, width=1)

            # calculate values 
            for i in range(height):
                for j in range(width):
                    a[i][j] = self.f(ii + i, jj + j)

            # draw filled cells
            for i in range(height):
                for j in range(width):
                    if a[i][j]:
                        draw.rectangle(
                            [(i * sz + 1, j * sz + 1), ((i + 1) * sz - 1, (j + 1) * sz - 1)],
                            fill=hex_color_inv,
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
                                
        frames = [Image.open(f) for f in png_files]
        gif_filename = os.path.join(os.path.dirname(__file__), "static", "_" + text + ".gif")
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )

        return os.path.join("/static", "_" + text + ".gif")

if __name__ == "__main__":
    generator = FGenerator()
    generator.make_gif("Alex Artukh")