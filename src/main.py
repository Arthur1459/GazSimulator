import pygame as pg
import time
import vars as vr
import tools as t
import utils as u
from particle import ParticleBlue, ParticleGreen, ParticleRed, ParticleYellow, Atmosphere
from random import randint
from solid import Solid

def gameUpdate():
    vr.cursor = pg.mouse.get_pos()
    if u.key("R"):
        vr.atmosphere.composition["RED"] += 1
        coord = t.Vsum(pg.mouse.get_pos(), (randint(-20, 20), randint(-20, 20)))
        vr.atmosphere.particles.append(ParticleRed(coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
    if u.key("G"):
        vr.atmosphere.composition["GREEN"] += 1
        coord = t.Vsum(pg.mouse.get_pos(), (randint(-20, 20), randint(-20, 20)))
        vr.atmosphere.particles.append(ParticleGreen(coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
    if u.key("B"):
        vr.atmosphere.composition["BLUE"] += 1
        coord = t.Vsum(pg.mouse.get_pos(), (randint(-20, 20), randint(-20, 20)))
        vr.atmosphere.particles.append(ParticleBlue(coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
    if u.key("Y"):
        vr.atmosphere.composition["YELLOW"] += 1
        coord = t.Vsum(pg.mouse.get_pos(), (randint(-20, 20), randint(-20, 20)))
        vr.atmosphere.particles.append(ParticleYellow(coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))

    if u.key("L"):
        vr.persistence = vr.persistence + 2 if vr.persistence + 2 <= 100 else vr.persistence
    elif u.key("M"):
        vr.persistence = vr.persistence - 2 if vr.persistence - 2 >= 0 else vr.persistence

    if u.key("P") and vr.wait_key < 0:
        vr.display_pressure = True if vr.display_pressure is False else False
        vr.wait_key = 0.3

    if u.key("I") and vr.wait_key < 0:
        vr.atmosphere = Atmosphere()
        vr.wait_key = 0.3

    if u.key("S") and vr.wait_key < 0:
        vr.solids.append(Solid(vr.cursor, 50, 50))
        vr.wait_key = 0.3

    vr.atmosphere.update()

    for solid_id in range(len(vr.solids)-1, -1, -1):
        vr.solids[solid_id].update()

    return

def displayUpdate():
    if vr.screen is None:
        print("Screen not initialized")
        return

    for solid in vr.solids:
        solid.draw()

    vr.atmosphere.draw()

    persistence = pg.Surface(vr.screen_size_2)
    persistence = persistence.convert_alpha()
    persistence.fill((vr.back_color[0], vr.back_color[1], vr.back_color[2], vr.persistence))
    vr.screen.blit(persistence, (0, 0))

    nb_particles = max(vr.atmosphere.composition["BLUE"] + vr.atmosphere.composition["GREEN"] + vr.atmosphere.composition["RED"] + vr.atmosphere.composition["YELLOW"], 1)
    blue_percent, green_percent, red_percent, yellow_percent = vr.atmosphere.composition["BLUE"]/nb_particles, vr.atmosphere.composition["GREEN"]/nb_particles, vr.atmosphere.composition["RED"]/nb_particles, vr.atmosphere.composition["YELLOW"]/nb_particles

    pg.draw.rect(vr.screen, vr.back_color, (0, vr.screen_size - 75, 280, 100))
    pg.draw.rect(vr.screen, (40, 40, 160), (200, vr.screen_size - 5 - 65 * blue_percent, 18, 65 * blue_percent))
    pg.draw.rect(vr.screen, (160, 40, 40), (220, vr.screen_size - 5 - 65 * red_percent, 18, 65 * red_percent))
    pg.draw.rect(vr.screen, (40, 160, 40), (240, vr.screen_size - 5 - 65 * green_percent, 18, 65 * green_percent))
    pg.draw.rect(vr.screen, (200, 200, 40), (260, vr.screen_size - 5 - 65 * yellow_percent, 18, 65 * yellow_percent))

    u.Text(f"FPS : {round(vr.real_fps, 2)} frame/s", t.Vmult_sum(vr.bot_left, 1, [10, -15], vr.screen_factor), "grey", vr.screen)
    u.Text(f"Particles : {nb_particles}", t.Vmult_sum(vr.bot_left, 1, [10, -30], vr.screen_factor), "grey", vr.screen, size=3)
    u.Text(f"Pressure : {vr.atmosphere.pressure}", t.Vmult_sum(vr.bot_left, 1, [10, -45], vr.screen_factor), "grey", vr.screen, size=3)


    pg.display.update()
    return

def main():
    vr.atmosphere = Atmosphere(vr.nb_blue_particles, vr.nb_green_particles, vr.nb_red_particles, vr.nb_yellow_particles)

    vr.running = True
    u.getInputs()

    while vr.running:
        while time.time() - vr.t < vr.dt_blocking:
            pass

        vr.dt = time.time() - vr.t
        vr.wait_key -= vr.dt
        vr.t = time.time()

        vr.real_fps = vr.frames / (time.time() - vr.t_frames)
        if vr.frames < 10000:
            vr.frames += 1
        else:
            vr.frames = 1
            vr.t_frames = time.time()

        for event in pg.event.get():
            if event.type == pg.QUIT or u.key("ESCAPE"):
                vr.running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                vr.inputs["CLICK"] = True
            elif event.type == pg.MOUSEBUTTONUP:
                vr.inputs["CLICK"] = False
                if vr.debug is True:
                    print(pg.mouse.get_pos())

        # Main Loop Here :
        u.getInputs()
        gameUpdate()
        displayUpdate()

    print("EXIT Game.")
    return

def init_main():
    vr.t_start = time.time()

    pg.init()
    # Icon / Name
    if vr.icon is not None:
        pg.display.set_icon(vr.icon)
    pg.display.set_caption(vr.game_name)

    # screen initialisation
    if not vr.fullscreen:
        vr.screen = pg.display.set_mode(vr.screen_size_2)
    else:
        vr.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        vr.screen_width, vr.screen_height = vr.screen.get_width(), vr.screen.get_height()

    # time / clock creation
    vr.clock, vr.t_frames, vr.t = pg.time.Clock(), time.time(), time.time()
    vr.id = 0

    for i in range(vr.grouping):
        vr.particles_groups.append([])
        for n in range(vr.grouping):
            vr.particles_groups[i].append([])

    print("Initialization done !", time.process_time(), "s")
    return

if __name__ == "__main__":
    init_main()
    main()
