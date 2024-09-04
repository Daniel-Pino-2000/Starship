import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up some constants
SHIP_SPEED = 5
LASER_BEAM_SPEED = 10
OBSTACLE_SPEED = 3
ENEMY_SHIP_SPEED = 2
ENEMY_LASER_BEAM_SPEED = 5

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Load the images
background_image = pygame.image.load('background.jpg')
player_ship_image = pygame.image.load('player_ship.png')
enemy_ship_image = pygame.image.load('enemy_ship.png')
obstacle_image = pygame.image.load('obstacle.png')
meteorite_frame1 = pygame.image.load('meteorite_frame1.png')
meteorite_frame2 = pygame.image.load('meteorite_frame2.png')

player_ship_image = pygame.transform.scale(player_ship_image, (50, 50))

enemy_ship_image = pygame.image.load('enemy_ship.png')
enemy_ship_image = pygame.transform.scale(enemy_ship_image, (player_ship_image.get_width(), player_ship_image.get_height()))

# Load the audio files
player_laser_sound = pygame.mixer.Sound('player_laser.mp3')
enemy_laser_sound = pygame.mixer.Sound('enemy_laser.mp3')
explosion_sound = pygame.mixer.Sound('explosion.wav')

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Set up the player's ship
class Ship:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = SHIP_SPEED
        self.laser_beam = None

    def move(self, direction):
        if direction == 'up':
            self.y -= self.speed
        elif direction == 'down':
            self.y += self.speed
        elif direction == 'left':
            self.x -= self.speed
        elif direction == 'right':
            self.x += self.speed

        # Don't allow the ship to leave the screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - player_ship_image.get_width()))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - player_ship_image.get_height()))

    def shoot_laser(self):
        self.laser_beam = LaserBeam(self.x + player_ship_image.get_width() // 2, self.y)
        player_laser_sound.play()

    def draw(self):
        screen.blit(player_ship_image, (self.x, self.y))

# Set up the laser beam
class LaserBeam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = LASER_BEAM_SPEED

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 10, 10))

# Set up the obstacles
class Obstacle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - obstacle_image.get_width())
        self.y = -obstacle_image.get_height()
        self.speed = OBSTACLE_SPEED
        self.animation_images = [obstacle_image, meteorite_frame1, meteorite_frame2]
        self.current_animation_image = 0
        self.animation_rate = 0.1  # in seconds
        self.last_animation_time = pygame.time.get_ticks()

    def animate(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_animation_time) / 1000 > self.animation_rate:
            self.current_animation_image = (self.current_animation_image + 1) % len(self.animation_images)
            self.last_animation_time = current_time

    def move(self):
        self.y += self.speed

    def draw(self):
        self.animate()
        screen.blit(self.animation_images[self.current_animation_image], (self.x, self.y))

