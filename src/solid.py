import vars as vr
import utils as u
import tools as t
import pygame as pg
from random import randint

class Solid:
    def __init__(self, anchor, width, height):
        self.top_left, self.width, self.height, = anchor, width, height
        self.cursor_anchor, self.size_anchor, self.base_size = None, None, [self.width, self.height]
        self.selected = False
        self.color = (randint(100, 200), randint(100, 200), randint(100, 200))
        return

    def update(self):
        if self.selected and u.key("D"):
            vr.solids.remove(self)
            return

        if u.key("LEFT_CLICK") and ((u.IsPointInBox(vr.cursor, self.top_left, self.width, self.height) and vr.solid_selected is False) or self.selected is True):
            vr.solid_selected = True
            self.selected = True
            if self.size_anchor is None:
                self.size_anchor = vr.cursor
            if self.size_anchor is not None:
                self.width = vr.cursor[0] - self.size_anchor[0] + self.base_size[0]
                self.height = vr.cursor[1] - self.size_anchor[1] + self.base_size[1]
        else:
            self.size_anchor = None
            self.base_size = [self.width, self.height]

        if u.key("RIGHT_CLICK") and u.IsPointInBox(vr.cursor, self.top_left, self.width, self.height) and (vr.solid_selected is False or self.selected is True):
            vr.solid_selected = True
            self.selected = True
            if self.cursor_anchor is None:
                self.cursor_anchor = t.Vsum(vr.cursor, t.Vmult(self.top_left, -1))
            if self.cursor_anchor is not None:
                self.top_left = t.Vsum(vr.cursor, t.Vmult(self.cursor_anchor, -1))
        else:
            self.cursor_anchor = None

        if not u.key("LEFT_CLICK") and not u.key("RIGHT_CLICK"):
            vr.solid_selected = False
            self.selected = False

        return

    def draw(self):
        pg.draw.rect(vr.screen, self.color, pg.Rect(self.top_left[0], self.top_left[1], self.width, self.height))
        return
