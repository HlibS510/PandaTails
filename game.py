from pygame import *
from random import randint
import pygame
import os
import json


pygame.init()

leveldatafile = open('levelsdata')
leveldata = json.load(leveldatafile)

titles = leveldata["level1"]

leveldatafile.close()

os.environ['SDL_VIDEO_CENTERED'] = '1'
info = pygame.display.Info()
win_width, win_height = info.current_w, info.current_h

level_width, level_height = 7168, 4096
window = display.set_mode((win_width, win_height), FULLSCREEN)



healthfullwidth = 130

coins = 0
background = transform.scale(image.load("level1.jpg"), (level_width, level_height))


sprite_sheet_player = pygame.image.load("characters/player/idle.png").convert_alpha()
sprite_sheet_enemy = pygame.image.load("characters/enemy/idle.png").convert_alpha()
frames_player = []
frames_enemy = []
def pr_anim(spritesheet, frames_array, width, height, frames_count):
    frame_width = width
    frame_height = height
    num_frames = frames_count
    for i in range(num_frames):
        frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        frames_array.append(frame)

pr_anim(sprite_sheet_player, frames_player, 400, 186, 5)
pr_anim(sprite_sheet_enemy, frames_enemy, 112, 98, 4)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, custom_rect = False):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0
        self.animation_speed = 100  # мс на кадр

        #прибираємо зайву пустоту
        if custom_rect:
            self.rect.width = 210
            self.rect.height = 160
        self.rect.x = x
        self.rect.y = y
        self.local_x = x  # Локальні координати відносно рівня
        self.local_y = y


    def anim(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def render(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


    def reset(self, camera_x, camera_y, isrender = True):
        # Відображаємо спрайт з урахуванням позиції камери
        self.rect.x = self.local_x - camera_x
        self.rect.y = self.local_y - camera_y
        if isrender:
            self.render()

    def move(self, camera_x, camera_y):
        keys = key.get_pressed()

        old_x = self.local_x
        old_y = self.local_y

        speed = 4
        if key.get_pressed():
            if keys[K_a] and self.local_x > 5:
                self.local_x -= speed

            if keys[K_d] and self.local_x < level_width - self.rect.width:
                self.local_x += speed

            if keys[K_w] and self.local_y > 5:
                self.local_y -= speed

            if keys[K_s] and self.local_y < level_height - self.rect.height:
                self.local_y += speed
        else:
            player.image.anim()

        self.reset(camera_x, camera_y)

        wascollide = False
        if sprite.spritecollide(player.image, barier.borders, False):
            wascollide = True

        if wascollide:
            self.local_x = old_x
            self.local_y = old_y


class GameSprite(sprite.Sprite):
    def __init__(self,img, x, y , size_x, size_y):
        super().__init__()
        self.image = transform.scale(image.load(img),(size_x,size_y))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.local_x = x  # Локальні координати відносно рівня
        self.local_y = y

    def render(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def reset(self, camera_x, camera_y, isrender = True):
        # Відображаємо спрайт з урахуванням позиції камери
        self.rect.x = self.local_x - camera_x
        self.rect.y = self.local_y - camera_y
        if isrender:
            self.render()

class Collision():
    def __init__(self, pos_x, pos_y):
        self.width = 450
        self.height = 260
        self.curent_object = 0
        self.curent_line = 0
        self.borders = sprite.Group()

    def generate_borders(self):
        self.row = 0
        self.column = 0
        for tile in titles:
            if tile == 61:
                self.borders.add(GameSprite("live_indicator.png", self.column * 64, self.row * 64, 64, 64))
            self.column += 1
            if self.column == self.width:
                self.row += 1
                self.column = 0

    def update(self):
        for gsprite in self.borders:
            gsprite.reset(camera_x, camera_y, False)

class Player():
    def __init__(self, pos_x, pos_y, lives):
        self.maxLives = lives
        self.lives = lives
        self.image = AnimatedSprite(pos_x, pos_y, frames_player, True)
        self.healthbar = HealthBar("live_indicator.png", self.image.rect.x - 30, self.image.rect.y - 50, healthfullwidth, 40)
        self.healthbarframe = GameSprite("live_indicator_border.png", self.image.rect.x - 40, self.image.rect.y - 57, 150, 50)

    def player_damage(self):
        if self.lives != 0:
            self.lives -= 1
            self.healthbar.resize(healthfullwidth * (self.lives / self.maxLives))

    def update(self, camera_x, camera_y):
        self.image.anim(dclock)
        self.image.move(camera_x, camera_y)

class NPC():
    def __init__(self, pos_x, pos_y, text):
        self.text = text
        self.image = GameSprite("enemy_1.png", pos_x, pos_y, 70, 70, text)

    def update(self, camera_x, camera_y):
        self.image.reset()

    def dialog(self, pos_x, pos_y, text):
        font.init()
        self.menu_font = font.Font(None, 60)
        self.text_1 = self.menu_font.render("привіт", True, (255, 255, 255))
        self.image = GameSprite("enemy_1.png", pos_x, pos_y, 1500, 1500, text)
        if self.text == 1:
            self.text_1.render(100, 200)

class Enemy():
    def __init__(self, pos_x, pos_y, lives):
        self.maxLives = lives
        self.lives = lives
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.direction_atack = 0
        self.sprite_alive = True
        self.colected_loot = False
        self.image = AnimatedSprite(pos_x, pos_y, frames_enemy)
        self.imagecoin = GameSprite("npc.png", pos_x, pos_y,70,70)
        self.healthbar = HealthBar("live_indicator.png", self.image.rect.x - 30, self.image.rect.y - 50, healthfullwidth, 40)
        self.healthbarframe = GameSprite("live_indicator_border.png", self.image.rect.x - 40, self.image.rect.y - 57, 150, 50)



    def update(self, camera_x, camera_y):
        if self.lives != 0:
            self.healthbar.reset(camera_x, camera_y)
            self.healthbarframe.reset(camera_x, camera_y)
            self.image.reset(camera_x, camera_y)
            self.image.anim(dclock)

            print(self.lives)
        if self.lives == 0:
            self.imagecoin = GameSprite("npc.png", self.pos_x, self.pos_y, 70, 70)
            self.image = GameSprite("enemy_1.png", level_width * 1000, level_height * 1000, 70, 70)
            self.healthbar = HealthBar("live_indicator.png", level_width * 1000, level_height * 1000,healthfullwidth, 40)
            self.healthbarframe = GameSprite("live_indicator_border.png", level_width * 1000, level_height * 1000, 150, 50)
            self.healthbar.reset(camera_x, camera_y)
            self.healthbarframe.reset(camera_x, camera_y)
            self.image.reset(camera_x, camera_y)
            if self.colected_loot == False:
                self.imagecoin.reset(camera_x, camera_y)
            if sprite.collide_rect(player.image, self.imagecoin) and self.colected_loot == False:
                self.colected_loot = True
                global coins
                coins += 1

    def damage(self):
        if self.lives > 0:
            self.lives -= 1
            self.healthbar.resize(healthfullwidth * (self.lives / self.maxLives))

class HealthBar(GameSprite):

    def resize(self, width):
        self.image = transform.scale(self.image, (width, self.image.get_rect().height))

class Buttons(GameSprite):
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    def show(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


background = transform.scale(image.load("bg_menu.png") ,(win_width, win_height))
menu_button = Buttons("menu_button.png", 25, 25, 65, 65)
new_game_button = Buttons("new_game_button.png", 85, win_height * 0.3, 600, 40)
countiniue_button = Buttons("contin_button.png", 85, win_height * 0.4, 600, 40)
# information_button = Buttons("information_button.png", 85, win_height * 0.5, 600, 40, 0)
settings_button = Buttons("settings_button.png", 85, win_height * 0.5, 600, 40)
exit_button = Buttons("exit_button.png", 85, win_height * 0.9, 600, 40)

next_dialog_button = Buttons("next_text_button.png", win_width * 0.9, win_height * 0.9, 50, 50)
dialog_menu = GameSprite("dialog_menu_2.png", 0, win_height * 0.45, win_width, win_height * 0.6)

slot_1 = GameSprite("slot_1.png", win_width * 0.05, win_height * 0.8, win_width * 0.07, win_width * 0.07)

healthbar = GameSprite("live_indicator.png", win_width * 0.81, win_height * 0.115, 172, 24)

#next_map_line = GameSprite("dialog_menu.png", level_width * 0.13, win_height * 0.6, 5, win_height * 0.2)

barier = Collision(0, 0)

game_started = False
menu = True
run = True
game = False
dialog = 0
atack_rest = False
counter_enemy_atack = 0
atack_rest_timer = 0
poisons = 0
lives = 5
level = 1
first_dialog_ended = 0
died_bg_counter = 0
poison_counter = 0

font.init()
dialog_font = font.Font(None, 80)
dialog_1 = dialog_font.render("Привіт, дякую що урятував мене ось", True,(255,255,255))
dialog_2 = dialog_font.render("подарунок від мене", True,(255,255,255))
# dialog_1 = dialog_font.render("Привіт", True,(255,255,255))
menu_font = font.Font(None, 60)
new_game_text = menu_font.render("Нова Гра", True,(255,255,255))
countiniue_text = menu_font.render("Продовжити", True,(150,150,150))
information_text = menu_font.render("Інформація", True,(255,255,255))
settings_text = menu_font.render("Налаштування", True,(255,255,255))
exit_text = menu_font.render("Вийти", True,(255,255,255))
font2 = font.Font(None, 20)
press_e = font2.render("Натисни Е щоб заатакувати", True,(255,255,255))
hp_text = menu_font.render("HP", True,(255,255,255))

num_front = font.Font(None, 90)
number_slot_1 = num_front.render(str(poisons), True,(255,255,255))


# Камера
camera_x, camera_y = 0, 0
camera_threshold_x = win_width * 0.5  # 80% ширини екрана
camera_threshold_y = win_height * 0.5  # 80% висоти екрана

clock = time.Clock()


player = Player(350, 370, 10)
enemy_1 = Enemy(800, 300, 1)
enemy_2 = Enemy(1000, 300, 2)
enemy_3 = Enemy(800, 300, 1)
enemy_4 = Enemy(1000, 300, 2)
enemy_5 = Enemy(800, 300, 1)
enemy_6 = Enemy(1000, 300, 2)
enemy_7 = Enemy(800, 300, 1)
enemy_8 = Enemy(1000, 300, 2)
enemy_9 = Enemy(800, 300, 1)
enemy_10 = Enemy(1000, 300, 2)
enemy_11 = Enemy(800, 300, 1)
enemy_12 = Enemy(1000, 300, 2)
enemy_13 = Enemy(800, 300, 1)
enemy_14 = Enemy(1000, 300, 2)
enemy_15 = Enemy(800, 300, 1)
enemy_16 = Enemy(1000, 300, 2)
enemy_17 = Enemy(800, 300, 1)
enemy_18 = Enemy(1000, 300, 2)
enemy_19 = Enemy(800, 300, 1)
enemy_20 = Enemy(1000, 300, 2)
NPC = GameSprite("npc.png", 2200, 2320, 200, 200)

while run:

    dclock = clock.tick(60)

    for e in event.get():
        if e.type == QUIT:
            run = False

# Оновлення позиції камери
    if menu:
        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if new_game_button.is_clicked(pos):
                barier.generate_borders()
                menu = False
                game = True
                game_started = True
                dialog = 0
                atack_rest = False
                counter_enemy_atack = 0
                atack_rest_timer = 0
                poisons = 0
                lives = 5
                first_dialog_ended = 0
                died_bg_counter = 0
                poison_counter = 0
                background = transform.scale(image.load("level1.jpg"), (level_width, level_height))
                player = Player(400, 370, 10)
                enemy_1 = Enemy(800, 300, 1,)
                enemy_2 = Enemy(1000, 300, 2)
                enemy_3 = Enemy(4500, 1020, 4)
                enemy_4 = Enemy(5960, 930, 4)
                enemy_5 = Enemy(3600, 2210, 4)
                enemy_6 = Enemy(4260, 2810, 4)
                NPC = GameSprite("npc.png", 2200, 2320, 200, 200)

            if game_started == True:
                countiniue_text = menu_font.render("Продовжити", True, (255, 255, 255))
            if countiniue_button.is_clicked(pos) and game_started == True:
                menu = False
                game = True
                background = transform.scale(image.load("bg.png"), (level_width, level_height))
            if settings_button.is_clicked(pos):
                print("set")
            if exit_button.is_clicked(pos):
                run = False

        window.blit(background, (0, 0))
        window.blit(new_game_text, (85, win_height * 0.3))
        window.blit(countiniue_text, (85, win_height * 0.4))
        # window.blit(information_text, (85, win_height * 0.5))
        window.blit(settings_text, (85, win_height * 0.5))
        window.blit(exit_text, (85, win_height * 0.9))

    if game:
        print(coins)
        keys = key.get_pressed()
        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if menu_button.is_clicked(pos):
                game = False
                menu = True
        #камера
        player_screen_x = player.image.local_x - camera_x
        player_screen_y = player.image.local_y - camera_y

        # Рух камери по горизонталі
        if player_screen_x > camera_threshold_x:
            camera_x = player.image.local_x - camera_threshold_x
        elif player_screen_x < win_width - camera_threshold_x:
            camera_x = player.image.local_x - (win_width - camera_threshold_x)

        # Рух камери по вертикалі
        if player_screen_y > camera_threshold_y:
            camera_y = player.image.local_y - camera_threshold_y
        elif player_screen_y < win_height - camera_threshold_y:
            camera_y = player.image.local_y - (win_height - camera_threshold_y)

        # Обмеження камери межами рівня
        camera_x = max(0, min(camera_x, level_width - win_width))
        camera_y = max(0, min(camera_y, level_height - win_height))


        window.blit(background, (-camera_x, -camera_y))
        window.blit(hp_text, (win_width * 0.77, win_height * 0.115))
        #next_map_line.reset(camera_x, camera_y)
        healthbar.render()

        slot_1.render()
        if game_started == True:
            NPC = GameSprite("npc.png", 2200, 2320, 200, 200)
            enemy_1.update(camera_x, camera_y)
            enemy_2.update(camera_x, camera_y)
            enemy_3.update(camera_x, camera_y)
            enemy_4.update(camera_x, camera_y)
            enemy_5.update(camera_x, camera_y)
            enemy_6.update(camera_x, camera_y)
            NPC.reset(camera_x, camera_y)
            player.update(camera_x, camera_y)
            barier.update()
            menu_button.show()
        # атака монстра
        if sprite.collide_rect(player.image, enemy_2.image) or sprite.collide_rect(player.image, enemy_1.image)  or sprite.collide_rect(player.image, enemy_3.image)  or sprite.collide_rect(player.image, enemy_4.image) or sprite.collide_rect(player.image, enemy_5.image) or sprite.collide_rect(player.image, enemy_6.image):
            counter_enemy_atack += 1
            if counter_enemy_atack >= 60 and lives != 0:
                lives -= 1
                counter_enemy_atack = 0
        else:
            counter_enemy_atack = 0

        if atack_rest == True:
            atack_rest_timer += 1
            if atack_rest_timer >= 50:
                atack_rest = False
                atack_rest_timer = 0
        # зілля
        if poisons > 0:
            number_slot_1 = num_front.render(str(poisons), True, (255, 255, 255))
            window.blit(number_slot_1, (slot_1.rect.x * 2, slot_1.rect.y))
            slot_1 = GameSprite("slot_1_with_poison.png", win_width * 0.05, win_height * 0.8, win_width * 0.07,
                                win_width * 0.07)
        elif poisons == 0:
            slot_1 = GameSprite("slot_1.png", win_width * 0.05, win_height * 0.8, win_width * 0.07, win_width * 0.07)
        if keys[K_q] and poisons > 0 and lives < 5:
            if poison_counter < 10:
                poison_counter += 1
            if poison_counter == 10 or poison_counter > 10:
                lives += 1
                poisons -= 1
                poison_counter = 0
        # атака
        if keys[K_e] and atack_rest == False:
            if sprite.collide_rect(player.image, NPC):
                dialog = 1
            if sprite.collide_rect(player.image, enemy_1.image):
                enemy_1.damage()
                atack_rest = True
            if sprite.collide_rect(player.image, enemy_2.image):
                enemy_2.damage()
                atack_rest = True

        # 2 рівень
        # if sprite.collide_rect(player.image, next_map_line):
        #     enemy_1 = Enemy(1800, 1000, 1)
        #     enemy_2 = Enemy(1800, 1000, 2)
        #     background = transform.scale(image.load("level2.jpg"), (level_width, level_height))
        # діалог
        if dialog == 1:
            game_started = False
            NPC.render()
            dialog_menu.render()
            window.blit(dialog_1, (win_width * 0.2, win_height * 0.6))
            window.blit(dialog_2, (win_width * 0.4, win_height * 0.7))
            NPC = GameSprite("npc.png", win_width * 0.4, win_height * 0.2, 550, 380)
            next_dialog_button.show()
            pos = pygame.mouse.get_pos()
            if next_dialog_button.is_clicked(pos):
                game_started = True
                if first_dialog_ended == False:
                    first_dialog_ended = True
                    poisons += 5
                first_dialog_ended = 1
                dialog = 0

        # перевірка на смерть
        if lives == 0:
            if died_bg_counter <= 50:
                game_started = False
                died_bg_counter += 1
                background = transform.scale(image.load("died_bg.png"), (level_width, level_height))
            if died_bg_counter >= 50:
                background = transform.scale(image.load("bg_menu.png"), (win_width, win_height))
                lives = 5
                game = False
                menu = True



    healthbar = GameSprite("live_indicator.png", win_width * 0.81, win_height * 0.115, lives * 34.4, 24)
    display.update()