class EnemyShip:
    def __init__(self, player_ship):
        self.x = random.randint(0, SCREEN_WIDTH - enemy_ship_image.get_width())
        self.y = -enemy_ship_image.get_height()
        self.speed = ENEMY_SHIP_SPEED
        self.laser_beams = []
        self.player_ship = player_ship
        self.target_x = player_ship.x
        self.target_y = player_ship.y
        self.shoot_time = pygame.time.get_ticks()
        self.shoot_interval = 1000  # in milliseconds, change this value to adjust the cadence of shots

    def move(self):
        dx = self.player_ship.x - self.x
        dy = self.player_ship.y - self.y
        angle = math.atan2(dy, dx)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

    def shoot_laser(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.shoot_time >= self.shoot_interval:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            angle = math.atan2(dy, dx)
            self.laser_beams.append(EnemyLaserBeam(self.x + enemy_ship_image.get_width() // 2, self.y, angle))
            self.shoot_time = current_time
            enemy_laser_sound.play()

    def draw(self):
        screen.blit(enemy_ship_image, (self.x, self.y))

class EnemyLaserBeam:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = ENEMY_LASER_BEAM_SPEED

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 10, 10))

class GameOverState:
    def __init__(self, score):
        self.score = score
        self.game_over_text = font.render("Game Over", True, (255, 0, 0))
        self.score_text = font.render("Score: " + str(score), True, (255, 0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        pass

    def draw(self):
        screen.fill((0, 0, 0))
        screen.blit(self.game_over_text, (SCREEN_WIDTH // 2 - self.game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - self.game_over_text.get_height()))
        screen.blit(self.score_text, (SCREEN_WIDTH // 2 - self.score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

# Create the player's ship
player_ship = Ship()

# Create a list of obstacles
obstacles = []

# Create a list of enemy ships
enemy_ships = [EnemyShip(player_ship)]

# Add a score tracking variable
score = 0

# Main loop
start_time = pygame.time.get_ticks()
game_over = False
font = pygame.font.SysFont(None, 30)  # Define font for score display
while not game_over:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # Get the pressed keys
    keys = pygame.key.get_pressed()

    # Move the player's ship
    if keys[pygame.K_UP]:
        player_ship.move('up')
    if keys[pygame.K_DOWN]:
        player_ship.move('down')
    if keys[pygame.K_LEFT]:
        player_ship.move('left')
    if keys[pygame.K_RIGHT]:
        player_ship.move('right')

    # Shoot a laser beam when the space key is pressed
    if keys[pygame.K_SPACE] and not player_ship.laser_beam:
        player_ship.shoot_laser()

    # Move the laser beam
    if player_ship.laser_beam:
        player_ship.laser_beam.move()
        if player_ship.laser_beam.y < 0:
            player_ship.laser_beam = None

    # Add new obstacles
    if random.random() < 0.01:  # Reduced the frequency of obstacles
        obstacles.append(Obstacle())

    # Move the obstacles
    for obstacle in obstacles:
        obstacle.move()
        if obstacle.y > SCREEN_HEIGHT:
            obstacles.remove(obstacle)

    # Check for collisions between the laser beam and the enemy ships
    if player_ship.laser_beam:
        for enemy_ship in enemy_ships[:]:
            if player_ship.laser_beam and player_ship.laser_beam.y < SCREEN_HEIGHT:
                laser_rect = pygame.Rect(player_ship.laser_beam.x, player_ship.laser_beam.y, 10, 10)
                enemy_rect = pygame.Rect(enemy_ship.x, enemy_ship.y, enemy_ship_image.get_width(), enemy_ship_image.get_height())
                if laser_rect.colliderect(enemy_rect):
                    enemy_ships.remove(enemy_ship)
                    player_ship.laser_beam = None
                    score += 3
                    explosion_sound.play()
                    break

    # Add new enemy ships
    if random.random() < 0.01:  # Reduced the frequency of enemy ships
        enemy_ships.append(EnemyShip(player_ship))

    # Make the enemy ships shoot at the player's last position
    for enemy_ship in enemy_ships:
        if random.random() < 0.1:
            enemy_ship.target_x = player_ship.x
            enemy_ship.target_y = player_ship.y
            enemy_ship.shoot_laser()

    # Move the enemy laser beams
    for enemy_ship in enemy_ships:
        for laser_beam in enemy_ship.laser_beams:
            laser_beam.move()

    # Check for collisions between the laser beam and the obstacles
    if player_ship.laser_beam:
        for obstacle in obstacles[:]:
            if player_ship.laser_beam and player_ship.laser_beam.y < SCREEN_HEIGHT:
                laser_rect = pygame.Rect(player_ship.laser_beam.x, player_ship.laser_beam.y, 10, 10)
                obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle_image.get_width(), obstacle_image.get_height())
                if laser_rect.colliderect(obstacle_rect):
                    obstacles.remove(obstacle)
                    player_ship.laser_beam = None
                    score += 1
                    explosion_sound.play()
                    break

    # Move the enemy ships
    for enemy_ship in enemy_ships[:]:
        enemy_ship.move()
        if enemy_ship.y > SCREEN_HEIGHT:
            enemy_ships.remove(enemy_ship)

    # Check for collisions between the player's ship and the obstacles
    player_rect = pygame.Rect(player_ship.x, player_ship.y, player_ship_image.get_width(), player_ship_image.get_height())
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle_image.get_width(), obstacle_image.get_height())
        if player_rect.colliderect(obstacle_rect):
            game_over = True

    # Check for collisions between the player's ship and the enemy laser beams
    for enemy_ship in enemy_ships:
        for laser_beam in enemy_ship.laser_beams:
            laser_rect = pygame.Rect(laser_beam.x, laser_beam.y, 10, 10)
            if player_rect.colliderect(laser_rect):
                game_over = True

    # Check for collisions between the player's ship and the enemy ships
    for enemy_ship in enemy_ships:
        enemy_rect = pygame.Rect(enemy_ship.x, enemy_ship.y, enemy_ship_image.get_width(), enemy_ship_image.get_height())
        if player_rect.colliderect(enemy_rect):
            game_over = True

    # Draw everything
    screen.blit(background_image, (0, 0))
    player_ship.draw()
    if player_ship.laser_beam:
        player_ship.laser_beam.draw()
    for obstacle in obstacles:
        obstacle.draw()
    for enemy_ship in enemy_ships:
        enemy_ship.draw()
        for laser_beam in enemy_ship.laser_beams:
            laser_beam.draw()
            
    # If the game is over, create a new GameOverState object and call its methods
    if game_over:
        game_over_state = GameOverState(score)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Fill the screen with a background color
            screen.fill((0, 0, 0))

            # Draw the game over state
            game_over_state.update()
            game_over_state.draw()

            # Draw the message telling the user how to exit the game
            font = pygame.font.SysFont(None, 50)  # Increase the font size
            text = font.render("Press ESC to exit", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))  # Center the text

            pygame.display.flip()

    # Display score
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)