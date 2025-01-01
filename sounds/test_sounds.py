import pygame
import sys
from config import Config  # Ensure config.py is in the same directory or adjust the import accordingly

def main():
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Sound Test")
    
    # Set up the display (required for some Pygame functionalities)
    screen = pygame.display.set_mode((400, 300))
    
    # Initialize the mixer
    try:
        pygame.mixer.init()
        print("Pygame mixer initialized successfully.")
    except pygame.error as e:
        print(f"Failed to initialize Pygame mixer: {e}")
        sys.exit(1)
    
    # Load sounds
    sounds = {}
    for name, path in Config.SOUND_PATHS.items():
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(Config.SOUND_VOLUME)
            sounds[name] = sound
            print(f"Loaded sound '{name}' from '{path}'.")
        except pygame.error as e:
            print(f"Error loading sound '{name}' from '{path}': {e}")
            sounds[name] = None  # Assign None for failed loads
    
    # Define key mappings for testing
    # Assign number keys to specific sounds
    sound_keys = {
        pygame.K_1: "game_start",
        pygame.K_2: "day",
        pygame.K_3: "night",
        pygame.K_4: "boat_arrives",
        pygame.K_5: "dino_roar",
        pygame.K_6: "dino_steps",
        pygame.K_7: "game_over",
        pygame.K_8: "player_damage",
        pygame.K_9: "player_move_soft",
        pygame.K_0: "potion_use",
        pygame.K_MINUS: "repellent_trigger",
        pygame.K_EQUALS: "win_game",
        pygame.K_q: "potion_pickup",
    }
    
    # Display instructions
    print("\n--- Sound Test Instructions ---")
    print("Press the following keys to play corresponding sounds:")
    for key, sound_name in sound_keys.items():
        key_name = pygame.key.name(key).upper()
        print(f"  {key_name}: {sound_name}")
    print("Press ESC to exit.\n")
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in sound_keys:
                    sound_name = sound_keys[event.key]
                    sound = sounds.get(sound_name, None)
                    if sound:
                        sound.play()
                        print(f"Playing sound: '{sound_name}'")
                    else:
                        print(f"Sound '{sound_name}' is not loaded and cannot be played.")
        
        # Optional: Fill the screen with a color
        screen.fill((30, 30, 30))
        
        # Optional: Update the display with text instructions
        font = pygame.font.SysFont("Arial", 16)
        y = 10
        for key, sound_name in sound_keys.items():
            key_name = pygame.key.name(key).upper()
            text = font.render(f"Press {key_name} to play '{sound_name}'", True, (255, 255, 255))
            screen.blit(text, (20, y))
            y += 25
        # Render exit instruction
        exit_text = font.render("Press ESC to exit.", True, (255, 0, 0))
        screen.blit(exit_text, (20, y))
        
        pygame.display.flip()
    
    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
