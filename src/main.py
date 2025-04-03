import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invader")
    
    game = Game(screen)
    clock = pygame.time.Clock()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()