with open("data/maps/map0.txt") as map_choice:
    lines = map_choice.read().replace(" ", "").replace("\n", "").split("[[")
print(lines)