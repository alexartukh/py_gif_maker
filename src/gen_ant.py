import hashlib

from gen_base import GifGeneratorBase


class AntGenerator(GifGeneratorBase):

    # направления муравья: вверх, вправо, вниз, влево (dx, dy)
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def __init__(self, textdata=""):
        super().__init__(textdata)
        self.type = 300
        self.steps_per_frame = 100  # шагов муравья между сохранёнными кадрами
        self.num_frames *= 4 

    def get_description(self):
        return [
            "Муравей Лэнгтона (Langton's Ant)",
            "Один агент ходит по сетке 50x50 (края склеены — тор)",
            "На белой клетке: поворот направо, красит клетку в чёрный, шаг вперёд",
            "На чёрной клетке: поворот налево, красит клетку в белый, шаг вперёд",
            "Переданный текст (digest) пока не влияет на результат",
        ]

    def make_gif(self, digest, uid):
        a = []
        self.init_matrix_zeros(a)

        # старт в центре поля, лицом "вверх"
        x = self.width // 2
        y = self.height // 2
        direction = 0  # индекс в DIRECTIONS

        for k in range(self.num_frames):

            for _ in range(self.steps_per_frame):
                if a[y][x] == 0:
                    # белая клетка: направо, красим в чёрный, шаг вперёд
                    direction = (direction + 1) % 4
                    a[y][x] = 1
                else:
                    # чёрная клетка: налево, красим в белый, шаг вперёд
                    direction = (direction - 1) % 4
                    a[y][x] = 0

                dx, dy = self.DIRECTIONS[direction]
                x = (x + dx) % self.width
                y = (y + dy) % self.height

            img = self.draw_frame(a)
            self.save_frame(img, k)

        filename = self.create_gif_file(uid, digest)

        return filename


if __name__ == "__main__":
    settings = """
        hex_color=#FF0000
        hex_color_bg=#FFFFFF
        hex_color_line=#FF00FF
    """
    generator = AntGenerator(settings)
    text = "TESTING"
    generator.make_gif(hashlib.md5(text.encode('utf-8')).digest(), 0)