import pygame, sys, random, time, os

pygame.init()
pygame.mixer.init()

# ============ НАЛАШТУВАННЯ ВІКНА ============
W, H = 960, 540
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Terraria Clone: Final Fix")
clock = pygame.time.Clock()

TILE = 32
WORLD_W = 200
WORLD_H = 80
GRAVITY = 0.8
DAY_TIME = 300
NIGHT_TIME = 180

# ============ ЗАВАНТАЖЕННЯ ГРАФІКИ (КАРТИНКИ) ============
assets = {}

def load_img(key, file_name, size=(TILE, TILE)):
    try:
        if os.path.exists(file_name):
            img = pygame.image.load(file_name).convert_alpha()
            img = pygame.transform.scale(img, size)
            assets[key] = img
    except Exception:
        pass

# --- ТУТ ЗАВАНТАЖУЮТЬСЯ ТЕКСТУРИ БЛОКІВ ---
load_img("dirt", "dirt.png")        # Земля
load_img("grass", "grass.png")      # Трава
load_img("stone", "stone.png")      # Камінь
load_img("coal", "vygol.png")       # Вугілля
load_img("iron", "iron.png")        # Залізо
load_img("gold", "gold.png")        # Золото
load_img("diamond", "diamant.png")  # Алмази
load_img("wood", "tree.png")        # Дерево (ствобур)
load_img("leaves", "listya.png")    # Листя
load_img("planks", "doski.png")     # Дошки

# --- ТУТ ЗАВАНТАЖУЮТЬСЯ ІНСТРУМЕНТИ ТА ГРАВЕЦЬ ---
load_img("wood_pickaxe", "kailo.png") # Кирка
load_img("wood_axe", "topor.png")     # Сокира
load_img("wood_sword", "sword.png")   # Меч
load_img("player", "gg.png", (24, 40)) # Персонаж (розмір 24x40)

# --- ТУТ ЗАВАНТАЖУЮТЬСЯ ФОНИ ДЛЯ МЕНЮ ---
menu_images = []
for name in ["menu1.png", "menu2.png", "menu3.png"]:
    if os.path.exists(name):
        bg = pygame.image.load(name).convert()
        bg = pygame.transform.scale(bg, (W, H))
        menu_images.append(bg)

# ============ АУДІО СИСТЕМА (ЗВУКИ) ============
music_files = {
    "menu": "06. Title Screen.mp3",    # Музика в головному меню
    "day": "01. Overworld Day.mp3",    # Музика вдень на поверхні
    "cave": "04. Underground.mp3"      # Музика в печерах
}
current_music = None

def play_music(track_key):
    global current_music
    file_path = music_files.get(track_key)
    if file_path and os.path.exists(file_path):
        if current_music != track_key:
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play(-1) # -1 означає безкінечний повтор
                pygame.mixer.music.set_volume(0.4)
                current_music = track_key
            except: pass

# ============ НАЛАШТУВАННЯ БЛОКІВ ТА ІНСТРУМЕНТІВ ============
BLOCK_DATA = {
    "grass":     {"tool": "shovel", "hard": 15, "hand_break": True},
    "dirt":      {"tool": "shovel", "hard": 15, "hand_break": True},
    "stone":     {"tool": "pickaxe", "hard": 60, "hand_break": False},
    "coal":      {"tool": "pickaxe", "hard": 70, "hand_break": False},
    "iron":      {"tool": "pickaxe", "hard": 80, "hand_break": False},
    "gold":      {"tool": "pickaxe", "hard": 90, "hand_break": False},
    "diamond":   {"tool": "pickaxe", "hard": 120, "hand_break": False},
    "wood":      {"tool": "axe",     "hard": 40, "hand_break": True},
    "leaves":    {"tool": "axe",     "hard": 5,  "hand_break": True},
    "planks":    {"tool": "axe",     "hard": 20, "hand_break": True},
}

TOOLS_INFO = {
    "wood_pickaxe": ("pickaxe", 2),
    "wood_axe":     ("axe", 2),
    "wood_sword":   ("sword", 1)
}

RECIPES = {
    "planks":       {"need": {"wood": 1},              "give": 4},
    "stick":        {"need": {"planks": 2},            "give": 4},
    "wood_pickaxe": {"need": {"planks": 3, "stick": 2}, "give": 1},
    "wood_axe":     {"need": {"planks": 3, "stick": 2}, "give": 1},
    "wood_sword":   {"need": {"planks": 2, "stick": 1}, "give": 1},
}

# ============ ГЕНЕРАЦІЯ СВІТУ ============
world = [[None for _ in range(WORLD_W)] for _ in range(WORLD_H)]
surface_heights = []

