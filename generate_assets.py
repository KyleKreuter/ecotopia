"""Generate pixel art assets for Ecotopia game."""
from PIL import Image, ImageDraw

CHAR_DIR = "/root/clawd/hackathon-workspace/ecotopia/frontend/public/assets/character"
TILE_DIR = "/root/clawd/hackathon-workspace/ecotopia/frontend/public/assets/tiles"

# Skin tones
SKIN_LIGHT = (255, 219, 172)
SKIN_MED = (234, 192, 147)
SKIN_TAN = (210, 170, 120)
SKIN_DARK = (180, 140, 100)

# Common colors
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def make_char(size=64):
    """Create blank RGBA character image."""
    return Image.new("RGBA", (size, size), TRANSPARENT)


def draw_head(draw, cx, top, skin, width=20, height=22):
    """Draw a head shape centered at cx, starting at top."""
    draw.rounded_rectangle(
        [cx - width // 2, top, cx + width // 2, top + height],
        radius=6, fill=skin
    )


def draw_eyes(draw, cx, ey, color=BLACK, spacing=6):
    """Draw two pixel eyes."""
    for dx in [-spacing // 2, spacing // 2]:
        draw.rectangle([cx + dx - 1, ey, cx + dx + 1, ey + 1], fill=color)


def draw_mouth(draw, cx, my, width=6, smile=True):
    """Draw a simple mouth."""
    if smile:
        draw.line([cx - width // 2, my, cx - 1, my + 1], fill=BLACK)
        draw.line([cx + 1, my + 1, cx + width // 2, my], fill=BLACK)
    else:
        draw.line([cx - width // 2, my, cx + width // 2, my], fill=BLACK)


def draw_body(draw, cx, top, bottom, color, width=26):
    """Draw torso rectangle."""
    draw.rectangle([cx - width // 2, top, cx + width // 2, bottom], fill=color)


def generate_karl():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Brown hair
    d.rounded_rectangle([21, 10, 43, 18], radius=4, fill=(101, 67, 33))
    d.rectangle([21, 14, 43, 20], fill=(101, 67, 33))
    # Head
    draw_head(d, cx, 14, SKIN_MED, 22, 24)
    # Square jaw - widen bottom
    d.rectangle([22, 30, 42, 38], fill=SKIN_MED)
    # Eyes - serious
    draw_eyes(d, cx, 24, BLACK, 8)
    # Eyebrows
    d.line([25, 22, 29, 22], fill=(80, 50, 20))
    d.line([35, 22, 39, 22], fill=(80, 50, 20))
    # Mouth - flat serious
    draw_mouth(d, cx, 33, 6, smile=False)
    # Blue work shirt
    draw_body(d, cx, 39, 63, (50, 80, 160), 28)
    # Collar
    d.polygon([(28, 39), (32, 45), (36, 39)], fill=(40, 65, 130))
    img.save(f"{CHAR_DIR}/karl.png")


def generate_mia():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Green hair - long
    d.rounded_rectangle([19, 8, 45, 22], radius=5, fill=(34, 170, 60))
    d.rectangle([19, 16, 23, 38], fill=(34, 170, 60))
    d.rectangle([41, 16, 45, 38], fill=(34, 170, 60))
    # Head
    draw_head(d, cx, 14, SKIN_LIGHT, 20, 22)
    # Eyes - determined
    draw_eyes(d, cx, 23, (40, 100, 40), 8)
    d.line([25, 21, 29, 22], fill=(34, 140, 50))
    d.line([35, 22, 39, 21], fill=(34, 140, 50))
    # Small nose
    d.point((32, 27), fill=(230, 200, 155))
    # Determined mouth
    d.line([29, 31, 35, 31], fill=(200, 100, 100))
    # Green hoodie
    draw_body(d, cx, 37, 63, (34, 140, 50), 28)
    # Hood strings
    d.line([29, 37, 29, 45], fill=WHITE)
    d.line([35, 37, 35, 45], fill=WHITE)
    img.save(f"{CHAR_DIR}/mia.png")


def generate_sarah():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Dark hair in bun
    d.ellipse([26, 4, 38, 16], fill=(40, 30, 20))
    d.rounded_rectangle([22, 10, 42, 20], radius=4, fill=(40, 30, 20))
    # Head - sharp
    draw_head(d, cx, 14, SKIN_LIGHT, 20, 22)
    # Sharp cheekbones
    d.line([22, 28, 25, 25], fill=(240, 205, 160))
    d.line([42, 28, 39, 25], fill=(240, 205, 160))
    # Eyes
    draw_eyes(d, cx, 23, (60, 40, 30), 8)
    # Confident smirk
    d.line([29, 32, 32, 31], fill=(180, 70, 70))
    d.line([32, 31, 37, 33], fill=(180, 70, 70))
    # Red blazer
    draw_body(d, cx, 37, 63, (180, 40, 40), 28)
    # Lapels
    d.polygon([(28, 37), (32, 48), (32, 37)], fill=(150, 30, 30))
    d.polygon([(36, 37), (32, 48), (32, 37)], fill=(150, 30, 30))
    # White shirt underneath
    d.rectangle([30, 37, 34, 50], fill=WHITE)
    img.save(f"{CHAR_DIR}/sarah.png")


def generate_bernd():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Gray hair
    d.rounded_rectangle([21, 10, 43, 20], radius=4, fill=(160, 160, 155))
    # Head - weathered
    draw_head(d, cx, 14, SKIN_TAN, 22, 24)
    # Gray beard
    d.rounded_rectangle([24, 30, 40, 40], radius=4, fill=(150, 150, 145))
    # Wise eyes
    d.rectangle([26, 23, 29, 25], fill=(80, 120, 80))
    d.rectangle([35, 23, 38, 25], fill=(80, 120, 80))
    # Crow's feet
    d.point((24, 23), fill=(190, 155, 108))
    d.point((40, 23), fill=(190, 155, 108))
    # Mouth hidden in beard
    d.line([29, 34, 35, 34], fill=(130, 130, 125))
    # Brown/green flannel
    draw_body(d, cx, 40, 63, (90, 110, 70), 28)
    # Flannel pattern
    for y in range(40, 64, 4):
        d.line([18, y, 46, y], fill=(110, 80, 50))
    for x in range(18, 47, 6):
        d.line([x, 40, x, 63], fill=(110, 80, 50))
    img.save(f"{CHAR_DIR}/bernd.png")


def generate_henning():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Straw hat
    d.rectangle([16, 8, 48, 12], fill=(220, 190, 120))
    d.rounded_rectangle([22, 4, 42, 12], radius=3, fill=(210, 180, 110))
    d.line([16, 12, 48, 12], fill=(180, 150, 90))
    # White hair
    d.rectangle([23, 12, 41, 18], fill=(230, 230, 225))
    # Head - sun-tanned
    draw_head(d, cx, 14, SKIN_TAN, 20, 22)
    # Eyes
    draw_eyes(d, cx, 23, (100, 80, 50), 8)
    # Smile wrinkles
    d.line([28, 32, 36, 32], fill=(180, 140, 100))
    d.arc([27, 30, 37, 35], 0, 180, fill=(160, 120, 80))
    # Plaid shirt
    draw_body(d, cx, 37, 63, (180, 60, 60), 26)
    for y in range(37, 64, 5):
        d.line([19, y, 45, y], fill=(200, 200, 80))
    for x in range(19, 46, 5):
        d.line([x, 37, x, 63], fill=(200, 200, 80))
    img.save(f"{CHAR_DIR}/henning.png")


def generate_kerstin():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Brown hair
    d.rounded_rectangle([20, 10, 44, 22], radius=5, fill=(139, 90, 43))
    d.rectangle([20, 16, 24, 36], fill=(139, 90, 43))
    d.rectangle([40, 16, 44, 36], fill=(139, 90, 43))
    # Head
    draw_head(d, cx, 14, SKIN_LIGHT, 20, 22)
    # Glasses
    d.rectangle([24, 22, 30, 27], outline=(60, 60, 60))
    d.rectangle([34, 22, 40, 27], outline=(60, 60, 60))
    d.line([30, 24, 34, 24], fill=(60, 60, 60))
    # Eyes behind glasses
    d.rectangle([26, 24, 28, 25], fill=(80, 60, 40))
    d.rectangle([36, 24, 38, 25], fill=(80, 60, 40))
    # Friendly smile
    d.arc([28, 30, 36, 36], 0, 180, fill=(200, 100, 100))
    # Yellow sweater
    draw_body(d, cx, 37, 63, (230, 200, 60), 26)
    # Neckline
    d.arc([27, 35, 37, 42], 0, 180, fill=(210, 180, 40))
    img.save(f"{CHAR_DIR}/kerstin.png")


def generate_lena():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Blonde hair
    d.rounded_rectangle([20, 9, 44, 22], radius=5, fill=(240, 210, 130))
    d.rectangle([20, 16, 24, 34], fill=(240, 210, 130))
    d.rectangle([40, 16, 44, 34], fill=(240, 210, 130))
    # Head
    draw_head(d, cx, 14, SKIN_LIGHT, 20, 22)
    # Kind eyes
    d.rectangle([26, 23, 28, 25], fill=(80, 130, 180))
    d.rectangle([36, 23, 38, 25], fill=(80, 130, 180))
    # Gentle smile
    d.arc([28, 30, 36, 35], 0, 180, fill=(200, 120, 120))
    # White/blue medical top
    draw_body(d, cx, 37, 63, WHITE, 26)
    # Blue trim
    d.rectangle([19, 37, 45, 40], fill=(100, 160, 220))
    d.line([32, 37, 32, 63], fill=(100, 160, 220))
    # Cross
    d.rectangle([30, 44, 34, 52], fill=(200, 60, 60))
    d.rectangle([28, 46, 36, 50], fill=(200, 60, 60))
    img.save(f"{CHAR_DIR}/lena.png")


def generate_oleg():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Short dark hair
    d.rounded_rectangle([22, 10, 42, 18], radius=3, fill=(40, 35, 30))
    # Head
    draw_head(d, cx, 14, SKIN_MED, 20, 22)
    # Goggles on forehead
    d.rectangle([24, 13, 30, 17], outline=(80, 80, 80), fill=(180, 220, 240))
    d.rectangle([34, 13, 40, 17], outline=(80, 80, 80), fill=(180, 220, 240))
    d.line([30, 15, 34, 15], fill=(80, 80, 80))
    # Eyes
    draw_eyes(d, cx, 24, BLACK, 8)
    # Neutral mouth
    draw_mouth(d, cx, 32, 6, smile=False)
    # Orange safety vest
    draw_body(d, cx, 37, 63, (240, 150, 30), 28)
    # Reflective stripes
    d.line([18, 48, 46, 48], fill=(255, 255, 200))
    d.line([18, 55, 46, 55], fill=(255, 255, 200))
    img.save(f"{CHAR_DIR}/oleg.png")


def generate_pavel():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Messy brown hair
    d.rounded_rectangle([20, 9, 44, 20], radius=4, fill=(100, 70, 40))
    for x in [21, 25, 30, 36, 41]:
        d.rectangle([x, 7, x + 2, 13], fill=(110, 75, 42))
    # Head
    draw_head(d, cx, 14, SKIN_MED, 20, 22)
    # Stubble
    for x in range(25, 40, 2):
        for y in range(32, 37, 2):
            d.point((x, y), fill=(140, 110, 80))
    # Eyes
    draw_eyes(d, cx, 23, (70, 90, 110), 8)
    # Slight frown
    d.line([28, 33, 36, 32], fill=(180, 130, 100))
    # Dark blue jacket
    draw_body(d, cx, 37, 63, (40, 50, 90), 26)
    # Collar
    d.polygon([(25, 37), (32, 44), (32, 37)], fill=(30, 40, 75))
    d.polygon([(39, 37), (32, 44), (32, 37)], fill=(30, 40, 75))
    img.save(f"{CHAR_DIR}/pavel.png")


def generate_yuki():
    img = make_char()
    d = ImageDraw.Draw(img)
    cx = 32
    # Black hair with bangs
    d.rounded_rectangle([20, 9, 44, 22], radius=5, fill=(20, 18, 25))
    d.rectangle([20, 16, 24, 36], fill=(20, 18, 25))
    d.rectangle([40, 16, 44, 36], fill=(20, 18, 25))
    # Bangs
    d.rectangle([23, 14, 41, 20], fill=(20, 18, 25))
    # Head
    draw_head(d, cx, 16, SKIN_LIGHT, 18, 20)
    # Round glasses
    d.ellipse([24, 23, 30, 29], outline=(80, 60, 40))
    d.ellipse([34, 23, 40, 29], outline=(80, 60, 40))
    d.line([30, 26, 34, 26], fill=(80, 60, 40))
    # Eyes behind glasses
    d.rectangle([26, 25, 28, 26], fill=(40, 30, 20))
    d.rectangle([36, 25, 38, 26], fill=(40, 30, 20))
    # Small smile
    d.arc([29, 31, 35, 35], 0, 180, fill=(200, 120, 120))
    # Purple scarf
    d.rectangle([20, 36, 44, 42], fill=(120, 60, 160))
    d.rectangle([22, 42, 26, 50], fill=(120, 60, 160))
    # Dark top
    draw_body(d, cx, 42, 63, (60, 50, 80), 26)
    img.save(f"{CHAR_DIR}/yuki.png")


# TILE GENERATION (32x32)

def make_tile(size=32):
    return Image.new("RGBA", (size, size), TRANSPARENT)


def fill_ground(d, color, size=32):
    d.rectangle([0, 0, size - 1, size - 1], fill=color)


def generate_empty():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Grass texture
    for x in range(2, 30, 4):
        for y in range(2, 30, 6):
            d.line([x, y + 3, x, y], fill=(120, 175, 60))
            d.line([x + 1, y + 2, x + 2, y], fill=(145, 200, 80))
    img.save(f"{TILE_DIR}/empty.png")


def generate_forest():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (60, 120, 40))
    # Trees
    for cx, cy in [(8, 10), (22, 8), (14, 18), (26, 20)]:
        d.rectangle([cx - 1, cy + 6, cx + 1, cy + 10], fill=(100, 70, 40))
        d.polygon([(cx, cy - 4), (cx - 5, cy + 6), (cx + 5, cy + 6)], fill=(30, 100, 30))
        d.polygon([(cx, cy - 7), (cx - 4, cy + 2), (cx + 4, cy + 2)], fill=(40, 120, 40))
    img.save(f"{TILE_DIR}/forest.png")


def generate_wasteland():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (160, 140, 110))
    # Cracks
    d.line([4, 8, 14, 12], fill=(120, 100, 80))
    d.line([14, 12, 10, 22], fill=(120, 100, 80))
    d.line([20, 4, 24, 16], fill=(130, 110, 85))
    d.line([24, 16, 28, 28], fill=(130, 110, 85))
    # Rocks
    d.ellipse([2, 24, 8, 28], fill=(140, 130, 115))
    d.ellipse([22, 22, 28, 26], fill=(145, 135, 118))
    img.save(f"{TILE_DIR}/wasteland.png")


def generate_ocean():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (40, 100, 180))
    # Waves
    for y in range(0, 32, 6):
        d.arc([0, y, 16, y + 8], 0, 180, fill=(60, 130, 210))
        d.arc([16, y + 3, 32, y + 11], 0, 180, fill=(50, 120, 200))
    img.save(f"{TILE_DIR}/ocean.png")


def generate_river():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (70, 150, 220))
    # Flow lines
    for y in range(2, 30, 5):
        d.line([4, y, 12, y + 2], fill=(100, 180, 240))
        d.line([18, y + 1, 26, y + 3], fill=(90, 170, 235))
    # Sparkle
    d.point((15, 10), fill=WHITE)
    d.point((8, 20), fill=WHITE)
    img.save(f"{TILE_DIR}/river.png")


def generate_factory():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Building
    d.rectangle([4, 12, 24, 30], fill=(120, 120, 130))
    # Chimney
    d.rectangle([6, 4, 10, 12], fill=(100, 100, 110))
    # Smoke
    d.ellipse([4, 0, 12, 6], fill=(180, 180, 180, 160))
    d.ellipse([8, -2, 16, 4], fill=(200, 200, 200, 120))
    # Windows
    d.rectangle([8, 16, 12, 20], fill=(200, 200, 100))
    d.rectangle([16, 16, 20, 20], fill=(200, 200, 100))
    # Door
    d.rectangle([13, 24, 17, 30], fill=(80, 80, 90))
    img.save(f"{TILE_DIR}/factory.png")


def generate_clean_factory():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Modern building
    d.rectangle([4, 10, 26, 30], fill=(220, 230, 240))
    # Blue accents
    d.rectangle([4, 10, 26, 13], fill=(100, 160, 220))
    # Windows
    for x in range(7, 24, 5):
        d.rectangle([x, 16, x + 3, 22], fill=(150, 200, 240))
    # Solar panel on roof
    d.rectangle([14, 7, 22, 10], fill=(50, 80, 140))
    img.save(f"{TILE_DIR}/clean_factory.png")


def generate_solar_farm():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (110, 170, 60))
    # Solar panels in rows
    for y in [6, 14, 22]:
        d.polygon([(4, y + 6), (4, y + 2), (28, y), (28, y + 4)], fill=(40, 60, 140))
        # Reflection
        d.line([6, y + 3, 26, y + 1], fill=(80, 120, 200))
        d.line([6, y + 5, 26, y + 3], fill=(60, 90, 170))
    img.save(f"{TILE_DIR}/solar_farm.png")


def generate_wind_farm():
    img = make_tile()
    d = ImageDraw.Draw(img)
    # Green hills
    fill_ground(d, (100, 170, 60))
    d.arc([-8, 16, 40, 40], 180, 360, fill=(90, 155, 50))
    # Turbines
    for cx in [10, 24]:
        d.rectangle([cx - 1, 8, cx + 1, 28], fill=(220, 220, 220))
        # Blades
        d.line([cx, 8, cx - 6, 2], fill=WHITE, width=1)
        d.line([cx, 8, cx + 5, 3], fill=WHITE, width=1)
        d.line([cx, 8, cx + 1, 16], fill=WHITE, width=1)
        d.ellipse([cx - 1, 7, cx + 1, 9], fill=(200, 200, 200))
    img.save(f"{TILE_DIR}/wind_farm.png")


def generate_research_lab():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # White building
    d.rectangle([4, 12, 26, 30], fill=(230, 235, 240))
    # Blue glow base
    d.rectangle([3, 28, 27, 31], fill=(80, 160, 240, 100))
    # Antenna
    d.rectangle([14, 2, 16, 12], fill=(180, 180, 190))
    d.ellipse([12, 0, 18, 6], fill=(80, 160, 255))
    # Windows
    d.rectangle([7, 16, 12, 22], fill=(150, 200, 250))
    d.rectangle([18, 16, 23, 22], fill=(150, 200, 250))
    img.save(f"{TILE_DIR}/research_lab.png")


def generate_coal_plant():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Dark building
    d.rectangle([4, 14, 24, 30], fill=(70, 65, 65))
    # Two smoke stacks
    for x in [8, 18]:
        d.rectangle([x - 2, 4, x + 2, 14], fill=(60, 55, 55))
        # Black smoke
        d.ellipse([x - 4, -2, x + 4, 6], fill=(50, 50, 50, 180))
        d.ellipse([x - 3, -5, x + 5, 3], fill=(40, 40, 40, 140))
    # Dirty windows
    d.rectangle([8, 18, 12, 22], fill=(160, 140, 80))
    d.rectangle([16, 18, 20, 22], fill=(160, 140, 80))
    img.save(f"{TILE_DIR}/coal_plant.png")


def generate_residential():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # House 1
    d.rectangle([2, 16, 14, 28], fill=(220, 180, 140))
    d.polygon([(2, 16), (8, 8), (14, 16)], fill=(180, 60, 50))
    d.rectangle([6, 22, 10, 28], fill=(120, 80, 50))
    # House 2
    d.rectangle([18, 14, 30, 28], fill=(200, 200, 180))
    d.polygon([(18, 14), (24, 6), (30, 14)], fill=(100, 80, 60))
    d.rectangle([20, 18, 24, 22], fill=(180, 210, 240))
    img.save(f"{TILE_DIR}/residential.png")


def generate_commercial():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Shop building
    d.rectangle([2, 10, 28, 30], fill=(230, 220, 200))
    # Awning
    d.polygon([(0, 10), (0, 16), (30, 16), (30, 10)], fill=(200, 60, 50))
    d.polygon([(0, 13), (5, 16), (10, 13), (15, 16), (20, 13), (25, 16), (30, 13)],
              fill=(180, 50, 40))
    # Shop windows
    d.rectangle([4, 18, 12, 26], fill=(180, 220, 240))
    d.rectangle([16, 18, 24, 26], fill=(180, 220, 240))
    # Door
    d.rectangle([12, 22, 16, 30], fill=(120, 80, 50))
    img.save(f"{TILE_DIR}/commercial.png")


def generate_farmland():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (180, 160, 90))
    # Wheat rows
    for x in range(2, 30, 4):
        d.line([x, 2, x, 30], fill=(160, 140, 70))
        for y in range(4, 28, 5):
            d.ellipse([x - 1, y - 2, x + 2, y + 1], fill=(220, 190, 60))
            d.ellipse([x, y, x + 3, y + 3], fill=(210, 180, 50))
    img.save(f"{TILE_DIR}/farmland.png")


def generate_dead_farmland():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (150, 120, 80))
    # Dead crop rows
    for x in range(2, 30, 4):
        d.line([x, 4, x, 28], fill=(120, 95, 60))
        for y in range(6, 26, 6):
            d.line([x - 2, y, x, y - 3], fill=(130, 100, 65))
            d.line([x + 2, y, x, y - 3], fill=(130, 100, 65))
    img.save(f"{TILE_DIR}/dead_farmland.png")


def generate_city_inner():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (100, 100, 105))
    # Tall buildings
    d.rectangle([2, 4, 10, 30], fill=(140, 150, 170))
    d.rectangle([12, 8, 20, 30], fill=(160, 160, 175))
    d.rectangle([22, 2, 30, 30], fill=(130, 140, 160))
    # Windows (lit)
    for bx, by, bw in [(2, 4, 10), (12, 8, 20), (22, 2, 30)]:
        for x in range(bx + 1, bw - 1, 3):
            for y in range(by + 2, 28, 4):
                color = (255, 240, 140) if (x + y) % 5 != 0 else (100, 100, 120)
                d.rectangle([x, y, x + 1, y + 1], fill=color)
    img.save(f"{TILE_DIR}/city_inner.png")


def generate_city_outer():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Suburban houses
    for bx, color in [(2, (210, 190, 170)), (18, (190, 200, 180))]:
        d.rectangle([bx, 18, bx + 12, 30], fill=color)
        d.polygon([(bx, 18), (bx + 6, 10), (bx + 12, 18)], fill=(160, 80, 60))
        d.rectangle([bx + 4, 24, bx + 8, 30], fill=(100, 70, 45))
    # Road
    d.rectangle([14, 20, 18, 30], fill=(100, 100, 105))
    img.save(f"{TILE_DIR}/city_outer.png")


def generate_carbon_capture():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Dome
    d.arc([4, 6, 28, 30], 180, 360, fill=(100, 180, 240))
    d.ellipse([6, 10, 26, 28], fill=(180, 210, 240))
    # Blue glow
    d.ellipse([10, 14, 22, 24], fill=(80, 160, 255))
    d.ellipse([12, 16, 20, 22], fill=(120, 200, 255))
    # Tech lines
    d.line([8, 20, 24, 20], fill=(60, 140, 220))
    d.line([16, 12, 16, 26], fill=(60, 140, 220))
    img.save(f"{TILE_DIR}/carbon_capture.png")


def generate_clean_river():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (80, 170, 230))
    # Clear water sparkles
    for x, y in [(6, 8), (18, 14), (10, 24), (24, 6), (28, 22)]:
        d.point((x, y), fill=(220, 240, 255))
        d.point((x + 1, y), fill=(200, 230, 255))
    # Flow
    for y in range(3, 30, 6):
        d.arc([2, y, 18, y + 8], 0, 180, fill=(110, 190, 245))
    img.save(f"{TILE_DIR}/clean_river.png")


def generate_nuclear_plant():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Cooling towers
    for cx in [10, 22]:
        d.polygon([(cx - 5, 28), (cx - 3, 10), (cx + 3, 10), (cx + 5, 28)], fill=(200, 200, 205))
        d.ellipse([cx - 3, 8, cx + 3, 13], fill=(210, 210, 215))
        # Steam
        d.ellipse([cx - 3, 2, cx + 3, 9], fill=(230, 230, 235, 150))
    # Base building
    d.rectangle([6, 24, 26, 30], fill=(180, 180, 185))
    img.save(f"{TILE_DIR}/nuclear_plant.png")


def generate_park():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (110, 190, 70))
    # Tree
    d.rectangle([6, 14, 8, 22], fill=(120, 80, 40))
    d.ellipse([2, 6, 12, 16], fill=(50, 140, 50))
    # Bench
    d.rectangle([16, 20, 28, 22], fill=(140, 90, 40))
    d.rectangle([17, 22, 19, 26], fill=(120, 75, 35))
    d.rectangle([25, 22, 27, 26], fill=(120, 75, 35))
    # Flowers
    for x, y, c in [(20, 10, (255, 80, 80)), (24, 14, (255, 200, 50)), (14, 8, (200, 80, 200))]:
        d.ellipse([x - 1, y - 1, x + 2, y + 2], fill=c)
        d.line([x, y + 2, x, y + 5], fill=(60, 130, 40))
    # Path
    d.line([14, 28, 14, 16], fill=(190, 175, 140), width=2)
    img.save(f"{TILE_DIR}/park.png")


