import inspect
import sys
from typing import Final, Tuple

import pygame
from pygame import Rect, Surface
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN
from pygame.event import Event
from pygame.key import ScancodeWrapper
from pygame.math import Vector2
from pygame.sprite import Group, Sprite, spritecollideany, spritecollide
from pygame.time import Clock

HEIGHT: Final[int] = 450
WIDTH: Final[int] = 400

ACCELERATION: Final[float] = 0.5
FRICTION: Final[float] = -0.12
FPS: Final[int] = 60

ORIGIN: Final[Tuple[int, int]] = (0, 0)
BLACK = (0, 0, 0)
 

class Player(Sprite):
    PLAYER_DEFAULT_FILL = (67, 179, 174) # Verdigris
    PLAYER_DEFAULT_SIZE = (30, 30)
    def __init__(self, size: Tuple[int]=PLAYER_DEFAULT_SIZE, fill_color: Tuple[int]=PLAYER_DEFAULT_FILL) -> None:
        super().__init__()
        self.surface = Surface(size=size)
        self.surface.fill(color=fill_color)
        self.rect: Rect = self.surface.get_rect()

        # Vector2 takes individual ordinates for its argument OR
        # a tuple of coordinates.
        self.position = Vector2((WIDTH // 2, HEIGHT // 2))
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def draw(self, surface: Surface) -> None:
        surface.blit(source=self.surface, dest=self.rect)
    
    def move(self, collide=False) -> None:
        self.acceleration = Vector2(0,0)

        pressed_keys: ScancodeWrapper = pygame.key.get_pressed()

        if collide and self.velocity != Vector2(0,0):
            self.velocity = Vector2(0,0)# -self.velocity
            self.acceleration = Vector2(0,0)
        else:
        # Here, we're using ScancodeWrapper, which is a very bizarre
        # class that uses an indexing scheme to address specific keys
        # that are pulled as constants from the pygame main module.
            if pressed_keys[K_LEFT]:
                self.acceleration.x = -ACCELERATION
            if pressed_keys[K_RIGHT]:
                self.acceleration.x = ACCELERATION
            # Origin is in the top-left, so these are opposite what
            # one might expect
            if pressed_keys[K_UP]:
                self.acceleration.y = -ACCELERATION
            if pressed_keys[K_DOWN]:
                self.acceleration.y = ACCELERATION
        
        # Motion equations. Yawn.
        print(f"currentacc {self.acceleration}")
        self.acceleration += self.velocity * FRICTION
        print(f"Now adding to velocity {self.acceleration}")
        self.velocity += self.acceleration
        self.position += self.velocity + (0.5 * self.acceleration)

        # Make sure we're not out of bounds.
        # Here, we do 'pacman-style' warping, where we exit
        # the screen on one side and enter back in on the other
        if self.position.x > WIDTH:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = WIDTH
        
        if self.position.y > HEIGHT:
            self.position.y = 0
        if self.position.y < 0:
            self.position.y = HEIGHT

        self.rect.midbottom = self.position


class Wall(Sprite):
    WALL_DEFAULT_FILL = (255, 0, 0)
    WALL_DEFAULT_SIZE = (WIDTH // 4, 20)
    def __init__(self, size: Tuple[int]=WALL_DEFAULT_SIZE, fill_color: Tuple[int]=WALL_DEFAULT_FILL, initial_postition: Tuple[int]=ORIGIN):
        super().__init__()
        self.surface = Surface(size=size)
        self.surface.fill(color=fill_color)
        self.rect: Rect = self.surface.get_rect()

        self.position = Vector2(initial_postition)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
    
    # TODO: Add an overlying class -- this is all common stuff
    def draw(self, surface: Surface) -> None:
        surface.blit(source=self.surface, dest=self.rect)

def main():
    pygame.init()
    game_clock: Clock = pygame.time.Clock()
    print(f'fps: {game_clock}, {type(game_clock)}')
    display_surface: Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    print(f'Display surface: {type(display_surface)}')
    pygame.display.set_caption("A Game")
    
    wall_1 = Wall(size=(WIDTH, 20), initial_postition=(WIDTH // 2, HEIGHT - 10))
    player_1 = Player()
    # Puts player sprite to initial position
    player_1.move()

    all_sprites = Group()
    walls = Group()
    all_sprites.add([wall_1, player_1])
    walls.add([wall_1])
    import pdb
    # pdb.set_trace()

    while True:
        pygame.display.update()

        event: Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            display_surface.fill(BLACK)

        hits = spritecollide(sprite=player_1, group=walls, dokill=False)
        if not hits:
            player_1.move()
        else:
            # player_1.position.y += 7
            player_1.move(collide=True)
            # pdb.set_trace()
        # print(hits)

        entity: Sprite
        display_surface.fill(BLACK)
        for entity in all_sprites:
            entity.draw(surface=display_surface)
        
        game_clock.tick(FPS)



if __name__ == "__main__":
    main()
