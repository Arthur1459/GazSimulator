# Config :
game_name = "Game Of Life V1"
icon = None

debug = False
fancy = False
display_pressure = False

base_size = 600
screen_size = 800
screen_size_2 = (screen_size, screen_size)
top_left, top_right, bot_left, bot_right = (0, 0), (screen_size, 0), (0, screen_size), (screen_size, screen_size)
center = (screen_size//2, screen_size//2)
screen_factor = screen_size / base_size
fullscreen = False

back_color = (10, 10, 10)
font, default_sizes = "./ressources/pixel.ttf", {0: 4, 1: 6, 2: 8, 3: 12, 4: 18, 5: 32, 6: 48, 7: 64, 8: 96}

cursor = (0, 0)
screen = None
fps = 120
dt_blocking = 1 / fps

solids = []
solid_selected = False

grouping = 18
persistence = 50

# Particles Parameters:
wall_interaction = 1000

blue_color = (40, 40, 160)
nb_blue_particles = 0
max_speed_blue = 25
blue_interaction = 8000

green_color = (40, 160, 40)
nb_green_particles = 0
max_speed_green = 100
green_interaction = 15000

red_color = (160, 40, 40)
nb_red_particles = 0
max_speed_red = 100
red_interaction = 10000

yellow_color = (200, 200, 40)
nb_yellow_particles = 0
max_speed_yellow = 100
yellow_interaction = 8000

# Current :
running = False
clock = None
t_start = 0
t, dt, frames, t_frames, real_fps = 0, 0, 0, 0, 0

inputs = {}
wait_key = 0

id = 0
particles = []
atmosphere = None
particles_dict = {}
particles_dict_type = {"blue": [], "green": [], "red": []}
particles_groups = []
