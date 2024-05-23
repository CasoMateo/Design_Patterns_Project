import pygame
import random
import sys
from abc import ABC, abstractmethod

# Toggle flags
USE_FLYWEIGHT = True
USE_OBSERVER = True
USE_STRATEGY = False

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Shooter")

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Observer pattern
class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass

class Subject(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class GameState(Subject):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.health = 100

    def change_state(self, event):
        if USE_OBSERVER:
            self.notify(event)
        else:
            if event == "ENEMY_HIT":
                self.score += 10
            elif event == "PLAYER_HIT":
                self.health -= 25

class ScoreObserver(Observer):
    def update(self, event):
        if event == "ENEMY_HIT":
            game_state.score += 10
            print(f"Score updated: {game_state.score}")

class HealthObserver(Observer):
    def update(self, event):
        if event == "PLAYER_HIT":
            game_state.health -= 25
            print(f"Health updated: {game_state.health}")

class TimerObserver(Observer):
    def __init__(self, time_limit):
        self.start_ticks = pygame.time.get_ticks()  # Get the initial ticks
        self.time_limit = time_limit  # Time limit in seconds
        self.remaining_time = time_limit

    def update(self, event):
        elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        self.remaining_time = max(0, self.time_limit - elapsed_seconds)
        if self.remaining_time <= 0 and game_state.health > 0:
            game_state.notify("TIME_UP")

game_state = GameState()
score_observer = ScoreObserver()
health_observer = HealthObserver()
timer_observer = TimerObserver(15)  # 15 seconds timer

if USE_OBSERVER:
    game_state.attach(score_observer)
    game_state.attach(health_observer)
    game_state.attach(timer_observer)

# Flyweight pattern
class EnemyFlyweight:
    def __init__(self, image):
        self.image = image

class FlyweightFactory:
    def __init__(self):
        self._flyweights = {}

    def get_flyweight(self, key):
        if key not in self._flyweights:
            self._flyweights[key] = EnemyFlyweight(pygame.image.load(key).convert_alpha())
        return self._flyweights[key]

flyweight_factory = FlyweightFactory()

# Strategy pattern
class EnemyBehavior(ABC):
    @abstractmethod
    def move(self, enemy):
        pass

class ZigZagBehavior(EnemyBehavior):
    def move(self, enemy):
        enemy.rect.x += enemy.speed * enemy.direction
        enemy.rect.y += enemy.speed
        if enemy.rect.x <= 0 or enemy.rect.x >= 800:
            enemy.direction *= -1

class StraightBehavior(EnemyBehavior):
    def move(self, enemy):
        enemy.rect.y += enemy.speed

class TowardsPlayerBehavior(EnemyBehavior):
    def move(self, enemy):
        if enemy.rect.x < enemy.player.rect.x:
            enemy.rect.x += enemy.speed
        elif enemy.rect.x > enemy.player.rect.x:
            enemy.rect.x -= enemy.speed
        enemy.rect.y += enemy.speed

# Game objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(400, 500))
        self.speed = 7  # Increase player speed

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < 600:
            self.rect.y += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, behavior=None):
        super().__init__()
        if USE_FLYWEIGHT:
            self.flyweight = flyweight_factory.get_flyweight("enemy.png")
            self.image = self.flyweight.image
        else:
            self.image = pygame.image.load("enemy.png").convert_alpha()
        self.rect = self.image.get_rect(center=(random.randint(0, 800), -50))
        self.speed = 10  # Increase enemy speed for more difficulty
        self.direction = 1
        self.player = player
        if USE_STRATEGY:
            if self.rect.x < player.rect.x:
                self.behavior = TowardsPlayerBehavior()
            else:
                self.behavior = ZigZagBehavior()
        else:
            # Implement behavior directly (messier way)
            if self.rect.x < player.rect.x:
                self.move = self.move_towards_player
            else:
                self.move = self.move_zigzag

    def update(self):
        if USE_STRATEGY:
            self.behavior.move(self)
        else:
            self.move()
        if self.rect.top > 600:
            self.kill()

    def move_zigzag(self):
        self.rect.x += self.speed * self.direction
        self.rect.y += self.speed
        if self.rect.x <= 0 or self.rect.x >= 800:
            self.direction *= -1

    def move_straight(self):
        self.rect.y += self.speed

    def move_towards_player(self):
        if self.rect.x < self.player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > self.player.rect.x:
            self.rect.x -= self.speed
        self.rect.y += self.speed

# Sprite groups
player = Player()
player_group = pygame.sprite.Group(player)
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Main game loop
clock = pygame.time.Clock()
running = True
game_over = False
win = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over and not win:
        # Update timer
        timer_observer.update(None)
        remaining_time = timer_observer.remaining_time

        # Spawn enemies less frequently
        if random.randint(1, 20) == 1:
            enemy = Enemy(player)
            enemy_group.add(enemy)

        # Shooting bullets
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            bullet = Bullet(player.rect.centerx, player.rect.top)
            bullet_group.add(bullet)

        # Update sprites
        player_group.update()
        bullet_group.update()
        enemy_group.update()

        # Check collisions between bullets and enemies
        collisions = pygame.sprite.groupcollide(enemy_group, bullet_group, True, True)
        for collision in collisions:
            game_state.change_state("ENEMY_HIT")

        # Check collisions between player and enemies
        player_hit = pygame.sprite.spritecollideany(player, enemy_group)
        if player_hit:
            game_state.change_state("PLAYER_HIT")
            player_hit.kill()  # Remove the enemy that hit the player

        # Check win/lose conditions
        if game_state.health <= 0:
            game_over = True
        if remaining_time <= 0 and game_state.health > 0:
            win = True
        if game_state.score >= 100:
            win = True
            game_over = True

    # Draw everything
    screen.fill((0, 0, 0))
    player_group.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)

    # Draw score, health, and timer
    score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
    health_text = font.render(f"Health: {game_state.health}", True, (255, 255, 255))
    timer_text = font.render(f"Time: {remaining_time:.2f}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))
    screen.blit(timer_text, (10, 90))

    # Draw win/lose messages
    if game_over and game_state.health <= 0:
        lose_text = large_font.render("You Lose!", True, (255, 0, 0))
        

        screen.blit(lose_text, (250, 250))
    elif win:
        win_text = large_font.render("You Win!", True, (0, 255, 0))
        screen.blit(win_text, (250, 250))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
