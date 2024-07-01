import pygame
import random
import sys
from abc import ABC, abstractmethod
from config import USE_FLYWEIGHT, USE_OBSERVER, USE_STRATEGY

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Shooter")
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Observer pattern
class Observer(ABC):

    @abstractmethod
    def update(self, event):
        pass

class Subject(ABC):
    def __init__(self, game_state):
        self._observers = []
        self.game_state = game_state

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event):
        for observer in self._observers:
            observer.update(event, self.game_state)

class GameCollisions(Subject): 

    def change_state(self, event): 
        self.notify(event)

class GameState():
    def __init__(self, time_limit):
        super().__init__()
        self.score = 0
        self.health = 10000
        self.start_ticks = pygame.time.get_ticks()  # Get the initial ticks
        self.time_limit = time_limit  # Time limit in seconds
        self.remaining_time = time_limit
        self.score_text = font.render(f"Score: {0}", True, (255, 255, 255))
        self.health_text = font.render(f"Health: {10000}", True, (255, 255, 255))
        
    def update_timer(self): 
        elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        self.remaining_time = max(0, self.time_limit - elapsed_seconds)

    def draw(self): 
        
        screen.blit(self.score_text, (10, 10))
        screen.blit(self.health_text, (10, 50))
        screen.blit(font.render(f"Time: {self.remaining_time:.2f}", True, (255, 255, 255)), (10, 90))

class ScoreObserver(Observer):
    def update(self, event, game_state):
        if event == "ENEMY_HIT":
            
            game_state.score += 5
            game_state.score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
            

class HealthObserver(Observer):
    def update(self, event, game_state):
        if event == "PLAYER_HIT":
            game_state.health -= 20
            game_state.health_text = font.render(f"Health: {game_state.health}", True, (255, 255, 255))
            

# Flyweight pattern
class Flyweight:
    def __init__(self, image):
        self.image = image

class FlyweightFactory:
    def __init__(self):
        self._flyweights = {}

    def get_flyweight(self, key):
        return self._flyweights.setdefault(key, Flyweight(pygame.image.load(key).convert_alpha()))

flyweight_factory = FlyweightFactory()

# Strategy pattern
class EnemyBehavior(ABC):
    @abstractmethod
    def move(self, enemy):
        pass

class StraightBehavior(EnemyBehavior):
    def move(self, enemy):
        enemy.rect.y += enemy.speed

class LeftBehavior(EnemyBehavior):
    def move(self, enemy):
        enemy.rect.x -= enemy.speed
        enemy.rect.y += enemy.speed

class RightBehavior(EnemyBehavior):
    def move(self, enemy):
        enemy.rect.x += enemy.speed
        enemy.rect.y += enemy.speed

# Game objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(400, 500))
        self.speed = 8  # Increase player speed

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
        if USE_FLYWEIGHT:
            self.flyweight = flyweight_factory.get_flyweight("bullet.png")
            self.image = self.flyweight.image
        else:
            self.image = pygame.image.load("bullet.png").convert_alpha()
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_rect_x):
        super().__init__()
        if USE_FLYWEIGHT:
            self.flyweight = flyweight_factory.get_flyweight("enemy.png")
            self.image = self.flyweight.image
        else:
            self.image = pygame.image.load("enemy.png").convert_alpha()
        self.rect = self.image.get_rect(center=(random.randint(0, 800), -50))
        self.speed = 10
        self.direction = 1
        self.player_rect_x = player_rect_x
        
        if USE_STRATEGY:
            self.setStrategy()
        

    def setStrategy(self): 
        dif = (self.player_rect_x - self.rect.x) 

        if dif >= 30:
            self.strategy = RightBehavior()
        elif dif <= -30:
            self.strategy = LeftBehavior()
        else: 
            self.strategy = StraightBehavior()
    
    def update(self, new_player_rect_x):
        if random.randint(1, 200) == 1:
            self.player_rect_x = new_player_rect_x
            self.setStrategy()
        self.move()
        if self.rect.top > 600:
            self.kill()

    def move(self):
        if USE_STRATEGY:
            self.strategy.move(self)
        else:
            if self.rect.x < self.player_rect_x:
                self.rect.x += self.speed
                self.rect.y += self.speed
            elif self.rect.x > self.player_rect_x:
                self.rect.x -= self.speed
                self.rect.y += self.speed
            else: 
                self.rect.y += self.speed

