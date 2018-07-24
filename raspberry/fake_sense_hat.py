from tkinter import *
from collections import namedtuple
import threading
from time import sleep
import keyboard

InputEvent = namedtuple('InputEvent', ('timestamp', 'direction', 'action'))
#event_list = []

class SenseHat:
    class stick:
        def get_events():
            try:
                if keyboard.is_pressed('up arrow'):
                    return [InputEvent(timestamp="0", direction="up", action="pressed")]
                elif keyboard.is_pressed('down arrow'):
                    return [InputEvent(timestamp="0", direction="down", action="pressed")]
                elif keyboard.is_pressed('right arrow'):
                    return [InputEvent(timestamp="0", direction="right", action="pressed")]
                elif keyboard.is_pressed('left arrow'):
                    return [InputEvent(timestamp="0", direction="left", action="pressed")]
                else:
                    return []
            except:
                return []

    # factor is the screen size factor
    factor = 20

    # leds holds the simulated LEDs in a two-dimensional list
    leds = []

    # The following hold the tkinter objects so that they are accessible through
    # the whole class
    canvas = None
    master = None


    def __init__(self):
        """This is a SenseHat substitude for our little IoT project. The reason it exists
        is to simulate the SenseHat LED hardware in order to run our project on a
        normal PC"""

        # Create window and canvas
        self.master = Tk()
        self.canvas = Canvas(self.master, width=self.factor*10, height=self.factor*10)
        self.canvas.pack()

        # Iterate through LEDs and create them
        for x in range(8):
            y_axis = []
            for y in range(8):
                y_axis.append(self.__create_box(self.canvas, y * self.factor, x * self.factor, self.factor))
            self.leds.append(y_axis)

    def __create_box(self, canvas, x, y, size):
        """Create a box on the canvas"""
        return canvas.create_rectangle(x, y, x + size, y + size, fill="#FFFFFF")

    def __color_array_to_value(self, color):
        """Convert colors from SenseHat API to Tkinter API"""
        return "#" + '{:02x}'.format(color[0]) + '{:02x}'.format(color[1]) + '{:02x}'.format(color[2])

    def set_pixels(self, pixel_list):
        """Simulate set_pixels API from SenseHat"""
        i = 0;
        for x in range(8):
            for y in range(8):
                self.canvas.itemconfig(self.leds[x][y], fill=self.__color_array_to_value(pixel_list[i]))
                i += 1
        self.master.update()

    def set_pixel(self, x, y, r, g, b):
        """Simulate set_pixel API from SenseHat"""
        self.canvas.itemconfig(self.leds[x][y], fill=self.__color_array_to_value([r, g, b]))
        self.master.update()
