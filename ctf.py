""" Starting file """
import main_functions

# Start the game with python ctf.py
# args: --singleplayer, --hot-multiplayer, --time-condition, --score-condition, --rounds-condition

#----- Main Loop -----#

main_functions.__init__()
while True:

    main_functions.event_handler()
    main_functions.object_update()
    main_functions.physics_update(0)
    main_functions.display_update()

    # Control the game framerate
    main_functions.clock.tick(main_functions.FRAMERATE)
