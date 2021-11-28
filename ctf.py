import main_functions

# Starta spelet med python ctf.py --singleplayer
# eller python ctf.py --hot-multiplayer

#----- Main Loop -----#

#-- Control whether the game is running
running = True
skip_update = 0

main_functions.screen.blit(main_functions.images.welcome,(50,50)) # Under konstruktion
main_functions.pygame.display.flip()

# Spel-loopen
while running:

    main_functions.event_handler(running)
    main_functions.ai_decide()
    main_functions.physics_update(skip_update)
    main_functions.object_update()
    main_functions.display_update()

    # Control the game framerate
    main_functions.clock.tick(main_functions.FRAMERATE)
