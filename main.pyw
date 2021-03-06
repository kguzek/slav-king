from modules import setup
from modules import variables as v
settings = setup.init()

# Cheats - Change these :D
god_mode = False
infinite_ammo = False
money_count = settings["start_money"]


# SOUND EFFECT CODE                                                              
class Effect(object):
    v.pygame.mixer.music.load(v.audio_dir + "music.mp3")
    v.pygame.mixer.music.play(-1)

    # Gets the volume from settings and converts it into decimal instead of percentage
    v.pygame.mixer.music.set_volume(0 if settings["muted"] else settings["volume"] / 100)

    def __init__(self, name, channel="default", should_loop=False):
        if channel == "default":
            channel = v.pygame.mixer.find_channel(True)
        else:
            channel = v.pygame.mixer.Channel(1)
        self.timer = 0
        sound_object = v.pygame.mixer.Sound(f"{v.audio_dir}{name}.wav")
        if should_loop:
            channel.play(sound_object, -1)
        else:
            channel.play(sound_object)


# BULLET CODE                                                                     
class Projectile(object):
    def __init__(self, x, y, radius, colour, facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.facing = facing
        self.vel = 32 * facing
        
    def draw(self):
        v.pygame.draw.circle(v.win, self.colour, (self.x, self.y), self.radius)

 
# AMMO/MONEY DROP CODE                                                            
class LootDrop(object):
    def __init__(self, x, y, pickup_amount, loot_type):
        self.x = x
        self.y = y
        self.loot_type = loot_type
        self.pickup_amount = 3 * pickup_amount if loot_type == "money" else pickup_amount
        self.hitbox = [self.x + 8, self.y, 48, 65]
        self.animation_cycle = 0
        self.current_font = v.pygame.font.SysFont("comicsans", 19 + self.animation_cycle)
        self.text = self.current_font.render("+" + str(self.pickup_amount), True, (255, 255, 255))
        self.text_position = [self.hitbox[0] + self.hitbox[2] // 2 - self.text.get_width() // 2, self.hitbox[1] - 20]
        self.animation_direction = 1
        
    def draw(self):
        self.current_font = v.pygame.font.SysFont("comicsans", 19 + self.animation_cycle)
        if self.animation_cycle == 0 and self.animation_direction == -1: 
            self.animation_direction = 1
        elif self.animation_cycle == 5 and self.animation_direction == 1: 
            self.animation_direction = -1
        if not v.paused:
            self.animation_cycle += self.animation_direction

        v.win.blit(v.bullet_stack if self.loot_type == "ammo" else v.coin_stack, (self.x, self.y))
        text_to_render = f"+{'$' if self.loot_type == 'money' else ''}{self.pickup_amount}"
        self.text = self.current_font.render(text_to_render, True, (255, 255, 255))
        
        v.win.blit(self.text, self.text_position)
        self.hitbox = [self.x + 8, self.y, 48, 65]
        self.text_position = [self.hitbox[0] + self.hitbox[2] // 2 - self.text.get_width() // 2, self.hitbox[1] - 20]
        # Uncomment below to show dropped item hitboxes
        # v.pygame.draw.rect(v.win, (255, 0, 0), self.hitbox, 2)


# WEAPONS RACK CODE AND STATISTICS 
class Weapon(object):
    def __init__(self, x, y, name, cost, dmg, rof, full_auto):
        self.x = x
        self.y = y
        self.name = name
        self.img = v.pygame.image.load(v.image_dir + "gun_" + name + ".png")
        self.cost = cost
        self.dmg = dmg  # damage
        self.rof = rof  # rate of fire
        self.fullAuto = full_auto  # if fully automatic fire is permitted
        self.text = v.bold_font.render(name + " - $" + str(cost), 1, (255, 255, 255))
        self.affordable = money_count >= self.cost
        self.flash_sequence = -1
        self.outer_hitbox = [self.x, self.y, 256, 164]
        self.owned = False
        if self.name == "AK-47":
            self.hitbox = [self.x, self.y, 256, 144]
        elif self.name == "MP5":
            self.hitbox = [self.x + (256 - 192) // 2, self.y + (144 - 104) // 2, 192, 144]
        elif self.name == "Beretta":
            self.hitbox = [self.x + (256 - 101) // 2, self.y + (144 - 72) // 2, 101, 72]
        elif self.name == "Deagle":
            self.hitbox = [self.x + (256 - 128) // 2, self.y + (144 - 128) // 2, 128, 128]
        self.text_position = [self.x + 256 // 2 - self.text.get_width() // 2, self.y + 144 - 10]

    def draw(self):
        if v.selected_gun == self:
            self.text = v.bold_font.render(self.name + " - SELECTED", 1, (255, 255, 255))
        elif self.owned:
            self.text = v.bold_font.render(self.name + " - OWNED", 1, (255, 255, 255))
        else:
            self.text = v.bold_font.render(self.name + " - $" + str(self.cost), 1, (255, 255, 255))
        self.text_position = [self.x + 256 // 2 - self.text.get_width() // 2, self.y + 144 - 10]
        if self.flash_sequence >= 0:
            self.flash_sequence += 0.5
            if self.flash_sequence // 2 != self.flash_sequence / 2:
                v.pygame.draw.rect(v.win, (255, 96, 96), self.outer_hitbox)
                v.pygame.draw.rect(v.win, (255, 0, 0), self.outer_hitbox, 5)
        if self.flash_sequence >= 6:
            self.flash_sequence = -1
        if self.owned:
            v.pygame.draw.rect(v.win, (72, 240, 112), self.outer_hitbox)
        elif self.affordable:
            v.pygame.draw.rect(v.win, (0, 255, 0), self.outer_hitbox, 5)
        if self == v.selected_gun:
            v.pygame.draw.rect(v.win, (255, 255, 255), self.outer_hitbox, 5)
        v.win.blit(self.img, (self.hitbox[:2]))
        v.win.blit(self.text, self.text_position)
        # Uncomment below to show weapon sprite hitboxes in store
        # v.pygame.draw.rect(v.win, (255, 0, 0), self.hitbox, 1)

    def flash(self):  # For flash animation when can't afford weapon
        self.flash_sequence = 0


# SHOP ABILITY CODE 
class AbilityPurchasable(object):
    def __init__(self, x, y, name, cost):
        self.x = x
        self.y = y
        self.name = name
        self.img = v.pygame.image.load(v.image_dir + "icon_" + name + ".png")
        self.cost = cost
        self.text = v.bold_font.render(name + " - $" + str(cost), 1, (255, 255, 255))
        self.owned_text = v.bold_font.render("0", 1, (255, 255, 255))
        self.affordable = money_count >= self.cost
        self.flash_sequence = -1
        self.outer_hitbox = [self.x, self.y, 256, 164]
        if self.name == "mayonnaise":
            self.hitbox = [self.x + (256 - 75) // 2, self.y + (144 - 116) // 2, 75, 116]
            self.owned = 0
            self.img = v.pygame.transform.scale(self.img, (75, 116))
        elif self.name == "beer":
            self.hitbox = [self.x + (256 - 40) // 2, self.y + (144 - 124) // 2, 40, 124]
            self.owned = 0
            self.img = v.pygame.transform.scale(self.img, (40, 124))
        self.text_position = [self.x + 256 // 2 - self.text.get_width() // 2, self.y + 144 - 10]
        self.owned_text_position = [self.x + 16, self.y + 12]

    def draw(self):
        self.owned_text = v.bold_font.render(str(self.owned), 1, (255, 255, 255))
        self.owned_text_position = [self.x + 16, self.y + 12]
        if self.owned > 0:
            v.pygame.draw.rect(v.win, (72, 240, 112), self.outer_hitbox)
            v.pygame.draw.rect(v.win, (255, 255, 255), self.outer_hitbox, 5)
        elif self.affordable:
            v.pygame.draw.rect(v.win, (0, 255, 0), self.outer_hitbox, 5)
        if self.flash_sequence >= 0:
            self.flash_sequence += 0.5
            if self.flash_sequence // 2 != self.flash_sequence / 2:
                v.pygame.draw.rect(v.win, (255, 96, 96), self.outer_hitbox)
                v.pygame.draw.rect(v.win, (255, 0, 0), self.outer_hitbox, 5)
        if self.flash_sequence >= 6:
            self.flash_sequence = -1
        v.win.blit(self.img, (self.hitbox[:2]))
        v.win.blit(self.text, self.text_position)
        v.win.blit(self.owned_text, self.owned_text_position)
        # Uncomment below to show powerup sprite hitboxes in store
        # v.pygame.draw.rect(v.win, (255, 0, 0), self.hitbox, 1)

    def flash(self):  # For flash animation when can't afford powerup
        self.flash_sequence = 0


# SHOP AMMO CODE 
class AmmoPurchasable(object):
    def __init__(self, x, y, cost):
        self.x = x
        self.y = y
        self.img = v.pygame.image.load(v.image_dir + "icon_bullets.png")
        self.img = v.pygame.transform.scale(self.img, (96, 96))
        self.cost = cost
        self.text = v.bold_font.render("15 rounds - $" + str(cost), 1, (255, 255, 255))
        self.owned_text = v.bold_font.render(str(v.ammo_count), 1, (255, 255, 255))
        self.affordable = money_count >= self.cost
        self.flash_sequence = -1
        self.outer_hitbox = [self.x, self.y, 256, 164]
        self.hitbox = [self.x + (256 - 96) // 2, self.y + (144 - 96) // 2, 96, 96]
        self.text_position = [self.x + 256 // 2 - self.text.get_width() // 2, self.y + 144 - 10]
        self.owned_text_position = [self.x + 16, self.y + 12]

    def draw(self):
        self.owned_text = v.bold_font.render(str(v.ammo_count), 1, (255, 255, 255))
        self.owned_text_position = [self.x + 16, self.y + 12]
        if self.affordable:
            v.pygame.draw.rect(v.win, (0, 255, 0), self.outer_hitbox, 5)
        if self.flash_sequence >= 0:
            self.flash_sequence += 0.5
            if self.flash_sequence // 2 != self.flash_sequence / 2:
                v.pygame.draw.rect(v.win, (255, 96, 96), self.outer_hitbox)
                v.pygame.draw.rect(v.win, (255, 0, 0), self.outer_hitbox, 5)
        if self.flash_sequence >= 6:
            self.flash_sequence = -1
        v.win.blit(self.img, (self.hitbox[:2]))
        v.win.blit(self.text, self.text_position)
        v.win.blit(self.owned_text, self.owned_text_position)
        # Uncomment below to show powerup sprite hitboxes in store
        # v.pygame.draw.rect(v.win, (255, 0, 0), self.hitbox, 1)

    def flash(self):  # For flash animation when can't afford powerup
        self.flash_sequence = 0


# IN-GAME ABILITY CODE
class Ability(object):
    def __init__(self, x, y, name):
        self.text_x = x
        self.y = y
        self.name = name
        self.text = v.bold_font.render(name, 1, (255, 255, 255))
        self.owned_text = v.bold_font.render("0", 1, (255, 255, 255))
        self.owned = 0
        self.progress = 0
        self.x = x + self.text.get_width() // 2 - 37 // 2
        self.dimensions = [x, y, self.text.get_width(), 58 + self.text.get_height()]
        self.bar_dimensions = [self.text_x + self.text.get_width() - 11, self.y + 18, 10, 40]
        self.dummy_text = v.bold_font.render(str(self.owned)[0], 1, (0, 0, 0))
        self.bar_fill_dimensions = [self.bar_dimensions[0], self.bar_dimensions[1] + (self.progress - 40) // 5,
                                    self.bar_dimensions[2], self.bar_dimensions[3] - (self.progress - 40) // 5]

    def draw(self):
        if v.paused and v.pause_menu == "shop":
            return

        for powerup in purchasable_powerups:  # Calculating how many powerups the user has purchased
            if powerup.name.startswith(self.name):
                self.owned = powerup.owned
                break
        self.dummy_text = v.bold_font.render(str(self.owned)[0], 1, (0, 0, 0))

        if self.owned > 0 or self.progress > 0:
            self.text = v.bold_font.render(self.name, 1, (255, 255, 255))
            self.owned_text = v.bold_font.render(str(self.owned), 1, (255, 255, 255))
            v.win.blit(v.mayo_jar if self.name == "mayo" else v.beer_bottle, (self.x, self.y))
        else:
            self.text = v.bold_font.render(self.name, 1, (128, 128, 128))
            self.owned_text = v.bold_font.render("0", 1, (128, 128, 128))
            v.win.blit(v.mayo_jar_bw if self.name == "mayo" else v.beer_bottle_bw, (self.x, self.y))
        v.win.blit(self.text, (self.text_x, self.y + 58))
        v.win.blit(self.owned_text, (self.text_x + self.text.get_width() - self.dummy_text.get_width() + 5, self.y - 2))
        if self.progress > 0:
            # Uncomment below to show powerup sprite hitboxes in game
            # v.pygame.draw.rect(v.win, (0, 204, 255), self.bar_dimensions)
            dims = self.bar_dimensions
            if self.progress < dims[3]:
                self.bar_fill_dimensions = [dims[0], dims[1] + dims[3] - self.progress, dims[2], self.progress]
            else:
                self.bar_fill_dimensions = [dims[0], dims[1] + (self.progress - 40) // 5,
                                            dims[2], dims[3] - (self.progress - 40) // 5]
            v.pygame.draw.rect(v.win, (204, 204, 0), self.bar_fill_dimensions)

    def activate(self):
        if self.progress == 0:
            for powerup in purchasable_powerups:
                if powerup.name.startswith(self.name):
                    powerup.owned -= 1
                    break
        if self.progress < 240:
            self.progress += 1
            if self.name == "mayo":
                v.mayo_power = True
                slav.vel = 20
            elif self.name == "beer":
                v.beer_power = True
                slav.vel = 5
        else:
            self.progress = 0
            if self.name == "mayo":
                v.mayo_power = False
            elif self.name == "beer":
                v.beer_power = False
            slav.vel = 10


# BUTTON CODE
class Button(object):
    def __init__(self, text, function, selected=False):
        self.text_message = text
        self.text = v.standard_font.render(text, 1, (0, 0, 0))
        self.function = function
        self.dimensions = None
        self.selected = selected

    def initialise_dimensions(self):
        sibling_buttons = []
        for pause_menu in buttons.keys():
            if self in buttons[pause_menu]:
                sibling_buttons = buttons[pause_menu]
                break
        if len(sibling_buttons) == 2:
            # The index of the button is either 1 or 0, which means its x_centre is the window width * either 1/4 or 3/4
            x_centre = v.win_width * (1 + 2 * sibling_buttons.index(self)) // 4
            # The x position is the x centre minus half of the button's width
            # The y position is at the halfway point of the window's height
            # The width of the button is one third of the window's width
            # The height of the button is 50px
            self.dimensions = [x_centre - v.win_width // 6, v.win_height * 1.75 // 3, v.win_width // 3, 50]
        else:
            # The index of the button is 0-2, which means its y_centre is the window height * either 2/6, 3/6 or 4/6
            y_centre = v.win_height * (2 + sibling_buttons.index(self)) // 6
            # The x position is at the halfway point of the window's width
            # The y position is either at 1/3, 1/2 or 2/3 of the window's height
            # The width of the button is one half of the window's width
            # The height of the button is 50px
            self.dimensions = [v.win_width // 2 - v.win_width // 4, y_centre, v.win_width // 2, 50]

    def draw(self, bg_shade=None):
        if self.dimensions is None:
            self.initialise_dimensions()
        if bg_shade is None:
            bg_shade = 64 if self.selected else 128
        v.pygame.draw.rect(v.win, [bg_shade] * 3, self.dimensions)
        # Renders button outline graphic
        v.pygame.draw.rect(v.win, (0, 0, 0), self.dimensions, 2)
        text_position = [self.dimensions[0] + self.dimensions[2] // 2 - self.text.get_width() // 2,
                         self.dimensions[1] + self.dimensions[3] // 2 - self.text.get_height() // 2]
        v.win.blit(self.text, text_position)

    def do_action(self):
        if not v.paused:
            return
        self.function()


# SLIDER CODE
class Slider(Button):
    def __init__(self, text):
        super().__init__(text, None)
        self.label_text = text
        self.text = None
        self.slider_dimensions = None

    def draw(self, bg_shade=32):
        if settings["muted"]:
            volume = 0
            volume_text = "MUTED"
        else:
            volume = settings["volume"] / 100
            volume_text = f"{settings['volume']}%"
        self.text = v.standard_font.render(self.label_text.format(vol=volume_text), 1, (0, 0, 0))

        super().draw(bg_shade)

        self.slider_dimensions = [self.dimensions[0] + int((self.dimensions[2] - 20) * volume),
                                  self.dimensions[1], 20, 50]
        v.pygame.draw.rect(v.win, (128, 128, 128), self.slider_dimensions)
        v.pygame.draw.rect(v.win, (0, 0, 0), self.slider_dimensions, 2)


# S L A V
class Player(object):
    walkRight = []
    walkLeft = []
    for i in range(1, 10):
        walkRight.append(v.pygame.image.load(v.sprite_dir + "R" + str(i) + ".png"))
        walkRight[-1] = v.pygame.transform.scale(walkRight[-1], (256, 256))
        walkLeft.append(v.pygame.image.load(v.sprite_dir + "L" + str(i) + ".png"))
        walkLeft[-1] = v.pygame.transform.scale(walkLeft[-1], (256, 256))

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 10
        self.jumping = True
        self.left = False
        self.right = True
        self.walk_count = 0
        self.jump_count = 40
        self.standing = True
        self.hitbox = [self.x + 78, self.y + 58, 100, 190]

    def draw(self):
        if self.walk_count >= 17:
            self.walk_count = 0
        if not self.standing:
            if self.left:
                v.win.blit(self.walkLeft[round(self.walk_count) // 2], (self.x, self.y))
                if not v.paused:
                    self.walk_count += self.vel // 5 / 2
            elif self.right:
                v.win.blit(self.walkRight[round(self.walk_count) // 2], (self.x, self.y))
                if not v.paused:
                    self.walk_count += self.vel // 5 / 2
        else:
            if self.right:
                v.win.blit(self.walkRight[0], (self.x, self.y))
            else:
                v.win.blit(self.walkLeft[0], (self.x, self.y))
        self.hitbox = [self.x + 78, self.y + 58, 100, 190]
        if settings["showPlayerHitbox"]:
            v.pygame.draw.rect(v.win, (0, 255, 0), self.hitbox, 2)

    def hit(self):  # When killed
        # Stops all sound effects
        v.pygame.mixer.stop()
        # Resets all variables to start values
        self.jumping = True
        self.x = 128
        self.y = v.win_height - 100 - 256 + 64
        self.vel = 10
        self.walk_count = 0
        self.jump_count = 40
        text = v.large_font.render("BUSTED", 1, (255, 0, 0))
        v.win.blit(text, ((v.win_width // 2) - (text.get_width() // 2), 200))
        v.pygame.display.update()
        i = 0
        for gun in guns:
            gun.owned = False
        for powerup in purchasable_powerups:
            powerup.owned = 0
        while i < 100:  # Waits 100 * 10ms (one second)
            v.pygame.time.delay(10)
            i += 1
            # Checks to see if user has attempted to close v.window during that 1s
            for close_event in v.pygame.event.get():
                if close_event.type == v.pygame.QUIT:
                    i = 100
                    v.paused = True
                    v.pause_menu = "quit"


# P O L I C E
class Enemy(object):
    walkRight = []
    walkLeft = []
    for i in range(1, 12):
        walkRight.append(v.pygame.image.load(v.sprite_dir + "ER" + str(i) + ".png"))
        walkRight[-1] = v.pygame.transform.scale(walkRight[-1], (256, 256))
        walkLeft.append(v.pygame.image.load(v.sprite_dir + "EL" + str(i) + ".png"))
        walkLeft[-1] = v.pygame.transform.scale(walkLeft[-1], (256, 256))

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = [50, v.win_width - 50 - 64]
        self.walk_count = 0
        self.vel = -3
        self.hitbox = [self.x + 78, self.y + 58, 100, 190]
        self.health = 100
        self.sprite_area = [self.x, self.y, 256, 256]

    def draw(self):
        if not v.paused:
            self.move()
        # If within 50px of player and currently in 'attack' animation
        if abs(self.x - slav.x) > 50 and self.walk_count >= 24:
            self.walk_count = 0
        elif self.walk_count >= 32:
            self.walk_count = 0

        if self.vel > 0:
            v.win.blit(self.walkRight[self.walk_count // 3], (self.x, self.y))
            if not v.paused:
                self.walk_count += 1
        elif self.vel < 0:
            v.win.blit(self.walkLeft[self.walk_count // 3], (self.x, self.y))
            if not v.paused:
                self.walk_count += 1
        else:
            self.walk_count = 20
            v.win.blit(self.walkLeft[self.walk_count // 3], (self.x, self.y))
        self.hitbox = [self.x + 78, self.y + 58, 100, 190]
        # Drawing health bar
        v.pygame.draw.rect(v.win, (255, 0, 0), (self.hitbox[0], self.hitbox[1] - 35, 100, 20))
        v.pygame.draw.rect(v.win, (0, 128, 0), (self.hitbox[0], self.hitbox[1] - 35, self.health, 20))
        self.sprite_area = [self.x, self.y, 256, 256]
        if settings["showCopHitboxes"]:
            v.pygame.draw.rect(v.win, (255, 0, 0), self.hitbox, 2)
            v.pygame.draw.rect(v.win, (0, 0, 255), self.sprite_area, 2)

    def move(self):
        if v.wanted_level == 0:
            self.vel = 0
        elif self.walk_count <= 24:
            if slav.x > self.x:
                self.vel = 3
                self.x += self.vel
            else:
                self.vel = -3
                self.x += self.vel

    def hit(self):  # When shot by bullet
        if v.wanted_level == 0:
            v.wanted_level += 1
        v.sounds.append(Effect("bullet_hit"))
        minus = v.selected_gun.dmg
        if v.mayo_power:  # Double damage taken when player has mayo power
            minus *= 2
        if self.health - minus > 0:
            self.health -= minus
        else:
            if v.wanted_level < 5:
                v.wanted_level += 1
            v.cop_amount += 1
            random_death_sound = "die" + str(v.random.randint(1, 3))
            v.sounds.append(Effect(random_death_sound))
            self.health = 0
            for loot_type in ("ammo", "money"):
                variance = v.random.randint(3, 5)
                random_x = v.random.randint(self.x - 10 * variance, self.x + 10 * variance) + 128
                random_y = v.random.randint(self.y - 10 * variance, self.y + 10 * variance) + 128
                if v.random.randint(1, 3) > 1:
                    v.drops.append(LootDrop(random_x, random_y, variance, loot_type))
            v.cops.remove(self)
            # Deletes the oldest created loot drop if there are more than ten
            if len(v.drops) >= 10:
                v.drops.pop(0)

    def regenerate(self):  # Respawn
        self.health = 100
        self.x = v.win_width
        self.y = v.win_height - 93

    def touching_hitbox(self, hitbox: list[int, int, int, int]) -> bool:
        nw_corner = (hitbox[0], hitbox[1])
        ne_corner = (hitbox[0] + hitbox[2], hitbox[1])
        sw_corner = (hitbox[0], hitbox[1] + hitbox[3])
        se_corner = (hitbox[0] + hitbox[2], hitbox[1] + hitbox[3])
        return True in [self.touching_point(corner) for corner in [nw_corner, ne_corner, sw_corner, se_corner]]

    def touching_point(self, point: tuple[int, int]) -> bool:
        return self.hitbox[0] < point[0] < self.hitbox[0] + self.hitbox[2] and \
               self.hitbox[1] < point[1] < self.hitbox[1] + self.hitbox[3]


# MOVE OBJECTS ON SCREEN
def move(distance):
    if v.win_width // 3 > slav.x + distance > 80:
        slav.x += distance
    else:
        if v.win_x > v.win_width:
            v.win_x = 0
        if v.win_x < -v.win_width:
            v.win_x = 0
        v.win_x -= distance
        for cop_to_move in v.cops:
            cop_to_move.x -= distance
        for bullet in v.bullets:
            bullet.x -= distance
        for drop in v.drops:
            drop.x -= distance


def fire(rapid_fire):
    if not v.firing:
        if rapid_fire:
            v.sounds.append(Effect("bullet_fire_" + v.selected_gun.name + "_auto", channel="gun", should_loop=True))
        elif v.selected_gun.fullAuto:
            v.sounds.append(Effect("bullet_fire_" + v.selected_gun.name + "_start", channel="gun", should_loop=False))
        else:
            v.sounds.append(Effect("bullet_fire_" + v.selected_gun.name, channel="gun", should_loop=False))
    if v.shot_cooldown_time_passed >= v.shot_cooldown:
        # Makes the script wait a certain amount of time before a gun is able to fire again (rof = Rate of Fire)
        rate_of_fire = v.selected_gun.rof / 60  # rounds per second
        shot_interval = 1 / rate_of_fire  # seconds
        v.shot_cooldown_time_passed = 0
        v.shot_cooldown = shot_interval
        # Makes the bullet travel in the direction the player is facing
        if slav.left:
            facing = -1
        else:
            facing = 1
        # Fires bullet
        v.bullets.append(Projectile(round(slav.x + slav.width // 2),
                                    round(slav.y + slav.height // 2.5), 3, (0, 0, 0), facing))
        if not infinite_ammo:
            v.ammo_count -= 1
    v.firing = True


# RENDER GAME GRAPHICS / SPRITES
def redraw_game_window(cop_hovering_over):
    v.win.blit(v.bg, (v.win_x, 0))
    if v.win_x > 0:
        v.win.blit(v.bg, (v.win_x - v.win_width, 0))
    elif v.win_x < 0:
        v.win.blit(v.bg, (v.win_x + v.win_width, 0))
    for cop_to_draw in v.cops:
        cop_to_draw.draw()
    slav.draw()
    for drop in v.drops:
        drop.draw()
    for bullet in v.bullets:
        bullet.draw()
    score_text = v.bold_font.render("score: " + str(v.score), 1, (255, 255, 255))
    highscore_text = v.bold_font.render("highscore: " + str(settings["highscore"]), 1, (255, 255, 255))
    fps_counter_text = v.bold_font.render(str(round(fps)) + " FPS", 1, (255 - round(fps / 27 * 255),
                                                                        round(fps / 27 * 255), 0))
    if infinite_ammo:
        ammo_count_text = v.bold_font.render("ammo: infinite", 1, (255, 255, 255))
    else:
        ammo_count_text = v.bold_font.render("ammo: " + str(v.ammo_count), 1, (255, 255, 255))
    money_count_text = v.bold_font.render("money: $" + str(money_count), 1, (255, 255, 255))
    paused_text = v.big_font.render("PAUSED", 1, (255, 255, 255))
    paused_text_outline = v.big_outline_font.render("PAUSED", 1, (0, 0, 0))
    quit_text = v.big_font.render("Are you sure you want to quit?", 1, (255, 255, 255))
    for filled_star in range(1, v.wanted_level + 1):
        v.win.blit(v.star_1, (v.win_width - 32 * filled_star - 10, v.win_height - 32 - 10))
    for empty_star in range(v.wanted_level + 1, 6):
        v.win.blit(v.star_0, (v.win_width - 32 * empty_star - 10, v.win_height - 32 - 10))
    if v.paused:
        v.win.blit(v.pause_bg, (0, 0))
        for button_in_menu in buttons[v.pause_menu]:
            button_in_menu.draw()
        if v.pause_menu == "shop":
            v.win.blit(v.bg_store, (0, 0))
            v.win.blit(v.back, (16, v.win_height - 16 - 64 - 16))
            for gun in guns:
                gun.draw()
            for powerup in purchasable_powerups:
                powerup.draw()
            for purchasable_item in v.purchasables:
                purchasable_item.draw()
        elif v.pause_menu == "quit":
            v.win.blit(quit_text, (v.win_width // 2 - quit_text.get_width() // 2, v.win_height // 3))
        else:
            v.win.blit(paused_text_outline, (v.win_width // 2 - paused_text_outline.get_width() // 2,
                                             v.win_height // 5 + 1))
            v.win.blit(paused_text, (v.win_width // 2 - paused_text.get_width() // 2, v.win_height // 5))
            v.win.blit(v.store_icon, (16, v.win_height - 16 - 64))
    elif cop_hovering_over is not None:
        v.win.blit(v.mouse_icon, cop_hovering_over)
    v.win.blit(score_text, (v.win_width - score_text.get_width() - 20, 10))
    v.win.blit(highscore_text, (v.win_width - highscore_text.get_width() - 20, 30))
    v.win.blit(fps_counter_text, (v.win_width - fps_counter_text.get_width() - 20, 50))
    v.win.blit(ammo_count_text, (20, 10))
    v.win.blit(money_count_text, (20, 30))
    for powerup_shop_icon in powerups:
        powerup_shop_icon.draw()
    v.pygame.display.update()


# Calling classes
slav = Player(128, v.win_height - 100 - 256 + 64, 256, 256)


def toggle_mute():
    button_mute_music.selected = settings["muted"] = not settings["muted"]
    if settings["muted"]:
        v.pygame.mixer.music.set_volume(0)
    else:
        v.pygame.mixer.music.set_volume(settings["volume"] / 100)


def toggle_slav_hitbox():
    settings["showPlayerHitbox"] = not settings["showPlayerHitbox"]
    button_toggle_slav_hitbox.selected = settings["showPlayerHitbox"]


def toggle_cop_hitbox():
    settings["showCopHitboxes"] = not settings["showCopHitboxes"]
    button_toggle_cop_hitbox.selected = settings["showCopHitboxes"]


button_resume = Button("resume [ESC]", lambda: exec("v.paused = False"))
button_options = Button("options...", lambda: exec("v.pause_menu = 'options'"))
button_quit = Button("quit", lambda: exec("v.pause_menu = 'quit'"))
button_volume = Button("music options...", lambda: exec("v.pause_menu = 'volume'"))
button_options_dev = Button("developer options...", lambda: exec("v.pause_menu = 'dev'"))
button_back = Button("back... [ESC]", lambda: exec("v.pause_menu = 'main'"))
slider_volume = Slider("volume: {vol}")
button_mute_music = Button("mute background music", toggle_mute, settings["muted"])
button_back_volume = Button("back... [ESC]", lambda: exec("v.pause_menu = 'options'"))
button_toggle_slav_hitbox = Button("toggle player hitbox", toggle_slav_hitbox)
button_toggle_cop_hitbox = Button("toggle enemy hitboxes", toggle_cop_hitbox)
button_no = Button("no", lambda: exec("v.pause_menu = 'main'"))
button_yes = Button("yes", lambda: exec("v.run = False"))

buttons = {
    "main": [button_resume, button_options, button_quit],
    "options": [button_volume, button_options_dev, button_back],
    "volume": [slider_volume, button_mute_music, button_back_volume],
    "dev": [button_toggle_slav_hitbox, button_toggle_cop_hitbox, button_back],
    "quit": [button_no, button_yes],
    "shop": []
}

# gun_mp5 = weapon(v.win_width - 128 - 256, v.win_height // 8, name="MP5", cost=100, dmg=30, rof=750, full_auto=True)
# gun_ak47 = weapon(128, v.win_height // 2, name="AK-47", cost=300, dmg=50, rof=630, full_auto=True)
gun_beretta = Weapon(32, v.win_height // 8, name="Beretta", cost=100, dmg=20, rof=1000, full_auto=False)
gun_deagle = Weapon((v.win_width - 256) // 2, v.win_height // 8, "Deagle", cost=300, dmg=60, rof=200, full_auto=False)
guns = [gun_beretta, gun_deagle]

purchasable_light_ammo = AmmoPurchasable(v.win_width - 32 - 256, v.win_height // 8, cost=75)
purchasable_heavy_ammo = AmmoPurchasable(v.win_width - 32 - 256, v.win_height // 8, cost=100)

purchasable_powerup_mayo = AbilityPurchasable(32, v.win_height // 2, name="mayonnaise", cost=50)
purchasable_powerup_beer = AbilityPurchasable((v.win_width - 256) // 2, v.win_height // 2, name="beer", cost=100)
purchasable_powerups = [purchasable_powerup_mayo, purchasable_powerup_beer]

powerup_mayo = Ability(20, 75, "mayo")
powerup_beer = Ability(20, 75 + 100, "beer")
powerups = [powerup_mayo, powerup_beer]

# MAIN LOOP
while v.run:
    v.clock.tick(27)  # Loops every 1/27 seconds (27 FPS)
    fps = v.clock.get_fps()
    keys = v.pygame.key.get_pressed()
    mouse_pos = v.pygame.mouse.get_pos()
    # Detects v.window updates
    for event in v.pygame.event.get():
        if event.type == v.pygame.QUIT:  # If user clicks red 'X' button to close
            v.paused = True
            v.pause_menu = "quit"
        elif event.type == v.pygame.KEYDOWN:  # If a key is pressed down this frame
            # If the attack key was pressed this frame
            if event.key == setup.key_index[settings["attack_key"]] and v.selected_gun is not None:
                if v.shot_cooldown_time_passed >= v.shot_cooldown:
                    if v.ammo_count > 0 or infinite_ammo:
                        fire(rapid_fire=False)
                    else:  # Plays empty mag sound effect if space was pressed this frame
                        v.sounds.append(Effect("bullet_empty"))
            # If escape was pressed this frame
            elif event.key == setup.key_index[settings["pause_key"]]:
                if v.paused:
                    # Defines what pressing the escape key should do inside pause menu
                    v.pause_menu = v.pause_instructions[v.pause_menu]
                    if v.pause_menu == "unpause":
                        v.paused = False
                        v.pygame.mixer.unpause()
                    elif v.pause_menu == "prev":
                        v.pause_menu = v.previous_pause_menu
                else:  # Pauses game if escape is pressed
                    v.paused = True
                    v.pause_menu = "main"
                    v.pygame.mixer.pause()
        # Sound effect code
        elif event.type == v.pygame.KEYUP and event.key == setup.key_index[settings["attack_key"]] and v.firing:
            firing = False
            if v.selected_gun.fullAuto:
                v.pygame.mixer.Channel(1).stop()
                v.sounds.append(Effect("bullet_fire_" + v.selected_gun.name + "_end"))

        # If a mouse button is pressed this frame
        elif event.type == v.pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # If that mouse button is the left mouse button
                # If clicked mouse in pause menu
                if v.paused:
                    for button in buttons[v.pause_menu]:
                        dim = button.dimensions
                        # Check if the mouse is within the button's boundary
                        if dim[0] < mouse_pos[0] < dim[0] + dim[2] and dim[1] < mouse_pos[1] < dim[1] + dim[3]:
                            v.slider_engaged = button is slider_volume
                            if button is slider_volume:
                                settings["muted"] = False
                                button_mute_music.selected = False
                            else:
                                button.do_action()  # Sends message that button was clicked
                            break  # Not sure if this is needed but it can't do any harm

                # If clicked mouse in game
                else:
                    for powerup_icon in powerups:
                        dim = powerup_icon.dimensions
                        if dim[0] < mouse_pos[0] < dim[0] + dim[2] and dim[1] < mouse_pos[1] < dim[1] + dim[3]\
                                and powerup_icon.owned > 0 and powerup_icon.progress == 0:
                            powerup_icon.activate()
                            v.sounds.append(Effect("mayo"))
                            v.sounds.append(Effect("eating"))
                    if v.cop_hovering_over is not None:
                        if money_count >= 100:
                            money_count -= 100
                            v.wanted_level = 0
                            v.sounds.append(Effect("purchase"))
                        else:
                            v.sounds.append(Effect("error"))
                # If clicked mouse in shop
                if v.pause_menu == "shop":
                    if 16 < mouse_pos[0] < 16 + 128 and v.win_height - 16 - 64 < mouse_pos[1] < v.win_height - 16:
                        # Go back
                        v.pause_menu = v.previous_pause_menu
                    else:
                        # If clicked on a gun
                        for gun_icon in guns:
                            dim = gun_icon.outer_hitbox
                            if dim[0] < mouse_pos[0] < dim[0] + dim[2] and dim[1] < mouse_pos[1] < dim[1] + dim[3]:
                                if gun_icon.owned:
                                    v.selected_gun = gun_icon
                                    if gun_icon.name == "Beretta":
                                        v.purchasables = [purchasable_light_ammo]
                                    elif gun_icon.name == "Deagle":
                                        v.purchasables = [purchasable_heavy_ammo]
                                else:
                                    if gun_icon.affordable:
                                        gun_icon.owned = True
                                        money_count -= gun_icon.cost
                                        v.sounds.append(Effect("purchase"))
                                        v.selected_gun = gun_icon
                                        if gun_icon.name == "Beretta":
                                            v.purchasables = [purchasable_light_ammo]
                                        elif gun_icon.name == "Deagle":
                                            v.purchasables = [purchasable_heavy_ammo]
                                    else:
                                        v.sounds.append(Effect("error"))
                                        gun_icon.flash()
                            gun_icon.affordable = money_count >= gun_icon.cost
                        # If clicked on a powerup
                        for usable_powerup in purchasable_powerups:
                            dim = usable_powerup.outer_hitbox
                            if dim[0] < mouse_pos[0] < dim[0] + dim[2] and dim[1] < mouse_pos[1] < dim[1] + dim[3]:
                                if usable_powerup.affordable:
                                    usable_powerup.owned += 1
                                    money_count -= usable_powerup.cost
                                    v.sounds.append(Effect("purchase"))
                                else:
                                    v.sounds.append(Effect("error"))
                                    usable_powerup.flash()
                            usable_powerup.affordable = money_count >= usable_powerup.cost
                        # If clicked on another purchasable
                        for purchasable in v.purchasables:
                            dim = purchasable.outer_hitbox
                            if dim[0] < mouse_pos[0] < dim[0] + dim[2] and dim[1] < mouse_pos[1] < dim[1] + dim[3]:
                                if purchasable.affordable:
                                    money_count -= purchasable.cost
                                    v.ammo_count += 15
                                    v.sounds.append(Effect("purchase"))
                                else:
                                    v.sounds.append(Effect("error"))
                                    purchasable.flash()
                            purchasable.affordable = money_count >= purchasable.cost

                # If clicked shop icon
                elif 16 < mouse_pos[0] < 16 + 64 and v.win_height - 16 - 64 < mouse_pos[1] < v.win_height - 16:
                    # Enter shop
                    v.previous_pause_menu = v.pause_menu
                    v.pause_menu = "shop"
                    for gun_icon in guns:
                        gun_icon.affordable = money_count >= gun_icon.cost
                    for usable_powerup in purchasable_powerups:
                        usable_powerup.affordable = money_count >= usable_powerup.cost
                    for purchasable in v.purchasables:
                        purchasable.affordable = money_count >= purchasable.cost
        elif v.slider_engaged and event.type == v.pygame.MOUSEBUTTONUP and event.button == 1:
            v.slider_engaged = False

    # If dragging volume slider
    if v.pygame.mouse.get_pressed(num_buttons=3)[0] and v.slider_engaged:
        # Converts mouse position on slider into volume percentage
        temp_volume = int((mouse_pos[0] - (v.win_width // 2 - v.win_width / 4)) / (v.win_width // 2) * 100)

        # Changes the volume setting with a minimum of 0% and maximum of 100%
        if 0 <= temp_volume <= 100:
            settings["volume"] = temp_volume
        elif temp_volume < 0:
            settings["volume"] = 0
        elif temp_volume > 100:
            settings["volume"] = 100
        v.pygame.mixer.music.set_volume(settings["volume"] / 100)

    # GAME LOGIC
    if not v.paused:
        v.shot_cooldown_time_passed += 1 / 27  # Seconds
        if len(v.cops) < v.cop_amount:
            if v.time_passed_since_last_cop_spawned >= v.cop_spawn_delay:
                v.cops.append(Enemy(v.win_width - 1, v.win_height - v.random.randint(92, 112) - 256 + 64, 256, 256))
                v.time_passed_since_last_cop_spawned = 0
                v.cop_spawn_delay = v.random.randint(500, 3000) / 1000
            else:
                v.time_passed_since_last_cop_spawned += 1 / 27

        # Continues the activation animation of each powerup if it has already been started
        for powerup_icon in powerups:
            if powerup_icon.progress > 0:
                powerup_icon.activate()

        v.cop_hovering_over = None
        # If player touches any cop
        for cop in v.cops:
            if v.wanted_level > 0:
                if cop.touching_point(mouse_pos):
                    v.cop_hovering_over = (mouse_pos[0], mouse_pos[1])
                if not god_mode and cop.touching_hitbox(slav.hitbox) and 29 >= cop.walk_count >= 24:
                    slav.hit()
                    for powerup_icon in powerups:
                        powerup_icon.progress = 0
                    v.firing = False
                    v.score = 0
                    v.ammo_count = 20
                    money_count = settings["start_money"]
                    v.wanted_level = 0
                    v.cops = []
                    v.cop_amount = 1
                    v.bullets = []
                    v.drops = []
                    v.purchasables = []
                    v.selected_gun = None
                    v.mayo_power = False
                    v.cop_hovering_over = None
        # If player touches ammo drop
        for loot_drop in v.drops:
            if slav.hitbox[1] < loot_drop.hitbox[1] + loot_drop.hitbox[3] \
                    and slav.hitbox[1] + slav.hitbox[3] > loot_drop.hitbox[1]:
                if slav.hitbox[0] + slav.hitbox[2] > loot_drop.hitbox[0]\
                        and slav.hitbox[0] < loot_drop.hitbox[0] + loot_drop.hitbox[2]:
                    if loot_drop.loot_type == "ammo":
                        v.sounds.append(Effect("bullet_pickup"))
                        v.ammo_count += loot_drop.pickup_amount
                    else:
                        effect_number = v.random.randint(1, 10)  # Plays v.random coin pickup sound
                        v.sounds.append(Effect("money_pickup" + str(effect_number)))
                        money_count += loot_drop.pickup_amount
                        # Updates consumable affordability after picking up money
                        for gun_icon in guns:
                            gun_icon.affordable = money_count >= gun_icon.cost
                        for usable_powerup in purchasable_powerups:
                            usable_powerup.affordable = money_count >= usable_powerup.cost
                    v.drops.remove(loot_drop)  # Deletes loot drop sprite after collecting it
        # If any bullet touches any cop
        for fired_bullet in v.bullets:
            if v.win_width >= fired_bullet.x >= 0:
                fired_bullet.x += fired_bullet.vel
            else:
                try:
                    v.bullets.remove(fired_bullet)
                    continue
                except Exception as e:
                    print("Uh oh. Idk what this error is. Exception:", e)
            for cop in v.cops:
                if cop.touching_point((fired_bullet.x, fired_bullet.y)):
                    cop.hit()
                    v.score += 1
                    v.bullets.remove(fired_bullet)
                    break
        # Moving left
        if keys[setup.key_index[settings["left_key"]]] or keys[v.pygame.K_LEFT]:
            move(-slav.vel)
            slav.left = True
            slav.right = False
            slav.standing = False            
        # Moving right
        elif keys[setup.key_index[settings["right_key"]]] or keys[v.pygame.K_RIGHT]:
            move(slav.vel)
            slav.right = True
            slav.left = False
            slav.standing = False
        # Not moving
        else:
            slav.standing = True
            slav.walk_count = 0
        # Jumping
        if not slav.jumping:
            if keys[setup.key_index[settings["jump_key"]]] or keys[v.pygame.K_UP]:
                slav.jumping = True
        elif slav.jump_count > -40:
            slav.y -= slav.jump_count
            slav.jump_count -= 8
        else:
            slav.y -= slav.jump_count
            slav.jump_count = 40
            slav.jumping = False

        if v.score > settings["highscore"]:
            settings["highscore"] = v.score  # Updates high score if user has surpassed it
    redraw_game_window(v.cop_hovering_over)
v.pygame.quit()
setup.finish(settings)