def generate_recycling_center():
    img = make_tile()
    d = ImageDraw.Draw(img)
    fill_ground(d, (134, 190, 72))
    # Green building
    d.rectangle([4, 10, 28, 30], fill=(50, 150, 60))
    # Roof
    d.rectangle([2, 8, 30, 12], fill=(40, 130, 50))
    # Recycling symbol (simplified triangular arrows)
    cx, cy = 16, 20
    d.polygon([(cx, cy - 5), (cx - 5, cy + 3), (cx + 5, cy + 3)], outline=WHITE)
    # Arrow hints
    d.line([cx + 2, cy - 2, cx + 4, cy - 1], fill=WHITE)
    d.line([cx - 4, cy + 1, cx - 2, cy + 3], fill=WHITE)
    d.line([cx + 1, cy + 4, cx - 1, cy + 3], fill=WHITE)
    # Door
    d.rectangle([14, 24, 18, 30], fill=(40, 120, 45))
    img.save(f"{TILE_DIR}/recycling_center.png")


if __name__ == "__main__":
    # Characters
    generate_karl()
    generate_mia()
    generate_sarah()
    generate_bernd()
    generate_henning()
    generate_kerstin()
    generate_lena()
    generate_oleg()
    generate_pavel()
    generate_yuki()

    # Tiles
    generate_empty()
    generate_forest()
    generate_wasteland()
    generate_ocean()
    generate_river()
    generate_factory()
    generate_clean_factory()
    generate_solar_farm()
    generate_wind_farm()
    generate_research_lab()
    generate_coal_plant()
    generate_residential()
    generate_commercial()
    generate_farmland()
    generate_dead_farmland()
    generate_city_inner()
    generate_city_outer()
    generate_carbon_capture()
    generate_clean_river()
    generate_nuclear_plant()
    generate_park()
    generate_recycling_center()

    print("All assets generated!")
