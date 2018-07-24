import random

class PixelArt:
    WHITE = [0, 0, 0]
    RED = [255, 0, 0]
    BLANK = WHITE * 8 * 8

    NUMBERS = [
        [0, 0, 0,
         1, 1, 1,
         1, 0, 1,
         1, 0, 1,
         1, 0, 1,
         1, 0, 1,
         1, 1, 1,
         0, 0, 0],

        [0, 0, 0,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 1, 1,
         0, 0, 1,
         1, 1, 1,
         1, 0, 0,
         1, 0, 0,
         1, 1, 1,
         0, 0, 0],
        
        [0, 0, 0,
         1, 1, 1,
         0, 0, 1,
         0, 1, 1,
         0, 0, 1,
         0, 0, 1,
         1, 1, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 0, 0,
         1, 0, 1,
         1, 1, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 1, 1,
         1, 0, 0,
         1, 1, 1,
         0, 0, 1,
         0, 0, 1,
         1, 1, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 1, 1,
         1, 0, 0,
         1, 1, 1,
         1, 0, 1,
         1, 0, 1,
         1, 1, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 1, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 1, 1,
         1, 0, 1,
         1, 1, 1,
         1, 0, 1,
         1, 0, 1,
         1, 1, 1,
         0, 0, 0],

        [0, 0, 0,
         1, 1, 1,
         1, 0, 1,
         1, 1, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 1,
         0, 0, 0]

    ]

    UP_ARROW = [0, 0, 0, 1, 1, 0, 0, 0,
                0, 0, 1, 1, 1, 1, 0, 0,
                0, 1, 1, 1, 1, 1, 1, 0,
                1, 1, 0, 1, 1, 0, 1, 1,
                0, 0, 0, 1, 1, 0, 0, 0,
                0, 0, 0, 1, 1, 0, 0, 0,
                0, 0, 0, 1, 1, 0, 0, 0,
                0, 0, 0, 1, 1, 0, 0, 0]

    def __init__(self):
        pass

    def fade(self, matrix, fade):
        faded_matrix = []

        if fade < 0 or fade > 1:
            return self.BLANK;
        
        for led in matrix:
            new_led_matrix = []
            for color in led:
                new_led_matrix.append(int(color * fade))
            faded_matrix.append(new_led_matrix)
        
        return faded_matrix

    def loading(self):
        loading_matrix = []
        for i in range(8 * 8):
            loading_matrix.append([random.randrange(255), random.randrange(255), random.randrange(255)])
        return loading_matrix

    def make_up_arror(self, color = RED):
        return self.__matrix_to_color_matrix(self.UP_ARROW, color)

    def make_score(self, score1, score2, color = RED):
        if score1 > 9 or score2 > 9:
            return self.BLANK;
        return self.__make_number_from_digits(score1, score2, True, color)

    def make_number(self, number, color = RED):
        if number > 99:
            return self.BLANK;

        decades = int(number / 10)
        singles = int(number % 10)

        return self.__make_number_from_digits(decades, singles, False, color)

    def __make_number_from_digits(self, decades, singles, score, color = RED):
        number_matrix = []
        
        i = 0
        first_digit = self.__matrix_to_color_matrix(self.NUMBERS[decades], color)
        second_digit = self.__matrix_to_color_matrix(self.NUMBERS[singles], color)
        i_first_matrix = 0
        i_second_matrix = 0

        for x in range(8):
            for y in range(8):
                if y in range(3):
                    number_matrix.append(first_digit[i_first_matrix])
                    i_first_matrix += 1
                elif y in range(5, 8):
                    number_matrix.append(second_digit[i_second_matrix])
                    i_second_matrix += 1
                else:
                    if score and y in range(3, 5) and x == 4:
                        number_matrix.append([60, 60, 60])
                    else:
                        number_matrix.append(self.WHITE)
                i += 1

        return number_matrix

    def __matrix_to_color_matrix(self, matrix, color):
        r = []
        for pixel in matrix:
            if pixel:
                r.append(color)
            else:
                r.append(self.WHITE)
        return r
