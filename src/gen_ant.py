import hashlib

from gen_base import GifGeneratorBase


class AntGenerator(GifGeneratorBase):

    # направления муравья: вверх, вправо, вниз, влево (dx, dy)
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


    # по 2 байта digest на муравья
    # 16 байт md5 хватает ровно на 8
    # минимальное количество = 1
    NUM_ANTS = 4

    def __init__(self, textdata=""):
        super().__init__(textdata)
        self.type = 300
        self.steps_per_frame = 10  # шагов муравья между сохранёнными кадрами
        self.num_frames *= 4 

    def get_description(self):
        return [
            "Муравей Лэнгтона (Langton's Ant)",
            "Нсколько агентов ходят по сетке (края склеены — тор)",
            "На белой клетке: поворот направо, красит клетку в чёрный, шаг вперёд",
            "На чёрной клетке: поворот налево, красит клетку в белый, шаг вперёд",
            "Стартовая клетка каждого муравья задаётся парой байтов digest",
        ]

    def make_gif(self, digest, uid):
        a = []
        self.init_matrix_zeros(a)

        # стартовые клетки берутся из digest: байты 0 и 1 — первый муравей,
        # 2 и 3 — второй, ..., 14 и 15 — восьмой; все смотрят "вверх"
        ants = []
        for i in range(self.NUM_ANTS):
            x = (digest[2 * i] * 1) % self.width
            y = (digest[2 * i + 1] * 1) % self.height
            direction = 0  # индекс в DIRECTIONS
            ant = [x, y, direction]
            ants.append(ant)

        for k in range(self.num_frames):

            for _ in range(self.steps_per_frame):
                # муравьи ходят по очереди, каждый делает один шаг
                for ant in ants:
                    x, y, direction = ant

                    if a[y][x] == 0:
                        # белая клетка: направо, красим в чёрный, шаг вперёд
                        direction = (direction + 1) % 4
                        a[y][x] = 1
                    else:
                        # чёрная клетка: налево, красим в белый, шаг вперёд
                        direction = (direction - 1) % 4
                        a[y][x] = 0

                    dx, dy = self.DIRECTIONS[direction]
                    ant[0] = (x + dx) % self.width
                    ant[1] = (y + dy) % self.height
                    ant[2] = direction

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