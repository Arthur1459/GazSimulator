# Particle Class
import vars as vr
import tools as t
import pygame as pg
import utils as u
from math import sqrt
from random import randint

BLUE, GREEN, RED, YELLOW, WALL = "blue", "green", "red", "yellow", "wall"
ATTRACT, REPULSE = 1, -1

class Wall:
    def __init__(self, coord):
        self.type = WALL
        self.coord = coord
        self.radius = 1

class Atmosphere:
    def __init__(self, blue=0, green=0, red=0, yellow=0):
        self.composition = {"BLUE": blue, "GREEN": green, "RED": red, "YELLOW": yellow}
        self.particles = []
        self.pressure = 0
        self.init_particles()
        return

    def init_particles(self):
        for type in self.composition:
            for i in range(self.composition[type]):
                relative_coord = (randint(-20, 20), randint(-20, 20))
                relative_coord = t.Vsum(pg.mouse.get_pos(), relative_coord)
                self.composition[type] += 1
                if type == "BLUE":
                    self.particles.append(ParticleBlue(relative_coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
                if type == "GREEN":
                    self.particles.append(ParticleGreen(relative_coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
                if type == "RED":
                    self.particles.append(ParticleRed(relative_coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
                if type == "YELLOW":
                    self.particles.append(ParticleYellow(relative_coord, u.getRndSpeed(bounds=[vr.max_speed_red, vr.max_speed_red]), [0, 0]))
            return

    def update(self):
        pressure = 0
        for particle in self.particles:
            particle.update()
            pressure += particle.pressure
        self.pressure = round(pressure / max(len(self.particles), 1), 2)

        return

    def draw(self):
        for particle in self.particles:
            particle.draw()
        return

# --------------------------------------------------------------- #

class ParticleBlue:
    def __init__(self, coord, speed, accel, radius=3):
        self.id, self.type = u.getNewId(), BLUE
        self.coord, self.speed, self.accel = coord, speed, accel
        self.radius = radius
        self.group = self.getGroup()
        self.pressure = 0

        vr.particles_groups[self.group[0]][self.group[1]].append(self.id)
        vr.particles_dict[self.id] = self
        vr.particles_dict_type[self.type].append(self.id)
        return

    def update(self):
        self.accel, self.pressure = [0, 0], 0
        for particle_id in self.getNeighborsId():
            force = self.getInteractionWith(vr.particles_dict[particle_id])
            self.accel = t.Vsum(self.accel, force)
            self.pressure += t.norm(force)
        self.pressure = sqrt(self.pressure)

        # Wall
        self.speed[0] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[0]))))

        self.speed[0] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(vr.screen_size - self.coord[0]))))

        self.speed[1] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[1]))))

        self.speed[1] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction  / max(0.1, sqrt(abs(vr.screen_size - self.coord[1]))))

        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        for solid in vr.solids:
            if u.IsPointInBox(self.coord, solid.top_left, solid.width, solid.height):
                dist_right = abs(self.coord[0] - (solid.top_left[0] + solid.width))
                dist_left = abs(self.coord[0] - solid.top_left[0])
                dist_bottom = abs(self.coord[1] - (solid.top_left[1] + solid.height))
                dist_top = abs(self.coord[1] - solid.top_left[1])
                if t.isLowerThanALL(dist_left, [dist_top, dist_bottom]) and dist_left < dist_right:
                    self.speed[0] = -1 * dist_left * abs(self.speed[0])
                elif t.isLowerThanALL(dist_right, [dist_top, dist_bottom]):
                    self.speed[0] = 1.1 * dist_right * abs(self.speed[0])
                elif t.isLowerThanALL(dist_top, [dist_left, dist_right]) and dist_top < dist_bottom:
                    self.speed[1] = -1.1 * dist_top * abs(self.speed[1])
                else:
                    self.speed[1] = 1.1 * dist_bottom * abs(self.speed[1])

        if vr.screen_size < self.coord[0] or self.coord[0] < 0:
            self.speed[0] = self.speed[0] * -1
        if vr.screen_size < self.coord[1] or self.coord[1] < 0:
            self.speed[1] = self.speed[1] * -1
        t.controlVect(self.speed, [[-vr.max_speed_red, vr.max_speed_red], [-vr.max_speed_red, vr.max_speed_red]])
        self.coord = t.Vsum(self.coord, t.Vmult(self.speed, vr.dt))
        t.controlVect(self.coord, [[0, vr.screen_size], [0, vr.screen_size]])
        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        group_line, group_col = self.getGroup()
        if not t.VisEqual((group_line, group_col), self.group):
            vr.particles_groups[self.group[0]][self.group[1]].remove(self.id)
            self.group = (group_line, group_col)
            vr.particles_groups[self.group[0]][self.group[1]].append(self.id)

        return

    def draw(self):
        coord_to_draw = t.Vsum(self.coord, t.Vmult((self.radius, self.radius), -1/2))
        if vr.fancy:
            surface = pg.Surface(vr.screen_size_2, pg.SRCALPHA)
            alpha = self.pressure if self.pressure <= 255 else 255
            pg.draw.circle(surface, (40, 40, 160, alpha), coord_to_draw, self.radius, width=self.radius)
            vr.screen.blit(surface, (0, 0))
        elif vr.display_pressure:
            red = self.pressure * 2 if self.pressure * 2 <= 255 else 255
            color = (red, 255 - red, 255 - red)
            pg.draw.circle(vr.screen, color, coord_to_draw, self.radius, width=self.radius)
        else:
            pg.draw.circle(vr.screen, vr.blue_color, coord_to_draw, self.radius, width=self.radius)

        if vr.debug:
            u.Text(f"{t.roundVect(self.accel)}", self.coord, "red", vr.screen, size=3)

        return

    def getInteractionWith(self, particle):
        force = [0, 0]
        v_distance = t.Vsum(particle.coord, t.Vmult(self.coord, -1))
        distance = max(t.norm(v_distance), 0.00001)
        vect_U = [t.s(v_distance[0]), t.s(v_distance[1])]

        if particle.type == BLUE:
            force = t.Vmult(vect_U, REPULSE * vr.blue_interaction / max(distance/2, 1))
        elif particle.type == GREEN:
            force = t.Vmult(vect_U, ((distance - 50)/distance) * ATTRACT * vr.green_interaction / max(distance, 1))
        elif particle.type == RED:
            force = t.Vmult(vect_U, REPULSE * vr.red_interaction / max(distance, 1))
        elif particle.type == YELLOW:
            force = t.Vmult(vect_U, ATTRACT * vr.yellow_interaction / max(distance, 1))

        return force

    def getGroup(self):
        group_size = vr.screen_size / vr.grouping
        line, col = 0, 0
        while (line + 1) * group_size < self.coord[1]:
            line += 1
        while (col + 1) * group_size < self.coord[0]:
            col += 1
        return min(line, vr.grouping - 1), min(col, vr.grouping - 1)

    def getNeighborsId(self):
        neightbors = []
        groups_next = [self.group, [self.group[0] - 1, self.group[1]], [self.group[0] + 1, self.group[1]], [self.group[0], self.group[1] - 1], [self.group[0], self.group[1] + 1]]
        groups_next = groups_next + [[self.group[0] - 1, self.group[1] - 1], [self.group[0] - 1, self.group[1] + 1], [self.group[0] + 1, self.group[1] + 1], [self.group[0] + 1, self.group[1] - 1]]
        for group in groups_next:
            if t.VerifyVbounds(group, [[0, vr.grouping - 1], [0, vr.grouping - 1]]):
                neightbors = neightbors + self.getParticlesIdGroup(group)
        return neightbors

    def getParticlesIdGroup(self, group):
        ids = []
        for particle_id in vr.particles_groups[group[0]][group[1]]:
            if particle_id != self.id:
                ids.append(particle_id)
        return ids

