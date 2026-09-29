import hashlib
import sys

from gen_base import GifGeneratorBase

class FGenerator(GifGeneratorBase):

    def __init__(self, t, textdata=""):

        try:
            generator_type = int(t)
        except (TypeError, ValueError):
            raise ValueError("FGenerator type must be an integer: " + str(t))

        if generator_type < 1 or generator_type > 5:
            raise ValueError("unknown FGenerator type: " + str(generator_type))

        super().__init__(textdata)
        self.type = generator_type

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

    def make_gif(self, digest, uid):
        a = []
        self.init_matrix_zeros(a)

        # окно будет перемещаться от этой левой верхней точки
        ii = digest[6]
        jj = digest[7]

        for k in range(self.num_frames):

            # calculate values 
            for i in range(self.height):
                for j in range(self.width):
                    a[i][j] = self.f(ii + i, jj + j)
            
            img = self.draw_frame(a)
            self.save_frame(img, k)

            jj += 1 # up-down
            ii += 1 # left-right

        # make movie : append almost all (except first and last) reversed array to itself
        last_idx = len(self.png_files) - 1
        for idx in range(last_idx - 1, 1, -1):
            self.png_files.append(self.png_files[idx])

        filename = self.create_gif_file(uid, digest)
        
        return filename

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        text = sys.argv[1]
    else:
        text = "TESTING"

    if len(sys.argv) >= 3:
        type = sys.argv[2]
    else:
        type = "1"

    settings = """
        hex_color=#FF0000
        hex_color_bg=#FFFFFF
        hex_color_line=#FF00FF
    """

    generator = FGenerator(type, settings)
    
    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)
