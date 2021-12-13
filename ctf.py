import main_functions

# Starta spelet med python ctf.py --singleplayer
# eller python ctf.py --hot-multiplayer

#----- Main Loop -----#

#-- Control whether the game is running

skip_update = 0
running = True

# Spel-loopen
main_functions.__init__()
while running:

    main_functions.event_handler()
    main_functions.object_update()
    main_functions.physics_update(skip_update)
    main_functions.display_update()

    # Control the game framerate
    main_functions.clock.tick(main_functions.FRAMERATE)