# --------------------------------------------------------------- #

class ParticleGreen:
    def __init__(self, coord, speed, accel, radius=4):
        self.id, self.type = u.getNewId(), GREEN
        self.coord, self.speed, self.accel = coord, speed, accel
        self.radius = radius
        self.group = self.getGroup()
        self.pressure = 0

        vr.particles_groups[self.group[0]][self.group[1]].append(self.id)
        vr.particles_dict[self.id] = self
        return

    def update(self):
        self.accel, self.pressure = [0, 0], 0
        for particle_id in self.getNeighborsId():
            force = self.getInteractionWith(vr.particles_dict[particle_id])
            self.accel = t.Vsum(self.accel, force)
            self.pressure += t.norm(force)
        self.pressure = sqrt(self.pressure)

        # Wall
        self.speed[0] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[0]))))

        self.speed[0] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(vr.screen_size - self.coord[0]))))

        self.speed[1] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[1]))))

        self.speed[1] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction  / max(0.1, sqrt(abs(vr.screen_size - self.coord[1]))))

        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        for solid in vr.solids:
            if u.IsPointInBox(self.coord, solid.top_left, solid.width, solid.height):
                dist_right = abs(self.coord[0] - (solid.top_left[0] + solid.width))
                dist_left = abs(self.coord[0] - solid.top_left[0])
                dist_bottom = abs(self.coord[1] - (solid.top_left[1] + solid.height))
                dist_top = abs(self.coord[1] - solid.top_left[1])
                if t.isLowerThanALL(dist_left, [dist_top, dist_bottom]) and dist_left < dist_right:
                    self.speed[0] = -1 * dist_left * abs(self.speed[0])
                elif t.isLowerThanALL(dist_right, [dist_top, dist_bottom]):
                    self.speed[0] = 1.1 * dist_right * abs(self.speed[0])
                elif t.isLowerThanALL(dist_top, [dist_left, dist_right]) and dist_top < dist_bottom:
                    self.speed[1] = -1.1 * dist_top * abs(self.speed[1])
                else:
                    self.speed[1] = 1.1 * dist_bottom * abs(self.speed[1])

        if vr.screen_size < self.coord[0] or self.coord[0] < 0:
            self.speed[0] = self.speed[0] * -1
        if vr.screen_size < self.coord[1] or self.coord[1] < 0:
            self.speed[1] = self.speed[1] * -1
        t.controlVect(self.speed, [[-vr.max_speed_red, vr.max_speed_red], [-vr.max_speed_red, vr.max_speed_red]])
        self.coord = t.Vsum(self.coord, t.Vmult(self.speed, vr.dt))
        t.controlVect(self.coord, [[0, vr.screen_size], [0, vr.screen_size]])
        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        group_line, group_col = self.getGroup()
        if not t.VisEqual((group_line, group_col), self.group):
            vr.particles_groups[self.group[0]][self.group[1]].remove(self.id)
            self.group = (group_line, group_col)
            vr.particles_groups[self.group[0]][self.group[1]].append(self.id)

        return

    def draw(self):
        coord_to_draw = t.Vsum(self.coord, t.Vmult((self.radius, self.radius), -1 / 2))
        if vr.fancy:
            surface = pg.Surface(vr.screen_size_2, pg.SRCALPHA)
            alpha = self.pressure if self.pressure <= 255 else 255
            pg.draw.circle(surface, (40, 160, 80, alpha), coord_to_draw, self.radius, width=self.radius)
            vr.screen.blit(surface, (0, 0))
        elif vr.display_pressure:
            red = self.pressure * 2 if self.pressure * 2 <= 255 else 255
            color = (red, 255 - red, 255 - red)
            pg.draw.circle(vr.screen, color, coord_to_draw, self.radius, width=self.radius)
        else:
            pg.draw.circle(vr.screen, vr.green_color, coord_to_draw, self.radius, width=self.radius)
        if vr.debug:
            u.Text(f"{t.roundVect(self.accel)}", self.coord, "red", vr.screen, size=3)

        return

    def getInteractionWith(self, particle):
        force = [0, 0]
        v_distance = t.Vsum(particle.coord, t.Vmult(self.coord, -1))
        distance = max(t.norm(v_distance), 0.00001)
        vect_U = [t.s(v_distance[0]), t.s(v_distance[1])]

        if particle.type == BLUE:
            force = t.Vmult(vect_U, REPULSE * vr.blue_interaction / max(distance, 1))
        elif particle.type == GREEN:
            force = t.Vmult(vect_U, ((distance - 30) / distance) * ATTRACT * vr.green_interaction / max(distance, 1))
        elif particle.type == RED:
            force = t.Vmult(vect_U, ATTRACT * vr.red_interaction / max(distance, 1))
        elif particle.type == YELLOW:
            force = t.Vmult(vect_U, REPULSE * vr.yellow_interaction / max(distance, 1))

        return force

    def getGroup(self):
        group_size = vr.screen_size / vr.grouping
        line, col = 0, 0
        while (line + 1) * group_size < self.coord[1]:
            line += 1
        while (col + 1) * group_size < self.coord[0]:
            col += 1
        return min(line, vr.grouping - 1), min(col, vr.grouping - 1)

    def getNeighborsId(self):
        neightbors = []
        groups_next = [self.group, [self.group[0] - 1, self.group[1]], [self.group[0] + 1, self.group[1]], [self.group[0], self.group[1] - 1], [self.group[0], self.group[1] + 1]]
        for group in groups_next:
            if t.VerifyVbounds(group, [[0, vr.grouping - 1], [0, vr.grouping - 1]]):
                neightbors = neightbors + self.getParticlesIdGroup(group)
        return neightbors

    def getParticlesIdGroup(self, group):
        ids = []
        for particle_id in vr.particles_groups[group[0]][group[1]]:
            if particle_id != self.id:
                ids.append(particle_id)
        return ids

