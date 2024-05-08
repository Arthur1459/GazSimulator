# Usefully functions for the game
import pygame as pg
import vars as vr
from random import randint

# Global vars :
pg.font.init()
fonts = {}
for size in vr.default_sizes:
    fonts[size] = pg.font.Font(vr.font, vr.default_sizes[size])  # set the fonts

def getInputs():
    keys = pg.key.get_pressed()
    vr.inputs["SPACE"] = True if keys[pg.K_SPACE] else False
    vr.inputs["ESCAPE"] = True if keys[pg.K_ESCAPE] else False
    vr.inputs["R"] = True if keys[pg.K_r] else False
    vr.inputs["G"] = True if keys[pg.K_g] else False
    vr.inputs["B"] = True if keys[pg.K_b] else False
    vr.inputs["Y"] = True if keys[pg.K_y] else False
    vr.inputs["P"] = True if keys[pg.K_p] else False
    vr.inputs["L"] = True if keys[pg.K_l] else False
    vr.inputs["M"] = True if keys[pg.K_m] else False
    vr.inputs["S"] = True if keys[pg.K_s] else False
    vr.inputs["D"] = True if keys[pg.K_d] else False
    vr.inputs["I"] = True if keys[pg.K_i] else False
    vr.inputs["RIGHT_CLICK"] = True if pg.mouse.get_pressed(num_buttons=3)[0] else False
    vr.inputs["LEFT_CLICK"] = True if pg.mouse.get_pressed(num_buttons=3)[2] else False
    return

def key(key):
    try:
        if vr.inputs[key]:
            return True
        else:
            return False
    except:
        print(f"ERROR : {key} not in inputs")
    return False

def Text(msg, coord, color, screen, size=3):  # blit to the screen a text
    global fonts
    TextColor = pg.Color(color)  # set the color of the text
    return screen.blit(fonts[size].render(msg, True, TextColor), coord)  # return and blit the text on the screen

def getNewId():
    vr.id += 1
    return vr.id

def getRndCoord():
    return [randint(10, vr.screen_size - 10), randint(10, vr.screen_size - 10)]

def getRndSpeed(bounds=(10, 10)):
    return [randint(-1 * bounds[0], bounds[0]), randint(-1 * bounds[1], bounds[1])]

def newList(content=None):
    return [] if content is None else [content]

def IsPointInBox(point, box_anchor, box_width, box_height):
    if box_anchor[0] <= point[0] <= box_anchor[0] + box_width:
        if box_anchor[1] <= point[1] <= box_anchor[1] + box_height:
            return True
    return False