import hashlib
import sys

from gen_base import GifGeneratorBase

class FGenerator(GifGeneratorBase):

    def __init__(self, textdata=""):
        super().__init__(textdata)
        self.type = 100

    def f(self, y, x, d):
        # d - 16 байт: каждая четвёрка байт (a, b, c, e) задаёт одну битовую функцию,
        # результаты четырёх функций объединяются через XOR или OR
        result = 0
        for k in range(0, 16, 4):
            a, b, c, e = d[k], d[k + 1], d[k + 2], d[k + 3]

            u = (x ^ y, x & y, x | y, x + y)[a & 3]            # базовая комбинация
            s = (x - b) if a & 4 else (y + b)                  # смещённая координата
            v = (s >> (c & 7)) if a & 8 else (s << (c & 3))    # маска
            t = (u & v) * (1 + 2 * (a >> 4))                   # нечётный множитель 1..31
            if e & 1:
                t = t * t
            if e & 2:
                shift = (x + y) % (2 + (c >> 4))               # плавающий сдвиг
            else:
                shift = (c >> 4) + (8 if e & 1 else 0)
            bit = (t >> shift) & 1

            if e & 4:
                result |= bit
            else:
                result ^= bit

        return result

    def get_description(self):
        return [
            "Сложная булевая функция от двух переменных, все 16 байт MD5 задают её вид",
            "2 байта из MD5 влияют на начальную позицию окна",
        ]

    def make_gif(self, digest, uid):
        a = []
        self.init_matrix_zeros(a)
        if self.random_colors:
            self.use_random_colors(digest)

        # окно будет перемещаться от этой левой верхней точки
        ii = digest[6]
        jj = digest[7]

        for k in range(self.num_frames):

            # calculate values 
            for i in range(self.height):
                for j in range(self.width):
                    a[i][j] = self.f(ii + i, jj + j, digest)
            
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

    settings = """
        hex_color=#FF0000
        hex_color_bg=#FFFFFF
        hex_color_line=#FF00FF
    """

    generator = FGenerator(type, settings)
    
    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)
