import pygame, sys, random, time

pygame.init()

# ============ WINDOW ============
W,H=960,540
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("Terraria Clone Advanced")
clock=pygame.time.Clock()

# ============ CONSTANTS ============
TILE=32
WORLD_W=400  # більший світ
WORLD_H=80
GRAVITY=1

DAY_TIME=180
NIGHT_TIME=180

# ============ COLORS ============
SKY_DAY=(135,206,235)
SKY_NIGHT=(30,30,60)

COLORS={
"grass":(80,200,80),
"dirt":(120,80,40),
"stone":(120,120,120),
"coal":(30,30,30),
"iron":(170,170,190),
"gold":(220,200,80),
"diamond":(80,220,255),
"wood":(140,100,60),
"leaves":(60,170,60),
"snow":(245,245,245),
"snow_tree":(200,200,200),
"player":(220,60,60),
"mob":(0,200,0),
"pig":(255,192,203),
"cow":(150,75,0)
}

# ============ BLOCK DATA ============
BLOCKS={
"grass":("shovel",20),
"dirt":("shovel",20),
"stone":("pickaxe",45),
"coal":("pickaxe",50),
"iron":("pickaxe",60),
"gold":("pickaxe",70),
"diamond":("pickaxe",90),
"wood":("axe",25),
"leaves":("axe",10),
"snow":("shovel",20),
"snow_tree":("axe",25)
}

# ============ WORLD GEN ============
world=[[None for _ in range(WORLD_W)] for _ in range(WORLD_H)]
surface=[]
h=32
for x in range(WORLD_W):
    h+=random.choice([-1,0,1])
    h=max(26,min(40,h))
    # зимний біом рідко
    is_snow=random.random()<0.05
    surface.append(h)
    for y in range(WORLD_H):
        if y==h:
            world[y][x]="snow" if is_snow else "grass"
        elif y>h:
            world[y][x]="dirt" if y<h+4 else "stone"

# Повний камінь внизу 10 рядів
for y in range(WORLD_H-10,WORLD_H):
    for x in range(WORLD_W): world[y][x]="stone"

# caves
for _ in range(250):
    cx=random.randint(0,WORLD_W-1)
    cy=random.randint(40,WORLD_H-15)
    r=random.randint(3,7)
    for y in range(cy-r,cy+r):
        for x in range(cx-r,cx+r):
            if 0<=x<WORLD_W and 0<=y<WORLD_H and random.random()>0.35: world[y][x]=None

# ores
def ore(name,chance,miny):
    for y in range(miny,WORLD_H):
        for x in range(WORLD_W):
            if world[y][x]=="stone" and random.random()<chance: world[y][x]=name
ore("coal",0.02,38)
ore("iron",0.015,42)
ore("gold",0.01,48)
ore("diamond",0.005,55)

# trees
for x in range(6,WORLD_W-6,9):
    g=surface[x]
    th=random.randint(4,6)
    # snow tree rare
    is_snow=random.random()<0.1
    for i in range(th): world[g-i][x]="snow_tree" if is_snow else "wood"
    for lx in range(x-2,x+3):
        for ly in range(g-th-2,g-th+1):
            if 0<=lx<WORLD_W and 0<=ly<WORLD_H:
                world[ly][lx]="snow_tree" if is_snow else "leaves"

# ============ PLAYER ============
player=pygame.Rect(100,100,26,42)
vel_y=0
speed=5
jump=-15
on_ground=False
hp=100
hunger=100
last_hunger=time.time()

# ============ CAMERA ============
cam_x=cam_y=0

# ============ INVENTORY ============
INV_W,INV_H=5,3
inventory=[[None for _ in range(INV_W)] for _ in range(INV_H)]
selected_slot=0
inventory_tools={"shovel":True,"pickaxe":False,"axe":False,"sword":False}
show_inv=False

def add_item(item):
    for y in range(INV_H):
        for x in range(INV_W):
            slot=inventory[y][x]
            if slot and slot[0]==item and slot[1]<99: slot[1]+=1; return True
    for y in range(INV_H):
        for x in range(INV_W):
            if inventory[y][x] is None: inventory[y][x]=[item,1]; return True
    return False

def remove_item(item):
    for y in range(INV_H):
        for x in range(INV_W):
            slot=inventory[y][x]
            if slot and slot[0]==item:
                slot[1]-=1
                if slot[1]==0: inventory[y][x]=None
                return True
    return False

