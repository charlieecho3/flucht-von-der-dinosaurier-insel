import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))

try:
    test_img = pygame.image.load("konrad_insel/bg_entities/player_3.png").convert_alpha()
except pygame.error as e:
    print("Failed to load image:", e)
    sys.exit()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    screen.blit(test_img, (100, 100))

    pygame.display.flip()

pygame.quit()