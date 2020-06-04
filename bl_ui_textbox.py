from . bl_ui_widget import *

import blf
import bpy


class BL_UI_Textbox(BL_UI_Widget):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._text_color = (1.0, 1.0, 1.0, 1.0)

        self._bg_color = (0.2, 0.2, 0.2, 1.0)

        self._carret_color = (0.0, 0.2, 1.0, 1.0)

        self._offset_letters = 0

        self._carret_pos = 0

        self.text = ""
        self._text_size = 12
        self._textpos = [x, y]
        self._max_input_chars = 100

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value

    @property
    def max_input_chars(self):
        return self._max_input_chars

    @max_input_chars.setter
    def max_input_chars(self, value):
        self._max_input_chars = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._carret_pos = len(value)

        self.update_carret()

    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._text_size = value

    def update(self, x, y):
        super().update(x, y)
        self._textpos = [x, y]
        self.update_carret()

    def set_carret_pos(self, mouse_x):
        self._carret_pos = 2
        self.update_carret()

    def get_carret_pos_px(self):

        size_all = blf.dimensions(0, self._text)
        size_to_carret = blf.dimensions(0, self._text[:self._carret_pos])
        return self.x_screen + (self.width / 2.0) - (size_all[0] / 2.0) + size_to_carret[0]

    def update_carret(self):

        if self.context:
            y_screen_flip = self.get_area_height() - self.y_screen

            x = self.get_carret_pos_px()

            # bottom left, top left, top right, bottom right
            vertices = (
                (x, y_screen_flip - 6),
                (x, y_screen_flip - self.height + 6)
            )

            self.batch_carret = batch_for_shader(
                self.shader, 'LINES', {"pos": vertices})

    def draw(self):

        super().draw()

        area_height = self.get_area_height()

        # Draw text
        self.draw_text(area_height)

        self.shader.bind()
        self.shader.uniform_float("color", self._carret_color)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glLineWidth(1)
        self.batch_carret.draw(self.shader)

    def set_colors(self):
        color = self._bg_color
        text_color = self._text_color

        self.shader.uniform_float("color", color)

    def draw_text(self, area_height):
        blf.size(0, self._text_size, 72)
        size = blf.dimensions(0, self._text)

        textpos_y = area_height - \
            self._textpos[1] - (self.height + size[1]) / 2.0
        blf.position(
            0, self._textpos[0] + (self.width - size[0]) / 2.0, textpos_y + 1, 0)

        r, g, b, a = self._text_color
        blf.color(0, r, g, b, a)

        blf.draw(0, self._text)

    def get_input_keys(self):
        return ['ESC', 'RET', 'BACK_SPACE', 'HOME', 'END', 'LEFT_ARROW', 'RIGHT_ARROW', 'DEL']

    def text_input(self, event):

        index = self._carret_pos

        if event.ascii != '' and len(self._text) < self.max_input_chars:
            self._text = self._text[:index] + event.ascii + self._text[index:]
            self._carret_pos += 1
        elif event.type == 'BACK_SPACE':
            if self._carret_pos > 0:
                self._text = self._text[:index-1] + self._text[index:]
                self._carret_pos -= 1

        elif event.type == 'DEL':
            if self._carret_pos < len(self._text):
                self._text = self._text[:index] + self._text[index+1:]

        elif event.type == 'LEFT_ARROW':
            if self._carret_pos > 0:
                self._carret_pos -= 1

        elif event.type == 'RIGHT_ARROW':
            if self._carret_pos < len(self._text):
                self._carret_pos += 1

        elif event.type == 'HOME':
            self._carret_pos = 0

        elif event.type == 'END':
            self._carret_pos = len(self._text)

        self.update_carret()
        try:
            self.text_changed_func(self, self.context, event)
        except:
            pass

        return True

    def set_text_changed(self, text_changed_func):
        self.text_changed_func = text_changed_func

    def mouse_down(self, x, y):
        if self.is_in_rect(x, y):
            return True

        return False

    def mouse_move(self, x, y):
        pass

    def mouse_up(self, x, y):
        pass