h = 40
for x in range(WORLD_W):
    h += random.choice([-1, 0, 1])
    h = max(30, min(50, h))
    surface_heights.append(h)
    for y in range(WORLD_H):
        if y == h: world[y][x] = "grass"
        elif y > h:
            if y < h + 4: world[y][x] = "dirt"
            else: world[y][x] = "stone"

for _ in range(150):
    cx, cy = random.randint(0, WORLD_W-1), random.randint(45, WORLD_H-5)
    r = random.randint(2, 6)
    for y in range(cy-r, cy+r):
        for x in range(cx-r, cx+r):
            if 0 <= x < WORLD_W and 0 <= y < WORLD_H:
                if random.random() > 0.4: world[y][x] = None

def generate_ore(name, chance, min_depth):
    for y in range(min_depth, WORLD_H):
        for x in range(WORLD_W):
            if world[y][x] == "stone" and random.random() < chance:
                world[y][x] = name

generate_ore("coal", 0.02, 42)
generate_ore("iron", 0.015, 48)
generate_ore("gold", 0.01, 55)
generate_ore("diamond", 0.005, 65)

for x in range(5, WORLD_W-5, 8):
    if random.random() < 0.7:
        y = surface_heights[x]
        tree_h = random.randint(4, 7)
        for i in range(tree_h):
            world[y - i][x] = "wood"
        for lx in range(x-2, x+3):
            for ly in range(y-tree_h-2, y-tree_h+1):
                if 0 <= lx < WORLD_W and 0 <= ly < WORLD_H:
                    if world[ly][lx] is None: world[ly][lx] = "leaves"

