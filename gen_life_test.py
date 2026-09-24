import hashlib

from gen_base import GifGeneratorBase

class LifeSimpleGenerator(GifGeneratorBase):

    def __init__(self):
        super().__init__()
        self.type = 100

    def get_description(self):
        return [
            "Оригинальная Life Конвея",
            "Использукется для тестирования",
            "Переданный текст не влияет ни на что",
            "Исходная матрица инициализируется случайным образом 50 на 50",
        ]
    
    def make_gif(self, digest, uid):
        a = []
        b = []
        self.init_matrix_50_50(a)
        self.init_matrix_zeros(b)

        for k in range(self.num_frames):

            img = self.draw_frame(a)

            # create matrix B from A
            for i in range(self.height):
                for j in range(self.width):
                    left = j - 1
                    right = j + 1
                    up = i - 1
                    down = i + 1
                    if (down == self.height): down = 0
                    if (up < 0): up = self.height - 1
                    if (right == self.width): right = 0
                    if (left < 0): left = self.width - 1

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

            self.save_frame(img, k)

        filename = self.create_gif_file(uid, digest)

        return filename

if __name__ == "__main__":
    generator = LifeSimpleGenerator()
    text = "TESTING"
    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)
