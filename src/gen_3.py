import hashlib
import math
import random
import sys

from gen_base import GifGeneratorBase

class ThirdGenerator(GifGeneratorBase):

    def __init__(self, textdata=""):
        super().__init__(textdata)
        self.type = 500

    def get_description(self):
        return [
            "Третий генератор (заготовка)",
            "Переданный текст преобразуется в MD5 хеш (16 байт)",
            "Матрица делится на прямоугольники примерно sqrt(высота) x sqrt(ширина)",
            "MD5 выбирает половину прямоугольников, они закрашиваются за все кадры",
            "Порядок закраски ячеек тоже зависит от MD5",
        ]

    def make_gif(self, digest, uid):
        random.seed(42)
        a = []
        self.init_matrix_zeros(a)
        if self.random_colors:
            self.use_random_colors(digest)

        rng = random.Random(digest)

        # split the matrix into blocks about sqrt(height) x sqrt(width),
        # the last block in a row / column takes the remainder
        blocks_i = int(math.sqrt(self.height))
        blocks_j = int(math.sqrt(self.width))

        blocks = []
        for bi in range(blocks_i):
            for bj in range(blocks_j):
                blocks.append((bi, bj))

        # half of the blocks are chosen by digest
        rng.shuffle(blocks)
        num_chosen = len(blocks) // 2

        # list of cells of the chosen blocks
        cells = []
        for idx in range(num_chosen):
            bi, bj = blocks[idx]
            i_start = bi * self.height // blocks_i
            i_end = (bi + 1) * self.height // blocks_i
            j_start = bj * self.width // blocks_j
            j_end = (bj + 1) * self.width // blocks_j
            for i in range(i_start, i_end):
                for j in range(j_start, j_end):
                    cells.append((i, j))

        # order of painting depends on digest
        rng.shuffle(cells)

        total = len(cells)
        painted = 0

        for k in range(self.num_frames):

            # paint the next part of cells, after the last frame all chosen blocks are painted
            target = (k + 1) * total // self.num_frames
            while painted < target:
                i, j = cells[painted]
                a[i][j] = 1
                painted = painted + 1

            img = self.draw_frame(a)

            self.save_frame(img, k)

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

    generator = ThirdGenerator(settings)

    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)