def simulate_player_actions(player, bullet_group, frame_count):
    """ Simulate player movements and shooting based on frame count for automated testing. """
    screen_width, screen_height = screen.get_size()  # Get the actual screen dimensions dynamically
    margin = 100  # Reduced margin from the edges for a wider movement range
    vertical_speed = player.speed * 0.8  # Decrease speed for more controlled movement

    # Define movement patterns based on frame count
    cycle = frame_count % 400  # Adjust cycle length for more fluid zigzag

    # Zigzag pattern with enhanced vertical movement
    if cycle < 100:
        player.rect.x += vertical_speed  # Move right more slowly
        if cycle % 20 < 10:  # Zigzag down and up every 10 frames
            player.rect.y += vertical_speed + 13
        else: 
            player.rect.y -= vertical_speed + 13
    elif cycle < 200:
        player.rect.x -= vertical_speed  # Move left more slowly
        if cycle % 20 < 10:
            player.rect.y += vertical_speed + 13
        else:
            player.rect.y -= vertical_speed + 13
    elif cycle < 300:
        player.rect.x += vertical_speed  # Move right again more slowly
        if cycle % 20 < 10:
            player.rect.y += vertical_speed + 13
        else:
            player.rect.y -= vertical_speed + 13
    elif cycle < 400:
        player.rect.x -= vertical_speed  # Move left again more slowly
        if cycle % 20 < 10:
            player.rect.y += vertical_speed + 13
        else:
            player.rect.y -= vertical_speed + 13

    # Ensure the player doesn't move outside the screen boundaries
    player.rect.x = max(margin, min(player.rect.x, screen_width - margin))
    player.rect.y = max(margin, min(player.rect.y, screen_height - margin))

    # Fire bullets less frequently to better observe shooting mechanics
    if frame_count % 8 == 0:  # Reduce the firing rate for testing
        bullet = Bullet(player.rect.centerx, player.rect.top)
        bullet_group.add(bullet)

def main_game_loop():
    game_state = GameState(15)  # Assuming a 15-second timer
    if USE_OBSERVER:
        game_collisions = GameCollisions(game_state)
        score_observer = ScoreObserver()
        health_observer = HealthObserver()
        game_collisions.attach(score_observer)
        game_collisions.attach(health_observer)

    player = Player()
    player_group = pygame.sprite.Group(player)
    bullet_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()

    clock = pygame.time.Clock()
    running = True
    game_over = False
    win = False
    frame_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over and not win:
            game_state.update_timer()
            simulate_player_actions(player, bullet_group, frame_count)

            if random.randint(1, 10) == 1:
                enemy = Enemy(player.rect.x)
                enemy_group.add(enemy)

            player_group.update()
            bullet_group.update()
            enemy_group.update(player.rect.x)

            collisions = pygame.sprite.groupcollide(enemy_group, bullet_group, True, True)

            for collision in collisions:
                if USE_OBSERVER:
                    game_collisions.change_state("ENEMY_HIT")
                else: 
                    game_state.score += 5
                    game_state.score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))

            player_hit = pygame.sprite.spritecollideany(player, enemy_group)

            if player_hit:
                if USE_OBSERVER: 

                    game_collisions.change_state("PLAYER_HIT")
                
                else: 
                    game_state.health -= 20
                    game_state.health_text = font.render(f"Health: {game_state.health}", True, (255, 255, 255))


                player_hit.kill()

            if game_state.health <= 0:
                game_over = True
            if game_state.remaining_time <= 0 and game_state.health > 0:
                win = True
            if game_state.score >= 10000:
                win = True
                game_over = True

        screen.fill((0, 0, 0))
        player_group.draw(screen)
        bullet_group.draw(screen)
        enemy_group.draw(screen)

        game_state.draw()

        if game_over and game_state.health <= 0:
            lose_text = large_font.render("You Lose!", True, (255, 0, 0))
            screen.blit(lose_text, (250, 250))
        elif win:
            win_text = large_font.render("You Win!", True, (0, 255, 0))
            screen.blit(win_text, (250, 250))

        pygame.display.flip()
        clock.tick(60)
        frame_count += 1  # Increment to change automated actions over time

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game_loop()
