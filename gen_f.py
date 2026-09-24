import hashlib

from gen_base import GifGeneratorBase

class FGenerator(GifGeneratorBase):

    def __init__(self, t):
        super().__init__()
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
    generator = FGenerator(1)
    text = "TESTING"
    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)
