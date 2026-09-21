import os
import random
import time
from PIL import Image, ImageDraw

# this is a pure Convay's Life (no random colors)

class LifeSimpleGenerator:
    def make_gif(self, text):

        frame_dir = "frames"
        num_frames = 20
        width = 25 # width in cells
        height = 25 # height in cells
        sz = 10
        png_files = []
        a = []
        b = []

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

        for k in range(num_frames):
            img = Image.new("RGB", (width * sz + 1, height * sz + 1), color="#000000")
            draw = ImageDraw.Draw(img)

            # draw grid
            for i in range(height + 1):
                draw.line([(0, i * sz), (width * sz + 1, i * sz)], fill="white", width=1)

            for j in range(width + 1):
                draw.line([(j * sz, 0), (j * sz, height * sz + 1)], fill="white", width=1)

            # draw filled cells
            for i in range(height):
                for j in range(width):
                    if a[i][j]:
                        draw.rectangle(
                            [(i * sz + 1, j * sz + 1), ((i + 1) * sz - 1, (j + 1) * sz - 1)],
                            fill="red",
                        )

            # create matrix B from A
            for i in range(height):
                for j in range(width):
                    left = j - 1
                    right = j + 1
                    up = i - 1
                    down = i + 1
                    if (down == height): down = 0
                    if (up < 0): up = height - 1
                    if (right == width): right = 0
                    if (left < 0): left = width - 1

                    near = 0
                    if (a[up][j]): near = near + 1
                    if (a[down][j]): near = near + 1
                    if (a[i][left]): near = near + 1
                    if (a[i][right]): near = near + 1
                    if (a[up][left]): near = near + 1
                    if (a[up][right]): near = near + 1
                    if (a[down][left]): near = near + 1
                    if (a[down][right]): near = near + 1

                    # b3s23 (classic life)
                    if (a[i][j]):
                        if (near == 2 or near == 3):
                            b[i][j] = 1
                        else:
                            b[i][j] = 0
                    else:
                        if (near == 3):
                            b[i][j] = 1
                        else:
                            b[i][j] = 0

            a = b

            png_file = os.path.join(frame_dir, "frame_" + str(k) + ".png")
            img.save(png_file)
            png_files.append(png_file)

        # make gif
        frames = [Image.open(f) for f in png_files]
        basename = str(int(time.time())) + "_" + text + ".gif"
        gif_filename = os.path.join(os.path.dirname(__file__), "static", basename)
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )

        return os.path.join("/static", basename)

if __name__ == "__main__":
    generator = LifeSimpleGenerator()
    generator.make_gif("Alex Artukh")
