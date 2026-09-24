import hashlib
import random

from gen_base import GifGeneratorBase

class LifeMyGenerator(GifGeneratorBase):

    def __init__(self):
        super().__init__()
        self.type = 200

    def get_description(self):
        return [
            "Усовершенствованная Life Конвея",
            "Переданный текст преобразуется в MD5 хеш (16 байт)",
            "10 байт из MD5 влияют на то, как будут использованны находящиеся рядом соседи",
            "Матрица всегда инициализируется 50/50 одним и тем же зерном",
        ]

    def make_gif(self, digest, uid):
        frames2skip = 5    
        random.seed(42)
        a = []
        b = []
        self.init_matrix_50_50(a)
        self.init_matrix_zeros(b)

        max_near = 0
        bits = []
        for b_idx in range(6, 16): # byes with indexes 6-15
            for offset in range(1,9): # 1-8
                v = (digest[b_idx] >> offset) & 1
                bits.append(v)
                if v == 1: max_near = max_near + 1

        for k in range(self.num_frames + frames2skip):

            img = self.draw_frame(a)

            # create matrix B from A
            for i in range(self.height):
                for j in range(self.width):

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
                            if ii >= self.height: continue
                            if jj >= self.width: continue

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

            if (k >= frames2skip):
                self.save_frame(img, k)

        # make movie : append almost all (except first and last) reversed array to itself
        last_idx = len(self.png_files) - 1
        for idx in range(last_idx - 1, 1, -1):
            self.png_files.append(self.png_files[idx])
                                
        filename = self.create_gif_file(uid, digest)
        
        return filename

if __name__ == "__main__":
    generator = LifeMyGenerator()
    text = "TESTING"
    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)