import hashlib
import os
import random
from PIL import Image, ImageDraw 

# this is a random Life (not a cycle field)

class LifeGenerator:
    def make_gif(self, text):

        frame_dir = "frames"
        skip_frames = 5
        num_frames = 20 
        width = 50 # width in cells 
        height = 50 # height in cells
        sz = 10
        png_files = []
        a = []
        b = []
        bits = []

        # initial state for 'a' and 'b'
        for i in range(height):
            line_a = []
            line_b = []
            for j in range(width):
                if random.random() > 0.5:
                    v = 1
                else:
                    v = 0
                line_a.append(v)
                line_b.append(0)

            a.append(line_a)
            b.append(line_b)

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

        max_near = 0;
        for bytes in range(6, 16): # byes with indexes 6-15
            for offset in range(1,9): # 1-8
                v = (digest[6] >> offset) & 1
                bits.append(v)
                if v == 1: max_near = max_near + 1

        for k in range(num_frames + skip_frames):
            img = Image.new("RGB", (width * sz + 1, height * sz + 1), color=hex_color)
            draw = ImageDraw.Draw(img)

            # draw grid
            for i in range(height + 1):
                draw.line([(0, i * sz), (width * sz + 1, i * sz)], fill=hex_color_line, width=1)

            for j in range(width + 1):
                draw.line([(j * sz, 0), (j * sz, height * sz + 1)], fill=hex_color_line, width=1)

            # draw filled cells
            for i in range(height):
                for j in range(width):
                    if a[i][j]:
                        draw.rectangle(
                            [(i * sz + 1, j * sz + 1), ((i + 1) * sz - 1, (j + 1) * sz - 1)],
                            fill=hex_color_inv,
                        )

            # create matrix B from A
            for i in range(height):
                for j in range(width):

                    near = 0 # 80 is max
                    bit_counter = 0
                    for ii in range(i - 4, i + 5):
                        for jj in range(j - 4, j + 5):
                            bit_counter = bit_counter + 1

                            if ii == i and jj == j:
                                bit_counter = bit_counter - 1
                                continue
                            
                            if ii < 0: continue
                            if jj < 0: continue
                            if ii >= height: continue
                            if jj >= width: continue

                            # print(bit_counter)
                            if (a[ii][jj] and bits[bit_counter - 1]):
                                near = near + 1
                            
                    # b3s23 (classic life, but with fractions)
                    if (a[i][j]):
                        if (near >= (1 / 8 * max_near) and near <= (3 / 8 * max_near)):
                            b[i][j] = 1
                        else:
                            b[i][j] = 0
                    else:
                        if (near >= (2 / 8 * max_near) and near <= (3 / 8 * max_near)):
                            b[i][j] = 1
                        else:
                            b[i][j] = 0

            a = b

            if (k >= skip_frames):
                png_file = os.path.join(frame_dir, "frame_" + str(k) + ".png")
                img.save(png_file)
                png_files.append(png_file)

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
    generator = LifeGenerator()
    generator.make_gif("Alex Artukh")