# --------------------------------------------------------------- #

class ParticleRed:
    def __init__(self, coord, speed, accel, radius=3):
        self.id, self.type = u.getNewId(), RED
        self.coord, self.speed, self.accel = coord, speed, accel
        self.radius = radius
        self.group = self.getGroup()
        self.pressure = 0

        vr.particles_groups[self.group[0]][self.group[1]].append(self.id)
        vr.particles_dict[self.id] = self
        return

    def update(self):
        self.accel, self.pressure = [0, 0], 0
        for particle_id in self.getNeighborsId():
            force = self.getInteractionWith(vr.particles_dict[particle_id])
            self.accel = t.Vsum(self.accel, force)
            self.pressure += t.norm(force)
        self.pressure = sqrt(self.pressure)

        # Wall
        self.speed[0] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[0]))))

        self.speed[0] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(vr.screen_size - self.coord[0]))))

        self.speed[1] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[1]))))

        self.speed[1] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction  / max(0.1, sqrt(abs(vr.screen_size - self.coord[1]))))

        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        for solid in vr.solids:
            if u.IsPointInBox(self.coord, solid.top_left, solid.width, solid.height):
                dist_right = abs(self.coord[0] - (solid.top_left[0] + solid.width))
                dist_left = abs(self.coord[0] - solid.top_left[0])
                dist_bottom = abs(self.coord[1] - (solid.top_left[1] + solid.height))
                dist_top = abs(self.coord[1] - solid.top_left[1])
                if t.isLowerThanALL(dist_left, [dist_top, dist_bottom]) and dist_left < dist_right:
                    self.speed[0] = -1 * dist_left * abs(self.speed[0])
                elif t.isLowerThanALL(dist_right, [dist_top, dist_bottom]):
                    self.speed[0] = 1.1 * dist_right * abs(self.speed[0])
                elif t.isLowerThanALL(dist_top, [dist_left, dist_right]) and dist_top < dist_bottom:
                    self.speed[1] = -1.1 * dist_top * abs(self.speed[1])
                else:
                    self.speed[1] = 1.1 * dist_bottom * abs(self.speed[1])

        if vr.screen_size < self.coord[0] or self.coord[0] < 0:
            self.speed[0] = self.speed[0] * -1
        if vr.screen_size < self.coord[1] or self.coord[1] < 0:
            self.speed[1] = self.speed[1] * -1
        t.controlVect(self.speed, [[-vr.max_speed_red, vr.max_speed_red], [-vr.max_speed_red, vr.max_speed_red]])
        self.coord = t.Vsum(self.coord, t.Vmult(self.speed, vr.dt))
        t.controlVect(self.coord, [[0, vr.screen_size], [0, vr.screen_size]])
        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        group_line, group_col = self.getGroup()
        if not t.VisEqual((group_line, group_col), self.group):
            vr.particles_groups[self.group[0]][self.group[1]].remove(self.id)
            self.group = (group_line, group_col)
            vr.particles_groups[self.group[0]][self.group[1]].append(self.id)

        return

    def draw(self):
        coord_to_draw = t.Vsum(self.coord, t.Vmult((self.radius, self.radius), -1/2))
        if vr.fancy:
            surface = pg.Surface(vr.screen_size_2, pg.SRCALPHA)
            alpha = self.pressure if self.pressure <= 255 else 255
            pg.draw.circle(surface, (160, 40, 40, alpha), coord_to_draw, self.radius, width=self.radius)
            vr.screen.blit(surface, (0, 0))
        elif vr.display_pressure:
            red = self.pressure * 2 if self.pressure * 2 <= 255 else 255
            color = (red, 255 - red, 255 - red)
            pg.draw.circle(vr.screen, color, coord_to_draw, self.radius, width=self.radius)
        else:
            pg.draw.circle(vr.screen, vr.red_color, coord_to_draw, self.radius, width=self.radius)

        if vr.debug:
            u.Text(f"{t.roundVect(self.accel)}", self.coord, "red", vr.screen, size=3)

        return

    def getInteractionWith(self, particle):
        force = [0, 0]
        v_distance = t.Vsum(particle.coord, t.Vmult(self.coord, -1))
        distance = max(t.norm(v_distance), 0.00001)
        vect_U = [t.s(v_distance[0]), t.s(v_distance[1])]

        if particle.type == BLUE:
            force = t.Vmult(vect_U, ((distance - 20)/distance) * ATTRACT * vr.blue_interaction / max(distance, 1))
        elif particle.type == GREEN:
            force = t.Vmult(vect_U, ((distance - 10)/distance) * ATTRACT * vr.green_interaction / max(distance, 1))
        elif particle.type == RED:
            force = t.Vmult(vect_U, REPULSE * vr.red_interaction / max(distance, 1))
        elif particle.type == YELLOW:
            force = t.Vmult(vect_U, ATTRACT * vr.yellow_interaction / max(distance, 1))

        return force

    def getGroup(self):
        group_size = vr.screen_size / vr.grouping
        line, col = 0, 0
        while (line + 1) * group_size < self.coord[1]:
            line += 1
        while (col + 1) * group_size < self.coord[0]:
            col += 1
        return min(line, vr.grouping - 1), min(col, vr.grouping - 1)

    def getNeighborsId(self):
        neightbors = []
        groups_next = [self.group, [self.group[0] - 1, self.group[1]], [self.group[0] + 1, self.group[1]], [self.group[0], self.group[1] - 1], [self.group[0], self.group[1] + 1]]
        for group in groups_next:
            if t.VerifyVbounds(group, [[0, vr.grouping - 1], [0, vr.grouping - 1]]):
                neightbors = neightbors + self.getParticlesIdGroup(group)
        return neightbors

    def getParticlesIdGroup(self, group):
        ids = []
        for particle_id in vr.particles_groups[group[0]][group[1]]:
            if particle_id != self.id:
                ids.append(particle_id)
        return ids