# spawn items
pickaxe_item=pygame.Rect(180,surface[6]*TILE-20,20,20)
sword_item=pygame.Rect(220,surface[6]*TILE-20,20,20)
axe_item=pygame.Rect(260,surface[6]*TILE-20,20,20)

# mobs and animals
mobs=[]
animals=[]
last_spawn=0

# spawn animals
for _ in range(8):
    animals.append({"type":"pig","rect":pygame.Rect(random.randint(0,WORLD_W-1)*TILE,surface[random.randint(0,WORLD_W-1)]*TILE-32,26,26),"hp":10})
for _ in range(5):
    animals.append({"type":"cow","rect":pygame.Rect(random.randint(0,WORLD_W-1)*TILE,surface[random.randint(0,WORLD_W-1)]*TILE-32,30,30),"hp":15})

# ============ DAY / NIGHT ============
is_day=True
cycle_start=time.time()

# ============ MUSIC ============
try:
    pygame.mixer.music.load("terraria_theme.mp3")  # добавь свій файл у папку
    pygame.mixer.music.play(-1)
except:
    print("Файл музики не знайдено, без музики")

# ============ FUNCTIONS ============
def blocks_near(rect):
    blocks=[]
    for y in range(rect.top//TILE-1,rect.bottom//TILE+2):
        for x in range(rect.left//TILE-1,rect.right//TILE+2):
            if 0<=x<WORLD_W and 0<=y<WORLD_H and world[y][x]:
                blocks.append(pygame.Rect(x*TILE,y*TILE,TILE,TILE))
    return blocks

def block_at_mouse():
    mx,my=pygame.mouse.get_pos()
    tx=(mx+cam_x)//TILE
    ty=(my+cam_y)//TILE
    if 0<=tx<WORLD_W and 0<=ty<WORLD_H: return tx,ty
    return None

# ============ MAIN LOOP ============
mining=False
mine_t=0
target=None

while True:
    clock.tick(60)
    now=time.time()

    # day/night
    if is_day and now-cycle_start>=DAY_TIME: is_day=False;cycle_start=now
    if not is_day and now-cycle_start>=NIGHT_TIME: is_day=True;cycle_start=now

    screen.fill(SKY_DAY if is_day else SKY_NIGHT)

    # hunger decay
    if now-last_hunger>5: hunger=max(0,hunger-1); last_hunger=now
    if hunger==0: hp=max(0,hp-1)

    for e in pygame.event.get():
        if e.type==pygame.QUIT: pygame.quit();sys.exit()
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_i: show_inv=not show_inv
            if e.key==pygame.K_e:
                if pickaxe_item and player.colliderect(pickaxe_item): inventory_tools["pickaxe"]=True; pickaxe_item=None
                if sword_item and player.colliderect(sword_item): inventory_tools["sword"]=True; sword_item=None
                if axe_item and player.colliderect(axe_item): inventory_tools["axe"]=True; axe_item=None
            if pygame.K_1<=e.key<=pygame.K_5: selected_slot=e.key-pygame.K_1
        if e.type==pygame.MOUSEBUTTONDOWN:
            target=block_at_mouse()
            if e.button==1: mining=True; mine_t=0
            if e.button==3:
                tx,ty=block_at_mouse()
                slot_item=None
                for y in range(INV_H):
                    for x in range(INV_W):
                        if x==selected_slot and inventory[y][x]: slot_item=inventory[y][x][0]; break
                    if slot_item: break
                if slot_item and world[ty][tx] is None:
                    world[ty][tx]=slot_item; remove_item(slot_item)
        if e.type==pygame.MOUSEBUTTONUP:
            if e.button==1: mining=False

    # movement X
    keys=pygame.key.get_pressed()
    dx=0
    if keys[pygame.K_a]: dx=-speed
    if keys[pygame.K_d]: dx=speed
    player.x+=dx
    for b in blocks_near(player):
        if player.colliderect(b):
            if dx>0: player.right=b.left
            if dx<0: player.left=b.right

    # movement Y
    if keys[pygame.K_SPACE] and on_ground: vel_y=jump
    vel_y+=GRAVITY
    player.y+=vel_y
    on_ground=False
    for b in blocks_near(player):
        if player.colliderect(b):
            if vel_y>0: player.bottom=b.top; vel_y=0; on_ground=True
            elif vel_y<0: player.top=b.bottom; vel_y=0

    # mining / chopping
    if mining and target:
        x,y=target
        b=world[y][x]
        if b:
            need,hard=BLOCKS[b]
            tool_ok=inventory_tools.get(need,False)
            if tool_ok:
                mine_t+=2
                if mine_t>=hard:
                    world[y][x]=None
                    add_item(b)
                    mining=False

    # mobs spawn
    if not is_day and now-last_spawn>3:
        last_spawn=now
        mx=random.randint(0,WORLD_W-1)*TILE
        my=surface[random.randint(0,WORLD_W-1)]*TILE-40
        mobs.append({"rect":pygame.Rect(mx,my,26,40),"spawn":now,"hp":20})

    # mobs AI + damage
    for m in mobs[:]:
        if m["rect"].x>player.x: m["rect"].x-=1
        else: m["rect"].x+=1
        if player.colliderect(m["rect"]): hp=max(0,hp-1)
        if is_day and now-m["spawn"]>5:
            if random.random()<0.5: add_item(random.choice(["dirt","coal","iron"]))
            mobs.remove(m)

    # animals AI
    for a in animals[:]:
        if random.random()<0.01: a["rect"].x+=random.choice([-1,1])*TILE//8
        for b in blocks_near(a["rect"]):
            if a["rect"].colliderect(b) and a["rect"].bottom>b.top: a["rect"].bottom=b.top
        # attack animals
        if pygame.mouse.get_pressed()[0] and inventory_tools["sword"]:
            mx,my=pygame.mouse.get_pos()
            rect=pygame.Rect(a["rect"].x-cam_x,a["rect"].y-cam_y,a["rect"].w,a["rect"].h)
            if rect.collidepoint(mx,my):
                a["hp"]-=10
                if a["hp"]<=0:
                    if a["type"]=="pig": add_item("dirt")  # замість м'яса можна зробити їжу
                    if a["type"]=="cow": add_item("iron")
                    animals.remove(a)

    # camera
    cam_x=max(0,min(player.centerx-W//2,WORLD_W*TILE-W))
    cam_y=max(0,min(player.centery-H//2,WORLD_H*TILE-H))

    # draw world
    for y in range(cam_y//TILE,cam_y//TILE+H//TILE+2):
        for x in range(cam_x//TILE,cam_x//TILE+W//TILE+2):
            if 0<=x<WORLD_W and 0<=y<WORLD_H and world[y][x]:
                pygame.draw.rect(screen,COLORS[world[y][x]],(x*TILE-cam_x,y*TILE-cam_y,TILE,TILE))

    # items
    for item in [pickaxe_item,sword_item,axe_item]:
        if item: pygame.draw.rect(screen,(200,200,255),(item.x-cam_x,item.y-cam_y,20,20))

    # mobs
    for m in mobs: pygame.draw.rect(screen,COLORS["mob"],(m["rect"].x-cam_x,m["rect"].y-cam_y,26,40))
    # animals
    for a in animals: pygame.draw.rect(screen,COLORS[a["type"]],(a["rect"].x-cam_x,a["rect"].y-cam_y,a["rect"].w,a["rect"].h))

    # player
    pygame.draw.rect(screen,COLORS["player"],(player.x-cam_x,player.y-cam_y,player.w,player.h))

    # HUD
    font=pygame.font.SysFont(None,22)
    pygame.draw.rect(screen,(0,0,0),(5,5,120,40))
    pygame.draw.rect(screen,(255,0,0),(10,10,hp,10))
    pygame.draw.rect(screen,(255,255,0),(10,25,hunger,10))
    screen.blit(font.render("HP",True,(255,255,255)),(50,7))
    screen.blit(font.render("Hunger",True,(255,255,255)),(50,22))

    # inventory UI
    if show_inv:
        pygame.draw.rect(screen,(0,0,0),(W//2-160,H//2-100,320,200))
        pygame.draw.rect(screen,(255,255,255),(W//2-160,H//2-100,320,200),2)
        for y in range(INV_H):
            for x in range(INV_W):
                sx=W//2-140+x*60; sy=H//2-80+y*60
                pygame.draw.rect(screen,(80,80,80),(sx,sy,50,50))
                pygame.draw.rect(screen,(255,255,255),(sx,sy,50,50),2)
                slot=inventory[y][x]
                if slot:
                    screen.blit(font.render(slot[0],True,(255,255,255)),(sx+3,sy+3))
                    screen.blit(font.render(str(slot[1]),True,(255,255,0)),(sx+3,sy+25))
                if x==selected_slot: pygame.draw.rect(screen,(255,255,0),(sx,sy,50,50),3)

    pygame.display.flip()
в 