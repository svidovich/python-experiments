import inspect
import sys
from typing import Final, Tuple

import pygame
from pygame import Surface
from pygame.event import Event
from pygame.math import Vector2
from pygame.sprite import Group, Sprite
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
        self.surf = Surface(size=size)
        self.surf.fill(color=fill_color)
        # The center kwarg... defines where it starts out?
        self.rect = self.surf.get_rect(center=(10, HEIGHT - 30))


class Platform(Sprite):
    PLATFORM_DEFAULT_FILL = (255, 0, 0)
    PLATFORM_DEFAULT_SIZE = (WIDTH // 4, 20)
    def __init__(self, size: Tuple[int]=PLATFORM_DEFAULT_SIZE, fill_color: Tuple[int]=PLATFORM_DEFAULT_FILL, initial_postition: Tuple[int]=ORIGIN):
        super().__init__()
        self.surf = Surface(size=size)
        self.surf.fill(color=fill_color)
        self.rect = self.surf.get_rect(center=(initial_postition))


def main():
    pygame.init()
    game_clock: Clock = pygame.time.Clock()
    print(f'fps: {game_clock}, {type(game_clock)}')
    display_surface: Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    print(f'Display surface: {type(display_surface)}')
    pygame.display.set_caption("A Game")
    
    platform_1 = Platform(size=(WIDTH, 20), initial_postition=(WIDTH // 2, HEIGHT - 10))
    player_1 = Player()

    all_sprites = Group()
    all_sprites.add([platform_1, player_1])

    while True:
        event: Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            display_surface.fill(BLACK)
        
        entity: Sprite
        for entity in all_sprites:
            display_surface.blit(source=entity.surf, dest=entity.rect)
        
        pygame.display.update()
        game_clock.tick(FPS)



if __name__ == "__main__":
    main()
