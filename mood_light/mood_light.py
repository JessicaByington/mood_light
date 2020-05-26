import magichue
import csv
import attributes
from functools import partial
import time


class LightSource:
    """
    Contains data and functions relevant to a single light source.
    The consumer will be able to power on and off the light source,
    set different modes (with different patterns and speeds), colors,
    brightness, and white values (warm or cold).
    """
    def __init__(self, name, ip_addr, room):
        """
        Initialize and create a light source, off by default
        :param name: string to identify the light source
        :param ip_addr: string ip address the light source is at
        :param room: string to identify the room the light source
        is in
        """
        self.name = name
        self.ip_addr = ip_addr
        self.room = room

        self.light_source = magichue.Light(ip_addr)

    def power_on(self):
        """
        Turns the light source on
        :return: n/a
        """
        self.light_source.on = True

    def power_off(self):
        """
        Turns the light source off
        :return: n/a
        """
        self.light_source.on = False

    def current_color(self):
        """
        Returns the current RGB value of the light source
        :return: integer tuple for red, green, and blue ranging from
        0-255
        """
        return self.light_source.rgb

    def enable_color(self):
        """
        Turns off the white LEDs and turns on the color LEDs
        :return: n/a
        """
        self.light_source.is_white = False

    def disable_color(self):
        """
        Turns off the color LEDs and turns on the white LEDs
        :return: n/a
        """
        self.light_source.is_white = True

    def set_white(self, warm_white, cold_white):
        """
        Sets the white LEDs color to be warm or cold
        :param warm_white: integer value ranging from 0-255
        :param cold_white: integer value ranging from 0-255
        :return: n/a
        """
        # turn off color mode so white LED's work
        self.disable_color()

        # change the value of warm to cold whites
        self.light_source.w = warm_white
        self.light_source.cw = cold_white

    def set_rgb_color(self, red, green, blue):
        """
        Sets the different levels of red, green, or blue LEDs
        :param red: integer value ranging from 0-255
        :param green: integer value ranging from 0-255
        :param blue: integer value ranging from 0-255
        :return: n/a
        """
        # turn on color mode
        self.enable_color()

        # change the values of red, blue, and green LEDs
        self.light_source.r = red
        # sleep allows commands to get to the bulb and allow time
        # for processing or colors will not change
        time.sleep(0.2)

        self.light_source.g = green
        time.sleep(0.2)

        self.light_source.b = blue
        time.sleep(0.2)

    def set_hsb_color(self, hue, saturation, brightness):
        """
        Sets the different levels of hue, saturation, or brightness
        LED's
        :param hue: float value ranging from 0-1
        :param saturation: float value ranging from 0-1
        :param brightness: integer value ranging from 0-255
        :return: n/a
        """
        # turn on color mode
        self.enable_color()

        # change the values of hue, saturation, and brightness
        self.light_source.hue = hue
        # sleep allows commands to get to the bulb and allow time
        # for processing or colors will not change
        time.sleep(0.2)

        self.light_source.saturation = saturation
        time.sleep(0.2)

        self.light_source.brightness = brightness
        time.sleep(0.2)

    def toggle_fade(self):
        """
        Toggle the fade effect when changing colors on or off
        :return: n/a
        """
        if self.light_source.allow_fading is False:
            self.light_source.allow_fading = True
        else:
            self.light_source.allow_fading = False

    def current_mode(self):
        """
        Returns the string name of the current built in flash pattern mode
        :return: string name of mode
        """
        return self.light_source.mode.name

    def set_mode(self, mode):
        """
        Sets flash pattern mode to built in pattern from magichue lib
        :param mode: magichue object the defines the type of mode
        :return: n/a
        """
        self.light_source.mode = mode

    def set_speed(self, speed):
        """
        Sets the speed at which the mode flashes to
        :param speed: float value ranging from 0-1
        :return: n/a
        """
        self.light_source.speed = speed


def name_checker(num_of_new_lights, current_lights):
    # check to see if generic name is currently in the list
    generic_name = 'New Light ' + str(num_of_new_lights)

    if current_lights:
        if not any([True for item in current_lights if generic_name == item.name]):
            num_of_new_lights += 1
            generic_name = 'New Light ' + str(num_of_new_lights)

            # recurse through the function until at a generic name
            # that does not currently exist
            name_checker(num_of_new_lights, current_lights)

    return generic_name


def discover_bulbs(current_lights):
    # keep track of all the new lights being added
    num_of_new_lights = 0

    # get a list all of bulb addresses found on LAN
    all_lights = magichue.discover_bulbs()

    # scan through list of current lights to find which ones are new
    for new_light in all_lights:
        num_of_new_lights += 1

        # create generic name based on number of new lights
        # being added as long as it does not currently exist
        generic_name = name_checker(num_of_new_lights, current_lights)

        # only add if ip address is not already present
        if not any([True for item in current_lights if item.ip_addr == new_light]):
            # create a new light source and added it to current list
            add_light = LightSource(generic_name, new_light, 'Unknown')
            current_lights.append(add_light)


def color_selector(light_source):
    # set the light source to on
    light_source.power_on()

    # print out the list of colors available to choose from
    for key in attributes.rgb_colors:
        print(key)

    # accept user input and change the color of the light source
    color = input("Select a color: ")

    if color in attributes.rgb_colors:
        colors = attributes.rgb_colors.get(color)
        light_source.set_rgb_color(colors[0], colors[1], colors[2])


def save_lights_to_file(current_lights):
    # save list of current light sources to the csv file
    # for later loading
    with open('docs/light_list.csv', 'w', newline='') as csv_file:
        file_writer = csv.writer(csv_file, delimiter=',')

        for item in current_lights:
            file_writer.writerow([item.name, item.ip_addr, item.room])


def load_lights_from_file():
    # load list of current light sources from csv file
    # and create a list of LightSource class objects from that
    current_lights = []

    with open('docs/light_list.csv', newline='') as csv_file:
        file_reader = csv.reader(csv_file, delimiter=',')

        for row in file_reader:
            # break up the row into name, ip address, and room
            light_source = LightSource(row[0], row[1], row[2])
            current_lights.append(light_source)

    return current_lights


def options(current_lights, selection=0, light_source=0):

    switcher = {
        # add new bulbs from ip address scan
        1: partial(discover_bulbs, current_lights),
        2: partial(color_selector, light_source)
    }

    # get the selection from those available
    func = switcher.get(selection, lambda: "Invalid Selection")

    # execute the option selected
    func()


def main():
    current_lights = []
    # Get all lights currently stored
    current_lights = load_lights_from_file()

    # get current light sources
    options(current_lights, 1)

    for item in current_lights:
        light_source = item

        # load options for user input
        options(current_lights, 2, light_source)

    save_lights_to_file(current_lights)


if __name__ == "__main__":
    main()