# ============ ГРАВЕЦЬ ============
player = pygame.Rect(WORLD_W//2 * TILE, 0, 24, 40)
player.y = (surface_heights[WORLD_W//2] - 5) * TILE
vel_y = 0
speed = 5
jump_power = -13
on_ground = False

hp = 100
max_hp = 100
hunger = 100
last_hunger_update = time.time()

# ============ ІНВЕНТАР ============
INV_W = 8
inventory = [None for _ in range(INV_W)]
selected_slot = 0
show_craft_menu = False

inventory[0] = {"name": "wood_pickaxe", "count": 1}
inventory[1] = {"name": "wood_axe", "count": 1}
inventory[2] = {"name": "wood_sword", "count": 1}

def add_to_inventory(item_name, amount=1):
    for i in range(INV_W):
        if inventory[i] and inventory[i]["name"] == item_name:
            inventory[i]["count"] += amount
            return True
    for i in range(INV_W):
        if inventory[i] is None:
            inventory[i] = {"name": item_name, "count": amount}
            return True
    return False

def remove_from_inventory(item_name, amount=1):
    for i in range(INV_W):
        if inventory[i] and inventory[i]["name"] == item_name:
            if inventory[i]["count"] >= amount:
                inventory[i]["count"] -= amount
                if inventory[i]["count"] <= 0:
                    inventory[i] = None
                return True
    return False

def has_item(item_name, amount=1):
    count = 0
    for i in range(INV_W):
        if inventory[i] and inventory[i]["name"] == item_name:
            count += inventory[i]["count"]
    return count >= amount

# ============ ЗМІННІ ГРИ ============
cam_x, cam_y = 0, 0
mining_time = 0
is_mining = False

is_day = True
cycle_timer = time.time()

font = pygame.font.SysFont("Arial", 18, bold=True)
font_big = pygame.font.SysFont("Arial", 36, bold=True)

# Логіка вибору випадкового фону при запуску
game_state = "MENU"
chosen_menu_bg = random.choice(menu_images) if menu_images else None

# ============ ГОЛОВНИЙ ЦИКЛ ============
while True:
    dt = clock.tick(60)
    current_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # --- ОБРОБКА ПОДІЙ МЕНЮ ---
        if game_state == "MENU":
            # Якщо натиснути будь-яку кнопку або клікнути мишкою - гра починається
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                game_state = "GAME"
        
        # --- ОБРОБКА ПОДІЙ ГРИ ---
        elif game_state == "GAME":
            # Скролл мишкою для вибору слота
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0: selected_slot = (selected_slot - 1) % INV_W
                elif event.y < 0: selected_slot = (selected_slot + 1) % INV_W

            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_8:
                    selected_slot = event.key - pygame.K_1
                if event.key == pygame.K_c:
                    show_craft_menu = not show_craft_menu
            
            # Логіка крафту
            if event.type == pygame.MOUSEBUTTONDOWN and show_craft_menu and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                menu_x = W - 220
                for i, (res_name, recipe) in enumerate(RECIPES.items()):
                    btn_rect = pygame.Rect(menu_x, 50 + i * 45, 200, 40)
                    if btn_rect.collidepoint(mx, my):
                        can_craft = True
                        for mat, amt in recipe["need"].items():
                            if not has_item(mat, amt): can_craft = False
                        if can_craft:
                            for mat, amt in recipe["need"].items():
                                remove_from_inventory(mat, amt)
                            add_to_inventory(res_name, recipe["give"])

            # Кліки миші в грі
            if event.type == pygame.MOUSEBUTTONDOWN and not show_craft_menu:
                mx, my = pygame.mouse.get_pos()
                
                # Перевірка кліку по інвентарю
                inv_clicked = False
                inv_start_x = W // 2 - (INV_W * 40) // 2
                if H - 50 <= my <= H - 10:
                    for i in range(INV_W):
                        x = inv_start_x + i * 45
                        if x <= mx <= x + 40:
                            selected_slot = i
                            inv_clicked = True
                            break
                
                # Якщо клікнули не по інвентарю - копаємо або ставимо блок
                if not inv_clicked:
                    if event.button == 1: # ЛКМ - копати
                        is_mining = True
                        mining_time = 0
                    if event.button == 3: # ПКМ - ставити
                        # Перетворення координат в int, щоб не було помилки з float
                        tx = int((mx + cam_x) // TILE)
                        ty = int((my + cam_y) // TILE)
                        
                        if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                            item = inventory[selected_slot]
                            if item:
                                if item["name"] in assets and "pickaxe" not in item["name"] and "sword" not in item["name"] and "axe" not in item["name"]:
                                     block_rect = pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)
                                     if not player.colliderect(block_rect) and world[ty][tx] is None:
                                         world[ty][tx] = item["name"]
                                         remove_from_inventory(item["name"], 1)
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: is_mining = False

    # --- МАЛЮВАННЯ МЕНЮ ---
    if game_state == "MENU":
        play_music("menu") # Грає 06. Title Screen.mp3
        if chosen_menu_bg:
            screen.blit(chosen_menu_bg, (0, 0))
        else:
            screen.fill((50, 50, 100))
        
        # Тексту немає, тільки фон
        
        pygame.display.flip()
        continue

    # --- ЛОГІКА ГРИ (Музика та фізика) ---
    player_grid_y = player.centery // TILE
    if player_grid_y > 45:
        play_music("cave") # Грає 04. Underground.mp3
    else:
        play_music("day")  # Грає 01. Overworld Day.mp3

    if is_day and current_time - cycle_timer > DAY_TIME:
        is_day = False; cycle_timer = current_time
    elif not is_day and current_time - cycle_timer > NIGHT_TIME:
        is_day = True; cycle_timer = current_time

    screen.fill((135, 206, 235) if is_day else (20, 20, 40))

    if current_time - last_hunger_update > 5:
        hunger = max(0, hunger - 1)
        last_hunger_update = current_time
        if hunger == 0: hp = max(0, hp - 1)

    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_a]: dx = -speed
    if keys[pygame.K_d]: dx = speed
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = jump_power; on_ground = False

    # Фізика і колізії гравця
    player.x += dx
    for y in range(player.top//TILE - 1, player.bottom//TILE + 2):
        for x in range(player.left//TILE - 1, player.right//TILE + 2):
            if 0 <= x < WORLD_W and 0 <= y < WORLD_H and world[y][x]:
                block_rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                if player.colliderect(block_rect):
                    if dx > 0: player.right = block_rect.left
                    if dx < 0: player.left = block_rect.right

    vel_y += GRAVITY
    player.y += vel_y
    on_ground = False
    for y in range(player.top//TILE - 1, player.bottom//TILE + 2):
        for x in range(player.left//TILE - 1, player.right//TILE + 2):
            if 0 <= x < WORLD_W and 0 <= y < WORLD_H and world[y][x]:
                block_rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                if player.colliderect(block_rect):
                    if vel_y > 0: player.bottom = block_rect.top; vel_y = 0; on_ground = True
                    elif vel_y < 0: player.top = block_rect.bottom; vel_y = 0

    # Процес майнінгу
    mx, my = pygame.mouse.get_pos()
    
    # Використовуємо int(), щоб уникнути помилок з координатами
    target_tx = int((mx + cam_x) // TILE)
    target_ty = int((my + cam_y) // TILE)
    
    if is_mining:
        if 0 <= target_tx < WORLD_W and 0 <= target_ty < WORLD_H:
            block_name = world[target_ty][target_tx]
            if block_name:
                block_info = BLOCK_DATA.get(block_name, {"hard": 20, "tool": "none", "hand_break": True})
                hand_item = inventory[selected_slot]
                tool_mult = 1
                has_correct_tool = False
                
                if hand_item:
                    tool_data = TOOLS_INFO.get(hand_item["name"])
                    if tool_data and tool_data[0] == block_info["tool"]:
                        tool_mult = tool_data[1]
                        has_correct_tool = True
                
                if block_info["hand_break"] or has_correct_tool:
                    speed_factor = tool_mult if has_correct_tool else 0.3
                    mining_time += 1 * speed_factor
                    
                    if mining_time >= block_info["hard"]:
                        world[target_ty][target_tx] = None
                        add_to_inventory(block_name, 1)
                        mining_time = 0
                else:
                    mining_time = 0

    # Рух камери
    target_cam_x = player.centerx - W // 2
    target_cam_y = player.centery - H // 2
    cam_x += (target_cam_x - cam_x) * 0.1
    cam_y += (target_cam_y - cam_y) * 0.1
    cam_x = max(0, min(cam_x, WORLD_W * TILE - W))
    cam_y = max(0, min(cam_y, WORLD_H * TILE - H))

    # --- МАЛЮВАННЯ ГРИ ---
    start_col = int(cam_x // TILE)
    end_col = int((cam_x + W) // TILE) + 1
    start_row = int(cam_y // TILE)
    end_row = int((cam_y + H) // TILE) + 1

    for y in range(start_row, end_row):
        for x in range(start_col, end_col):
            if 0 <= x < WORLD_W and 0 <= y < WORLD_H:
                if world[y][x]:
                    rect = pygame.Rect(x * TILE - cam_x, y * TILE - cam_y, TILE, TILE)
                    if world[y][x] in assets:
                        screen.blit(assets[world[y][x]], rect)
                    else:
                        pygame.draw.rect(screen, (255, 0, 255), rect)
                    
                    if is_mining and x == target_tx and y == target_ty:
                         break_progress = min(1, mining_time / 50)
                         pygame.draw.rect(screen, (0,0,0), rect, int(break_progress * 16))

    # Малювання гравця
    if "player" in assets:
        screen.blit(assets["player"], (player.x - cam_x, player.y - cam_y))
    else:
        pygame.draw.rect(screen, (200, 0, 0), (player.x - cam_x, player.y - cam_y, player.w, player.h))

    # Інвентар
    inv_start_x = W // 2 - (INV_W * 40) // 2
    for i in range(INV_W):
        x = inv_start_x + i * 45
        y = H - 50
        col = (200, 200, 200) if i == selected_slot else (100, 100, 100)
        pygame.draw.rect(screen, col, (x, y, 40, 40))
        pygame.draw.rect(screen, (0,0,0), (x, y, 40, 40), 2)
        
        item = inventory[i]
        if item:
            if item["name"] in assets:
                icon = pygame.transform.scale(assets[item["name"]], (30, 30))
                screen.blit(icon, (x+5, y+5))
            else:
                pygame.draw.circle(screen, (255, 0, 0), (x+20, y+20), 10)
            
            if item["count"] > 1:
                cnt_text = font.render(str(item["count"]), True, (255, 255, 255))
                screen.blit(cnt_text, (x+22, y+22))

    # Статистика (HP та Їжа)
    pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 25))
    pygame.draw.rect(screen, (200, 40, 40), (12, 12, 196 * (hp / max_hp), 21))
    screen.blit(font.render(f"HP: {int(hp)}", True, (255, 255, 255)), (20, 14))
    
    pygame.draw.rect(screen, (50, 50, 50), (10, 40, 200, 25))
    pygame.draw.rect(screen, (200, 180, 40), (12, 42, 196 * (hunger / 100), 21))
    screen.blit(font.render(f"Food: {int(hunger)}", True, (0, 0, 0)), (20, 44))

    # Крафт меню
    if show_craft_menu:
        menu_x = W - 220
        pygame.draw.rect(screen, (40, 40, 40), (menu_x, 50, 200, 300))
        pygame.draw.rect(screen, (255, 255, 255), (menu_x, 50, 200, 300), 2)
        screen.blit(font.render("Crafting", True, (255, 255, 255)), (menu_x+50, 20))
        
        for i, (res_name, recipe) in enumerate(RECIPES.items()):
            btn_rect = pygame.Rect(menu_x, 50 + i * 45, 200, 40)
            can_craft = True
            for mat, amt in recipe["need"].items():
                if not has_item(mat, amt): can_craft = False
            
            text_col = (100, 255, 100) if can_craft else (150, 150, 150)
            
            if res_name in assets:
                icon = pygame.transform.scale(assets[res_name], (30, 30))
                screen.blit(icon, (menu_x+5, 50 + i * 45 + 5))
            
            screen.blit(font.render(res_name, True, text_col), (menu_x + 40, 50 + i * 45 + 10))

    pygame.display.flip()