# --------------------------------------------------------------- #

class ParticleYellow:
    def __init__(self, coord, speed, accel, radius=3):
        self.id, self.type = u.getNewId(), YELLOW
        self.coord, self.speed, self.accel = coord, speed, accel
        self.radius = radius
        self.group = self.getGroup()
        self.pressure = 0

        vr.particles_groups[self.group[0]][self.group[1]].append(self.id)
        vr.particles_dict[self.id] = self
        return

    def update(self):
        self.accel, self.pressure = [0, 0], 0
        for particle_id in self.getNeighborsId():
            force = self.getInteractionWith(vr.particles_dict[particle_id])
            self.accel = t.Vsum(self.accel, force)
            self.pressure += t.norm(force)
        self.pressure = sqrt(self.pressure)

        # Wall
        self.speed[0] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[0]))))

        self.speed[0] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[0])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(vr.screen_size - self.coord[0]))))

        self.speed[1] += 1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction / max(0.1, sqrt(abs(self.coord[1]))))

        self.speed[1] += -1 * vr.wall_interaction * vr.dt / max(0.1, sqrt(abs(vr.screen_size - self.coord[1])))
        self.pressure += sqrt(vr.wall_interaction  / max(0.1, sqrt(abs(vr.screen_size - self.coord[1]))))

        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        for solid in vr.solids:
            if u.IsPointInBox(self.coord, solid.top_left, solid.width, solid.height):
                dist_right = abs(self.coord[0] - (solid.top_left[0] + solid.width))
                dist_left = abs(self.coord[0] - solid.top_left[0])
                dist_bottom = abs(self.coord[1] - (solid.top_left[1] + solid.height))
                dist_top = abs(self.coord[1] - solid.top_left[1])
                if t.isLowerThanALL(dist_left, [dist_top, dist_bottom]) and dist_left < dist_right:
                    self.speed[0] = -1 * dist_left * abs(self.speed[0])
                elif t.isLowerThanALL(dist_right, [dist_top, dist_bottom]):
                    self.speed[0] = 1.1 * dist_right * abs(self.speed[0])
                elif t.isLowerThanALL(dist_top, [dist_left, dist_right]) and dist_top < dist_bottom:
                    self.speed[1] = -1.1 * dist_top * abs(self.speed[1])
                else:
                    self.speed[1] = 1.1 * dist_bottom * abs(self.speed[1])

        if vr.screen_size < self.coord[0] or self.coord[0] < 0:
            self.speed[0] = self.speed[0] * -1
        if vr.screen_size < self.coord[1] or self.coord[1] < 0:
            self.speed[1] = self.speed[1] * -1
        t.controlVect(self.speed, [[-vr.max_speed_red, vr.max_speed_red], [-vr.max_speed_red, vr.max_speed_red]])
        self.coord = t.Vsum(self.coord, t.Vmult(self.speed, vr.dt))
        t.controlVect(self.coord, [[0, vr.screen_size], [0, vr.screen_size]])
        self.speed = t.Vsum(self.speed, t.Vmult(self.accel, 0.5 * vr.dt))

        group_line, group_col = self.getGroup()
        if not t.VisEqual((group_line, group_col), self.group):
            vr.particles_groups[self.group[0]][self.group[1]].remove(self.id)
            self.group = (group_line, group_col)
            vr.particles_groups[self.group[0]][self.group[1]].append(self.id)

        return

    def draw(self):
        coord_to_draw = t.Vsum(self.coord, t.Vmult((self.radius, self.radius), -1/2))
        if vr.fancy:
            surface = pg.Surface(vr.screen_size_2, pg.SRCALPHA)
            alpha = self.pressure if self.pressure <= 255 else 255
            pg.draw.circle(surface, (200, 200, 40, alpha), coord_to_draw, self.radius, width=self.radius)
            vr.screen.blit(surface, (0, 0))
        elif vr.display_pressure:
            red = self.pressure * 2 if self.pressure * 2 <= 255 else 255
            color = (red, 255 - red, 255 - red)
            pg.draw.circle(vr.screen, color, coord_to_draw, self.radius, width=self.radius)
        else:
            pg.draw.circle(vr.screen, vr.yellow_color, coord_to_draw, self.radius, width=self.radius)
        if vr.debug:
            u.Text(f"{t.roundVect(self.accel)}", self.coord, "red", vr.screen, size=3)

        return

    def getInteractionWith(self, particle):
        force = [0, 0]
        v_distance = t.Vsum(particle.coord, t.Vmult(self.coord, -1))
        distance = max(t.norm(v_distance), 0.00001)
        vect_U = [t.s(v_distance[0]), t.s(v_distance[1])]

        if particle.type == BLUE:
            force = t.Vmult(vect_U, REPULSE * vr.blue_interaction / max(distance, 1))
        elif particle.type == GREEN:
            force = t.Vmult(vect_U, ATTRACT * 2 * vr.green_interaction / max(distance, 1))
        elif particle.type == RED:
            force = t.Vmult(vect_U, REPULSE * 2 * vr.red_interaction / max(distance, 1))
        elif particle.type == YELLOW:
            force = t.Vmult(vect_U,  ((distance - 20)/distance) * ATTRACT * vr.yellow_interaction / max(distance, 1))

        return force

    def getGroup(self):
        group_size = vr.screen_size / vr.grouping
        line, col = 0, 0
        while (line + 1) * group_size < self.coord[1]:
            line += 1
        while (col + 1) * group_size < self.coord[0]:
            col += 1
        return min(line, vr.grouping - 1), min(col, vr.grouping - 1)

    def getNeighborsId(self):
        neightbors = []
        groups_next = [self.group, [self.group[0] - 1, self.group[1]], [self.group[0] + 1, self.group[1]], [self.group[0], self.group[1] - 1], [self.group[0], self.group[1] + 1]]
        for group in groups_next:
            if t.VerifyVbounds(group, [[0, vr.grouping - 1], [0, vr.grouping - 1]]):
                neightbors = neightbors + self.getParticlesIdGroup(group)
        return neightbors

    def getParticlesIdGroup(self, group):
        ids = []
        for particle_id in vr.particles_groups[group[0]][group[1]]:
            if particle_id != self.id:
                ids.append(particle_id)
        return ids