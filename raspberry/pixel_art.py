import random
import math
from pixel_art_bitmaps import PixelArtBitmaps

class PixelArt:
    """Creates pixel art (arrows, letters, numbers, effects) for the game"""
    bitmaps = PixelArtBitmaps() # Create bitmap object

    def __init__(self):
        # Nothing to do
        pass

    def fade(self, matrix, fade):
        """Fades a screen matrix. Fade value from 0 to 1"""
        faded_matrix = []

        if fade < 0 or fade > 1:
            return self.bitmaps.BLANK;
        
        # Go through each LED of the matrix and multiply it with the fade value
        for led in matrix:
            new_led_matrix = []
            for color in led:
                new_led_matrix.append(int(color * fade))
            faded_matrix.append(new_led_matrix)
        
        return faded_matrix

    def loading(self):
        """Create a loading screen (random colours in random places"""
        loading_matrix = []
        for i in range(8 * 8):
            loading_matrix.append([random.randrange(255), random.randrange(255), random.randrange(255)])
        return loading_matrix

    def scan(self, line, color = bitmaps.RED):
        """Creates a terminator-style scan bar"""
        matrix = [0] * 8 * 8
        matrix[line * 8: line * 8 + 8] = [1] * 8
        return self.__matrix_to_color_matrix(matrix, color)

    def waiting(self, degrees, color1 = bitmaps.RED, color2 = bitmaps.GREEN):
        """Creates two dots animated in a circle"""
        # Use cos and sin to determine the coordinates in the circle
        # Fixed circle diameter
        x_1 = 3 + int(3 * math.cos(math.radians(degrees)))
        y_1 = 3 + int(3 * math.sin(math.radians(degrees)))

        x_2 = 3 + int(3 * -math.cos(math.radians(degrees)))
        y_2 = 3 + int(3 * -math.sin(math.radians(degrees)))

        matrix = []

        for i in range(8 * 8):
            matrix.append([0, 0, 0])
        
        matrix[x_1 * 8 + y_1] = color1
        matrix[x_2 * 8 + y_2] = color2
        return matrix


    def make_up_arrow(self, color = bitmaps.RED):
        """Creates an arrow pointing up"""
        return self.__matrix_to_color_matrix(self.bitmaps.UP_ARROW, color)

    def make_score(self, score1, score2, color = bitmaps.RED):
        """Creates a score display"""
        if score1 > 9 or score2 > 9:
            return self.BLANK;
        return self.__make_number_from_digits(score1, score2, True, color)

    def make_number(self, number, color = bitmaps.RED):
        """Creates a number display"""
        if number > 99:
            return self.BLANK;

        # Seperate the two digits
        decades = int(number / 10)
        singles = int(number % 10)

        return self.__make_number_from_digits(decades, singles, False, color)

    def make_letter(self, letter, color = bitmaps.RED):
        """Creates a letter display"""
        return self.__matrix_to_color_matrix(self.bitmaps.LETTERS[letter], color)

    def __make_number_from_digits(self, decades, singles, score, color = bitmaps.RED):
        """Creates a number matrix from two digits"""
        number_matrix = []
        
        i = 0
        first_digit = self.__matrix_to_color_matrix(self.bitmaps.NUMBERS[decades], color)
        second_digit = self.__matrix_to_color_matrix(self.bitmaps.NUMBERS[singles], color)
        i_first_matrix = 0
        i_second_matrix = 0

        # Iterate through all points of the matrix, set the appropriate rbgs
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
                        # Faded white line for score divider
                        number_matrix.append([60, 60, 60])
                    else:
                        number_matrix.append(self.bitmaps.WHITE)
                i += 1

        return number_matrix

    def __matrix_to_color_matrix(self, matrix, color):
        """Converts a binary to a color matrix"""
        r = []
        for pixel in matrix:
            if pixel:
                r.append(color)
            else:
                r.append(self.bitmaps.WHITE)
        return r
