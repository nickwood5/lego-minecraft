from cmath import pi
from email.mime import base
import enum
from itertools import count, zip_longest
from tkinter import E
from turtle import pos
import anvil, copy, json, uuid
from flask import appcontext_popped
from numpy import empty, sort_complex
from ldr_write import build_model

def print(st):
    None

tile = {
    "1x1_tile": {
        "height": 1,
        "positions": [
            {"x": 0, "z": 0},
        ]
    }
}

f = open('config.json')
data = json.load(f)

f = open('config2.json')
brick_colour_data = json.load(f)

brick_shapes = data["bricks"]

#print(brick_shapes)

plate_sizes = {}
for plate in brick_shapes.keys():
    plate_sizes[plate] = len(brick_shapes[plate]["positions"])
    
#print(plate_sizes)

sorted_plates = {k: v for k, v in sorted(plate_sizes.items(), key=lambda item: item[1], reverse=True)}
sorted_plates = list(sorted_plates.keys())
sorted_plates.append("1x1_tile")

piece_ids = {}
for plate_num in range (0, len(sorted_plates)):
    piece_ids[sorted_plates[plate_num]] = str(plate_num + 1)

blocks = {
    "grass_block": {"type": "block"},
    "oak_log": {"type": "block"},
    "oak_planks": {"type": "block"},
    "birch_planks": {"type": "block"},
    "oak_slab": {"type": "slab"},
    "granite": {"type": "block"},
    "glowstone": {"type": "block"},
    "birch_slab": {"type": "slab"},
    "glass": {"type": "block"},
    "smooth_stone_slab": {"type": "block"},
    "oak_leaves": {"type": "block"}
}

translated_blocks = {
    "grass_block": "dark_green",
    "oak_log": "dark_red",
    "oak_planks": "medium_nougat",
    "birch_planks": "brick_yellow",
    "oak_slab": "medium_nougat_slab",
    "granite": "medium_nougat",
    "glowstone": "flame_yellowish_orange",
    "birch_slab": "brick_yellow_slab",
    "glass": "transparent_white",
    "dirt": "dark_green",
    "smooth_stone_slab": "medium_stone_grey_slab",
    "smooth_stone": "medium_stone_grey",
    "oak_leaves": "bright_yellowish_green"
}

lego_blocks = {
    "dark_green": {"type": "block", "colour": "dark_green"},
    "dark_red": {"type": "block", "colour": "dark_red"},
    "medium_nougat": {"type": "block", "colour": "medium_nougat"},
    "brick_yellow": {"type": "block", "colour": "brick_yellow"},
    "brick_yellow_slab": {"type": "slab", "colour": "brick_yellow"},
    "medium_nougat_slab": {"type": "slab", "colour":"medium_nougat"},
    "flame_yellowish_orange": {"type": "block", "colour": "flame_yellowish_orange"},
    "transparent_white": {"type": "block", "colour": "transparent_white"},
    "sand_yellow": {"type": "block", "colour": "sand_yellow"},
    "sand_yellow_slab": {"type": "block", "colour": "sand_yellow"},
    "medium_stone_grey_slab": {"type": "slab", "colour": "medium_stone_grey"},
    "medium_stone_grey": {"type": "block", "colour": "medium_stone_grey"},
    "bright_yellowish_green": {"type": "block", "colour": "bright_yellowish_green"}
}

use_all = False

if use_all:
    #for block in lego_blocks.keys():
    #    lego_blocks[block]["colour"] = "all_bricks"

    for colour in brick_colour_data.keys():
        brick_colour_data[colour] = brick_colour_data["all_bricks"]


  

def are_blocks_adjacent(block1, block2):
    if (abs(block1["x"] - block2["x"])) == 1 and block1["y"] == block2["y"] and block1["z"] == block2["z"]:
        return True

    if (abs(block1["y"] - block2["y"])) == 1 and block1["x"] == block2["x"] and block1["z"] == block2["z"]:
        return True

    if (abs(block1["z"] - block2["z"])) == 1 and block1["y"] == block2["y"] and block1["x"] == block2["x"]:
        return True

    return False

# Is block1 over block2
def is_block_above(block1, block2):
    if (block1["y"] - block2["y"]) == 1 and block1["x"] == block2["x"] and block1["z"] == block2["z"]:
        return True

    return False

def format_design(chunk):
    model = []
    all_elements = []

    for x in range (0, 12):
        yz_slice = []
        for y in range (-59, -30):
            row = []
            for z in range (0, 12):
                block = chunk.get_block(x, y, z)
                row.append({"id": block.id, "properties": block.properties})
                if block.id not in all_elements:
                    all_elements.append(block.id)
            yz_slice.append(row)
        
        model.append(yz_slice)
    
    return model, all_elements

def create_block_groupings(model):
    present_blocks = {}
    num = 1

    for x in range (0, 12):
        for z in range (0, 12):
            for y in range (1, 20):
                element_id = model[x][y][z]["id"]
                if element_id in translated_blocks.keys():
                    translated_element_id = translated_blocks[element_id]
                    if translated_element_id not in present_blocks.keys():
                        present_blocks[translated_element_id] = []
                    present_blocks[translated_element_id].append({"x": x, "y": y, "z": z, "metadata": lego_blocks[translated_element_id]})

    block_groupings = {}

    for block in present_blocks.keys():
        if block in lego_blocks.keys():
            block_groupings[block] = []

            for block1 in present_blocks[block]:
                block_groupings[block].append([block1])

            present_blocks[block].clear()

            #print(block_groupings[block])


            #print("Present blocks are {}".format(present_blocks[block]))
            
            #print(present_blocks[block])
            ##print(block_groupings["oak_log"])
                

            searching = True

            while searching:
                update = False
                for unsorted_block in present_blocks[block]:
                    if update:
                        break
                    grouped = False
                    for group in block_groupings[block]:
                        if grouped:
                            break
                        for compared_block in group:
                            if are_blocks_adjacent(unsorted_block, compared_block):
                                group.append(unsorted_block)
                                present_blocks[block].remove(unsorted_block)
                                grouped = True
                                update = True
                                break

                if len(present_blocks[block]) == 0 or update == False:
                    searching = False

            searching = True

            while searching:
                update = False
                exit = False
                for group in block_groupings[block]:
                    if exit:
                        break
                    for compared_group in block_groupings[block]:
                        if exit:
                            break
                        if compared_group != group:
                            if exit:
                                break
                            for block1 in compared_group:
                                if exit:
                                    break
                                for block2 in group:
                                    if are_blocks_adjacent(block1, block2):
                                        exit = True
                                        group += compared_group
                                        block_groupings[block].remove(compared_group)
                                        update = True
                                        break        

                if update == False:
                    searching = False

    #print("FIANL PRESENET IS {}".format(present_blocks))
    #print(block_groupings)

    return block_groupings

def get_min_y(block_group):
    min_y = 100
    for block in block_group:
        if block["y"] < min_y:
            min_y = block["y"]

    return min_y

decorations = {
    "dandelion": {}
}


slabs = {
    "oak_slab": {},
    "birch_slab": {}
}

block_ids = {}

for block_index, block in enumerate(lego_blocks.keys()):
    block_ids[block] = str(block_index + 1)


#print(all_elements)

    

# Check for overhanging blocks within all additional groups 

#print(block_groupings.keys())

##print(block_groupings["granite"])

#print("ttt")

def print_layer(layer):
    #print("")
    for row in layer:
        r = ""
        for col in row:
            if col["status"] == "filled":
                r += " X "
            elif col["status"] == "brick_filled":
                r += " " + str(col["id"]) + " "
            else:
                r += " 0 "
        #print(r)
    #print("")

def piece_fits_test(piece, brick_model, y, z, x, brick_colour, brick_below_needed):
    #if z == 10 and x == 2:
        #print("Testing colour {} {}".format(brick_colour, piece))
    #if piece == "4x4_plate":
    #    #print("Checking if {} fits".format(piece))
    all_layers = brick_model["all_layers"]
    piece_data = brick_shapes[piece]

    brick_positions_filled = []

    y_dim = len(all_layers) - 1
    z_dim = len(all_layers[0]) - 1
    x_dim = len(all_layers[0][0]) - 1

    works = True
    brick_below = False
 
    brick_height = piece_data["height"]
    brick_positions_below = []

    for pos in piece_data["positions"]:
        if works == False:
            break

        x_pos = pos["x"]
        z_pos = pos["z"]
        next_x = x + x_pos
        next_z = z + z_pos
        for y_pos in range (0, brick_height):
            
            next_y = y + y_pos

            if next_x > x_dim or next_x < 0 or next_y > y_dim or next_z > z_dim or next_z < 0:
                works = False
                break
            else:
                brick_position = all_layers[next_y][next_z][next_x]
                if brick_position["block"] != "air":
                    if brick_position["needs_brick"]:
                        if brick_position["metadata"]["colour"] == brick_colour:
                            ##print("So far this block works")
                            brick_positions_filled.append({"x": next_x, "y": next_y, "z": next_z})

                            if y_pos == 0:
                                if next_y == 0:
                                    brick_below = True
                                    if y_pos == 0:
                                        brick_positions_below = None
                                else:
                                    below_brick_position = all_layers[next_y - 1][next_z][next_x]
                                    if below_brick_position["needs_brick"]:
                                        brick_below = True

                            """
                            if y_pos == brick_height - 1:
                                if next_y + 1 < len(brick_model["layer_colours"]):
                                    above_brick_positon = all_layers[next_y + 1][next_z][next_x]
                                    if above_brick_positon["needs_brick"]:
                                        brick_below = True
                            """        
                                    

                        else:
                            ##print("wRONG COLOUR")
                            return False, None, None
                    else:
                        ##print("Fail because does not need brick")
                        return False, None, None
                else:
                    ##print("Fail because block is air")
                    return False, None, None

    if brick_below and works:
        return True, brick_positions_below, brick_positions_filled
    else:
        ##print("Fail because there is no brick below")
        return False, None, None

def piece_fits(piece, brick_model, y, z, x, brick_colour, brick_below_needed):
    #if z == 2 and x == 10:
    #    #print("Testing colour {} {}".format(brick_colour, piece))
    #if piece == "4x4_plate":
    #    #print("Checking if {} fits".format(piece))
    all_layers = brick_model["all_layers"]
    piece_data = brick_shapes[piece]

    brick_positions_filled = []

    y_dim = len(all_layers) - 1
    z_dim = len(all_layers[0]) - 1
    x_dim = len(all_layers[0][0]) - 1

    works = True
    brick_below = False
    brick_height = piece_data["height"]
    brick_positions_below = []

    for pos in piece_data["positions"]:
        if works == False:
            break

        x_pos = pos["x"]
        z_pos = pos["z"]
        next_x = x + x_pos
        next_z = z + z_pos
        for y_pos in range (0, brick_height):
            
            next_y = y + y_pos

            if next_x > x_dim or next_x < 0 or next_y > y_dim or next_z > z_dim or next_z < 0:
                works = False
                break
            else:
                brick_position = all_layers[next_y][next_z][next_x]
                if brick_position["block"] != "air":
                    if brick_position["needs_brick"]:
                        if brick_position["metadata"]["colour"] == brick_colour and brick_position["brick_in_place"] == None:
                            ##print("So far this block works")
                            brick_positions_filled.append({"x": next_x, "y": next_y, "z": next_z})

                            if y_pos == 0:
                                if next_y == 0:
                                    brick_below = True
                                    if y_pos == 0:
                                        brick_positions_below = None
                                else:
                                    below_brick_position = all_layers[next_y - 1][next_z][next_x]
                                    if below_brick_position["needs_brick"]:
                                        if brick_below_needed:
                                            if below_brick_position["brick_in_place"] != None:
                                                brick_below = True
                                                if y_pos == 0:
                                                    brick_positions_below.append({"x": next_x, "y": next_y - 1, "z": next_z})
                                        else:
                                            brick_below = True

                            
                            if y_pos == brick_height - 1:
                                if next_y + 1 < len(brick_model["layer_colours"]):
                                    above_brick_positon = all_layers[next_y + 1][next_z][next_x]
                                    if above_brick_positon["needs_brick"]:
                                        if above_brick_positon["brick_in_place"] != None:
                                            brick_below = True  

                        else:
                            
                            return False, None, None
                    else:
               
                        return False, None, None
                else:
                   
                    return False, None, None

    if brick_below and works:
        return True, brick_positions_below, brick_positions_filled
    else:
        return False, None, None

def does_piece_fit(piece, all_layers, row, col):
    layer = all_layers[row]
    piece_data = brick_shapes[piece]
    y_dim = len(layer) - 1
    x_dim = len(layer[0]) - 1
    piece_below = False
    tiles_filled = []
    works = True
    for pos in piece_data["positions"]:
        #print(pos)
        x_pos = pos["x"]
        y_pos = pos["y"]

        next_row = row + y_pos
        next_col = col + x_pos

        #print("Next is {}, {}, y dim is {}, x dim is {}".format(next_row, next_col, y_dim, x_dim))

        if next_row > y_dim or next_row < 0 or next_col > x_dim or next_col < 0:
            #print("Position not in the grid")
            works = False

            break
        else:
            #print("Position is in the grid, checking that tile")
            next_tile = layer[next_row][next_col]
            #print(next_tile)
            if next_tile["status"] == "filled":
                ##print("So far this block works")
                tiles_filled.append({"x": next_col, "y": next_row})
                
                if next_tile["block_below"]:
                    piece_below = True
                
            else:
                #print("This block does not work, remove and try next")
                works = False

                break
    
    if works and piece_below:
        #print("THIS PLATE WORKS: {} at {} {}".format(piece, row, col))
        for tile in tiles_filled:
            layer[tile["y"]][tile["x"]]["status"] = "brick_filled"
            layer[tile["y"]][tile["x"]]["id"] = piece_ids[piece]

        print_layer(layer)
        #print(tiles_filled)
            
            #exit()

def initial_layer_bricks(layer_index, brick_model):
    layer = brick_model[layer_index]
    
    for plate in sorted_plates:
        #print(plate)

        plate_data = brick_shapes[plate]
        for row in range (0, len(layer)):
            r = ""
            for col in range (0, len(layer[row])):
                
                square = layer[row][col]
                if square["status"] == "filled":
                    # Try every brick
                    #for plate in sorted_plates:
                    
                    does_piece_fit(plate, layer, row, col)

                    #exit()
                    r += " 1 "
                else:
                    r += " 0 "
            #print(r)
    
    return layer

def get_group_dimensions(group):
    #print("Formatting group {}".format(group))

    min_x = 100
    min_y = 100
    min_z = 100
    max_x = -1
    max_y = -1
    max_z = -1

    for block in group:
        if block["x"] > max_x:
            max_x = block["x"]
        if block["x"] < min_x:
            min_x = block["x"]

        if block["y"] > max_y:
            max_y = block["y"]
        if block["y"] < min_y:
            min_y = block["y"]

        if block["z"] > max_z:
            max_z = block["z"]
        if block["z"] < min_z:
            min_z = block["z"]

    #print("Min y is {}".format(min_y))
    #print("Max y is {}".format(max_y))

    #print("Min x is {}".format(min_x))
    #print("Max x is {}".format(max_x))

    #print("Min z is {}".format(min_z))
    #print("Max z is {}".format(max_z))
    #for y_height in range (min_y, max_y + 1):
    #    #print("Height {}".format(y_height))
    #exit()

    model = []
    for y in range (min_y, max_y + 1):
        zx_slice = []
        for z in range (min_z, max_z + 1):
            slice = []
            
            for x in range (min_x, max_x + 1):
                slice.append({"status":"empty", "block_above": False, "block_below": False})
            zx_slice.append(slice)
        
        model.append(zx_slice)

    #print("Model height is {}".format(len(model)))
    #print("Model x dim is {}".format(len(model[0])))
    #print("Model z dim is {}".format(len(model[0][0])))

    for block in group:
        #print("Placing block at {} {} {}".format(block["y"] - min_y, block["z"] - min_z, block["x"] - min_x))
        selected_block = model[block["y"] - min_y][block["z"] - min_z ][block["x"] - min_x]
        selected_block["status"] = "filled"
        selected_block["block_above"] = block["block_above"]
        selected_block["block_below"] = block["block_below"]
        selected_block["block_coordinate"] = {"x": block["x"], "y": block["y"], "z": block["z"]}

    
    #print(model)

    brick_model = []

    for slice in model:

        first_layer = False
        for row in slice:
            r = ""
            for col in row:
                col["brick_filled"] = False
                #print(col)

                

                if col["status"] == "filled":
                    r += " 1 "
                    if col["block_coordinate"]["y"] == 1:
                        first_layer = True
                else:
                    r += " 0 "
            #print(r)
        #exit()
        #print("\n")

        #print("Updating mod ")

        #print(slice[0][0])
        
        if first_layer:
            first_slice = copy.deepcopy(slice)
            for row in range (0, len(first_slice)):
                r = ""
                for col in range (0, len(first_slice[row])):
                    ##print(col)
                    
                    first_slice[row][col]["brick_filled"] = False
            
            brick_model.append(first_slice)

        brick_model.append(slice)
        #co = copy.deepcopy(slice)
        #brick_model.append(co)

        #brick_model[-1][0][0]["status"] = "filled"
        

        second_slice = copy.deepcopy(slice)

        for row in range (0, len(second_slice)):
            for col in range (0, len(second_slice[row])):
                ##print(col)
                if second_slice[row][col]["block_above"] == False:
                    second_slice[row][col]["status"] = "empty"
                    #print("Changing status of {} to ".format(col))
        

        brick_model.append(second_slice)
        

    #print("Bricks:")
    new_model = []

    """
    for slice in range (0, len(brick_model)):
        new_layer = initial_layer_bricks(slice, brick_model)
        new_model.append(new_layer)
    """
    
    return brick_model
         

def is_group_valid(block_group, valid_groups):
    for block in block_group:
        if block["y"] == 1:
            #print("Block group is valid because it is at the first layer")
            return True

        done = False
        for valid_group in valid_groups:
            valid_group_blocks = valid_group["blocks"]
            if done:
                break
            for valid_block in valid_group_blocks:
                if is_block_above(valid_block, block) or is_block_above(block, valid_block):
                    return True
    
    return False

def count_filled_coordinates(brick_model, layer_index):
    all_layers = brick_model["all_layers"]
    layer = all_layers[layer_index]
    num_filled = 0
    num_needed = 0 

    positions_filled = []
    positions_unfilled = []
    for row_index, row in enumerate(layer):
        r = ""
        for brick_position_index, brick_position in enumerate(row):
            if brick_position["block"] != "air":
                if brick_position["needs_brick"]:
                    num_needed += 1

                    filled = False
                    brick_position["brick_coordinate"] = {"x": brick_position_index, "y": layer_index, "z": row_index}
                    if brick_position["brick_in_place"] != None:
                        filled = True
                        num_filled += 1
                        positions_filled.append(brick_position)

                    if not filled:
                        positions_unfilled.append(brick_position)
    
    return num_filled, num_needed, positions_filled, positions_unfilled

def print_actual_brick_model(brick_model):
    all_layers = brick_model["all_layers"]
    for layer in all_layers:
        
        print_actual_brick_model_layer(layer)

def print_actual_brick_model_layer(layer):
    ##print("Printing ACTUAL brick model layer")
    layer_blocks = []
    layer_string = ""
    for row in layer:
        r = ""
        for brick_position in row:
            if brick_position["block"] != "air":
                if brick_position["needs_brick"]:
                    if brick_position["brick_in_place"] != None:
                        block_id = piece_ids[brick_position["brick_in_place"]["piece"]]
                        r += " " + block_id + " "
                        ##print("block id for {} is {}".format(brick_position["brick_in_place"]["piece"], block_id))
                        layer_blocks.append(int(block_id))
                    else:
                        r += " X "
                else:
                    r += " 0 "
            else:
                r += " 0 "
        ##print(r)
        layer_string += r + "\n"
    if sum(layer_blocks) != 0:
        print(layer_string)
        print("")
    else:
        print("No bricks")

def print_brick_model_layer(layer):
    print("Printing brick model layer")
    layer_blocks = []
    layer_string = ""
    for row in layer:
        r = ""
        for brick_position in row:
            if brick_position["block"] != "air":
                if brick_position["needs_brick"]:
                    block_id = block_ids[brick_position["block"]]
                    r += " " + block_id + " "
                    layer_blocks.append(int(block_id))
                else:
                    r += " 0 "
            else:
                r += " 0 "
        ##print(r)
        layer_string += r + "\n"
    if sum(layer_blocks) != 0:
        print(layer_string)
        print("")

def print_brick_model(brick_model):
    #print("printing brick model")
    all_layers = brick_model["all_layers"]

    for layer in all_layers:
        layer_blocks = []
        layer_string = ""
        for row in layer:
            r = ""
            for brick_position in row:
                if brick_position["block"] != "air":
                    if brick_position["needs_brick"]:
                        block_id = block_ids[brick_position["block"]]
                        r += " " + block_id + " "
                        layer_blocks.append(int(block_id))
                    else:
                        r += " 0 "
                else:
                    r += " 0 "
            ##print(r)
            layer_string += r + "\n"
        if sum(layer_blocks) != 0:
            print(layer_string)
            print("")

def print_block_model_layer(layer):
    #print("Printing block model layer")

    for row in layer:
        r = ""
        for block in row:
            if block["block"] != "air":
                ##print(block)
                r += " " + block_ids[block["block"]] + " "
            else:
                r += " 0 "
    
        print(r)
    print("")

def print_block_model(block_model):
    print("Printing block model")
    all_layers = block_model["layers"]
    for layer in all_layers:
        for row in layer:
            r = ""
            for block in row:
                if block["block"] != "air":
                    ##print(block)
                    r += " " + block_ids[block["block"]] + " "
                else:
                    r += " 0 "
        
            print(r)
        print("")
    

def create_block_model(block_groupings):
    block_model = {"layers": []}
    block_model_layers = block_model["layers"]

    block_object = {"block": "air", "properties": None}

    all_layers = []
    for y in range (-59, -30):
        layer = []
        for z in range (0, 12):
            row = []
            for x in range (0, 12):
                row.append(copy.deepcopy(block_object))
            layer.append(row)
        block_model_layers.append(layer)
    
    valid_groups = []

    addition_made = True
    while addition_made:
        addition_made = False
        for block_type in block_groupings.keys():
            block_groups = block_groupings[block_type]
            #print("Checking block type {}, {} groups".format(block_type, len(block_groups)))
            if addition_made:
                break

            for block_group_index, block_group in enumerate(block_groups):
                #print("Checking group {}, {} blocks".format(block_group_index, len(block_group)))

                valid_group = is_group_valid(block_group, valid_groups)
                #print(valid_group)
                if valid_group:
                    valid_groups.append({"block": block_type, "blocks": block_group})
                    block_groups.remove(block_group)
                    addition_made = True

                    break
  
    print_block_model(block_model)

    #print(valid_groups)

    for valid_group in valid_groups:
        valid_group_blocks = valid_group["blocks"]
        for block in valid_group_blocks:
            x = block["x"] #- 1
            y = block["y"] - 1
            z = block["z"] #- 1

            block_data = block_model_layers[y][z][x]

            block_data["block"] = valid_group["block"]
            block_data["metadata"] = block["metadata"]
            block_data["block_coordinate"] = {"x": x, "y": y, "z": z}
            #block_data["type"] = valid_group["type"]

    #print(block_ids)

    return block_model

def create_brick_model(block_model):
    brick_model = {}
    brick_model["all_layers"] = []
    brick_model["layer_colours"] = []
    brick_model["tiles_filled"] = {}
    brick_model["coordinates_filled"] = {}
    brick_model["brick_positions"] = []

    print_block_model(block_model)
    all_layers = block_model["layers"]

    #print(all_layers)

    first_layer = copy.deepcopy(all_layers[0])
    #print(first_layer)

    first_layer_colours = dict()
    for row_num, row in enumerate(first_layer):
        for block_num, block in enumerate(row):
            block_id = block["block"]
            if block_id != "air":
                block["needs_brick"] = True
                block["brick_in_place"] = None
                block_colour = block["metadata"]["colour"]

                if block_colour not in first_layer_colours.keys():
                    first_layer_colours[block_colour] = []

                first_layer_colours[block_colour].append({"z": row_num, "x": block_num})

                #first_layer_colours.add(block["metadata"]["colour"])
            else:
                block["needs_brick"] = False
    
    brick_model["all_layers"].append(first_layer)
    brick_model["layer_colours"].append(first_layer_colours)

    for layer in all_layers:
        layer_colours = dict()
        block_found = False
        print_block_model_layer(layer)

        first_new_layer = copy.deepcopy(layer)
        for row_num, row in enumerate(first_new_layer):
            for block_num, block in enumerate(row):
                ##print(block)
                block_id = block["block"]
                if block_id != "air":
                    type = block["metadata"]["type"]
                    if type == "block":
                        block_found = True
                        block_colour = block["metadata"]["colour"]

                        if block_colour not in layer_colours.keys():
                            layer_colours[block_colour] = []

                        layer_colours[block_colour].append({"z": row_num, "x": block_num})

                        #layer_colours.add(block["metadata"]["colour"])
                        block["needs_brick"] = True
                        block["brick_in_place"] = None
                    else:
                        block["needs_brick"] = False
                        block["needs_tile"] = True
                        block_found = True
                else:
                    block["needs_brick"] = False
                

        #print(block)
        #exit()

        if block_found:
            brick_model["layer_colours"].append(layer_colours)
            layer_colours = dict()
            brick_model["all_layers"].append(first_new_layer)
            print_brick_model_layer(first_new_layer)
        
            second_new_layer = copy.deepcopy(layer)
            #print("Start layer")
            for row_num, row in enumerate(second_new_layer):
                for block_num, block in enumerate(row):
                    block_id = block["block"]
                    if block_id != "air":
                        type = block["metadata"]["type"]
                        if type == "block":
                            block_colour = block["metadata"]["colour"]
                            block_coordinate = block["block_coordinate"]
                            x = block_coordinate["x"]
                            above_y = block_coordinate["y"] + 1
                            z = block_coordinate["z"]
                            ##print("{} {} {}".format(x, above_y, z))
                            ##print("Block is {}".format(block))
                            ##print(block_model)
                            block_above = all_layers[above_y][z][x]
                            
                            if block_above["block"] != "air":
                                ##print(block_above)
                                #layer_colours.add(block["metadata"]["colour"])

                                if block_colour not in layer_colours.keys():
                                    layer_colours[block_colour] = []

                                layer_colours[block_colour].append({"z": row_num, "x": block_num})

                                block["needs_brick"] = True
                                block["brick_in_place"] = None
                            
                            else:
                                block["needs_brick"] = False
                                block["needs_tile"] = True
                        else:
                            block["needs_brick"] = False
                    else:
                            block["needs_brick"] = False
                            

            brick_model["all_layers"].append(second_new_layer)
            brick_model["layer_colours"].append(layer_colours)
            print_brick_model_layer(second_new_layer)

    #print(all_layers[0])

    #exit()
    return brick_model
        #exit()

    

    



#print(brick_model["all_layers"][0][10][2])

#print(brick_shapes["1x1_brick"])

#print(piece_fits("1x1_brick", brick_model, 0, 10, 1, "medium_nougat", True))

#def develop_layer(brick_model):


#print(len(brick_model["layer_colours"]))
#print(len(brick_model["all_layers"]))

#print(brick_colour_data)


def sort_dict(dict_array, key):
    return (sorted(dict_array, key=lambda x: x[key], reverse=True))
        

def add_brick_to_model(brick_model, piece_data, brick_colour, update_model):
    
    all_layers = brick_model["all_layers"]
    ##print(all_layers)
    ##print(piece_data)
    positions_filled = piece_data["positions_filled"]
    for position in positions_filled:
        x = position["x"]
        y = position["y"]
        z = position["z"]
        if all_layers[y][z][x]["brick_in_place"] != None:
            return False

    brick_uuid = uuid.uuid4()
    first_position = positions_filled[0]
    x = first_position["x"]
    y = first_position["y"]
    z = first_position["z"]
    brick_model["brick_positions"].append({"x": x, "y": y, "z": z, "id": brick_uuid, "piece_id": piece_data["piece"], "colour": brick_colour})

    if brick_colour not in brick_model["coordinates_filled"].keys():
        brick_model["coordinates_filled"][brick_colour] = []
    for position in positions_filled:
        x = position["x"]
        y = position["y"]
        z = position["z"]

        if update_model:
            all_layers[y][z][x]["brick_in_place"] = {"piece": piece_data["piece"], "uuid": brick_uuid}

            if {"x": x, "z": z} not in brick_model["coordinates_filled"][brick_colour]:
                brick_model["coordinates_filled"][brick_colour].append({"x": x, "z": z})

    ##print("Added {} {}".format(brick_colour, piece_data["piece"]))

    return True

def get_new_overhangs(potential_brick_placements, brick_colour, brick_model):
    new_overhang_positions = []
    new_overhang_sizes = []
    for potential_placement in potential_brick_placements:
        ##print("Potent is {}".format(potential_placement))
        brick_positions = potential_placement["positions_filled"]
    
        new_overhangs_created = 0

        new_filled = []
        for position in brick_positions:
            x = position["x"]
            z = position["z"]

            if brick_colour in brick_model["coordinates_filled"].keys():
                ##print({"x": x, "z": z})
                ##print("New filled is {}, existing overhangs is {}".format(new_filled, brick_model["coordinates_filled"][brick_colour]))
                if {"x": x, "z": z} not in brick_model["coordinates_filled"][brick_colour] and {"x": x, "z": z} not in new_filled:
                    ##print("Creats new overhang")
                    new_overhangs_created += 1
            #else:
            #    new_overhangs_created = 0

            new_filled.append({"x": x, "z": z})
        
        if new_overhangs_created > 0:
            new_overhang_sizes.append(new_overhangs_created)
            new_overhang_positions.append(potential_placement)

        ##print("This position creates {} new overhangs".format(new_overhangs_created))
    
    return new_overhang_positions, new_overhang_sizes




def is_prime_overhang(position, positions_filled, brick_model):
    # Also count the number of adjacent tiles that are not an overhang
    all_layers = brick_model["all_layers"]

    y = position["y"]
    y_under = y - 1
    x = position["x"]
    z = position["z"]

    #print("POS filled are {}".format(positions_filled))

    if all_layers[y_under][z][x]["needs_brick"]:
        if all_layers[y_under][z][x]["brick_in_place"] != None:
            #print("Fail here")
            return False


    #print("We got here")
    z_above = z - 1
    #print("z_abo is {}".format(z_above))
    if z_above >= 0:
        #print("Checking a {}".format({"x": x, "y": y, "z": z_above}))
        if {"x": x, "y": y, "z": z_above} in positions_filled:
            #print("Checking a {}".format({"x": x, "y": y, "z": z_above}))
            if all_layers[y_under][z_above][x]["needs_brick"]:
                if all_layers[y_under][z_above][x]["brick_in_place"] != None:
                    return False

        if all_layers[y][z_above][x]["needs_brick"]:
            if all_layers[y][z_above][x]["brick_in_place"] != None:
                if all_layers[y_under][z_above][x]["needs_brick"]:
                    if all_layers[y_under][z_above][x]["brick_in_place"] != None:
                        return False
    
    z_below = z + 1
    if z_below < len(all_layers[y_under]):
        if {"x": x, "y": y, "z": z_below} in positions_filled:
            if all_layers[y_under][z_below][x]["needs_brick"]:
                if all_layers[y_under][z_below][x]["brick_in_place"] != None:
                    return False

        if all_layers[y][z_below][x]["needs_brick"]:
            if all_layers[y][z_below][x]["brick_in_place"] != None:
                if all_layers[y_under][z_below][x]["needs_brick"]:
                    if all_layers[y_under][z_below][x]["brick_in_place"] != None:
                        return False

    x_left = x - 1
    if x_left >= 0:
        if {"x": x_left, "y": y, "z": z} in positions_filled:
            if all_layers[y_under][z][x_left]["needs_brick"]:
                if all_layers[y_under][z][x_left]["brick_in_place"] != None:
                    return False
        if all_layers[y][z][x_left]["needs_brick"]:
            if all_layers[y][z][x_left]["brick_in_place"] != None:
                if all_layers[y_under][z][x_left]["needs_brick"]:
                    if all_layers[y_under][z][x_left]["brick_in_place"] != None:
                        return False

    x_right = x + 1
    if x_right < len(all_layers[y_under][z]):
        if {"x": x_right, "y": y, "z": z} in positions_filled:
            if all_layers[y_under][z][x_right]["needs_brick"]:
                if all_layers[y_under][z][x_right]["brick_in_place"] != None:
                    return False
        if all_layers[y][z][x_right]["needs_brick"]:
            if all_layers[y][z][x_right]["brick_in_place"] != None:
                if all_layers[y_under][z][x_right]["needs_brick"]:
                    if all_layers[y_under][z][x_right]["brick_in_place"] != None:
                        return False
    
    #print("Hooo")
    return True

def get_overhang_stats(positions_filled, brick_model, layer_index):
    if layer_index == 0:
        return 0

    all_layers = brick_model["all_layers"]

    num_overhangs = 0
    num_below = 0

    num_prime_overhangs = 0

    for position in positions_filled:

        #if is_prime_overhang(position, positions_filled, brick_model):
        #    num_prime_overhangs += 1
        
        y = position["y"] - 1

        if y == layer_index - 1:

            x = position["x"]
            z = position["z"]

            if all_layers[y][z][x]["needs_brick"]:
                if all_layers[y][z][x]["brick_in_place"] == None:
                    num_overhangs += 1
                else:
                    num_below += 1
            else:
                num_overhangs += 1
    
    stat = num_overhangs - num_below
    ##print(num_overhangs, num_below)

    ##print("Brick {} has overhang stat {}".format(positions_filled, num_prime_overhangs))

    return stat





def test_out_layer(brick_model, filled_coordinates_list, brick_colour_data, layer_index, brick_colour):
    brick_model = copy.deepcopy(brick_model)

    all_layers = brick_model["all_layers"]

    if len(brick_model["layer_colours"]) <= layer_index:
        return 0

    layer_colours = brick_model["layer_colours"][layer_index]

    bricks_available = brick_colour_data[brick_colour]
    colour_positions = layer_colours[brick_colour]
    coordinates_filled_by_brick = 0

    for coordinate in filled_coordinates_list:
        x = coordinate["x"]
        y = coordinate["y"]
        z = coordinate["z"]

        all_layers[y][z][x]["needs_brick"] = False
        if y == layer_index:
            coordinates_filled_by_brick += 1

        if y == layer_index:
            modified_coordinate = {"x": x, "z": z}
            if modified_coordinate in colour_positions:
                colour_positions.remove(modified_coordinate)

    potential_brick_placements = []

    for position in colour_positions:
        

        for brick in bricks_available:
            brick_data = brick_shapes[brick]

            if brick_data["height"] == 1:

                z = position["z"]
                x = position["x"]

                fits, positions_below, positions_filled = piece_fits_test(brick, brick_model, layer_index, z, x, brick_colour, False)

                if fits:
                    piece_size = len(brick_data["positions"]) * brick_data["height"]
                    overhang_stat = get_overhang_stats(positions_filled, brick_model, layer_index)
                    potential_brick_placements.append({"positions_filled": positions_filled, "brick_positions_under": positions_below, "piece": brick, "piece_size": piece_size, "overhang_stat": overhang_stat})

    potential_brick_placements = sort_dict(potential_brick_placements, "overhang_stat")

    for p in potential_brick_placements:
        added = add_brick_to_model(brick_model, p, brick_colour, True)

    num_filled, num_needed, positions_filled, positions_unfilled = count_filled_coordinates(brick_model, layer_index) + coordinates_filled_by_brick

    return num_filled


def get_piece_data(brick_model, x, y, z, colour):
    all_layers = brick_model["all_layers"]
    target_position = all_layers[y][z][x]
    if target_position["needs_brick"]:
        if target_position["brick_in_place"] != None:
            print(target_position)
            if target_position["metadata"]["colour"] == colour:
                brick_in_place = target_position["brick_in_place"]
                #print(brick_in_place)
                piece_id = brick_in_place["piece"]
                piece_uuid = brick_in_place["uuid"]
                piece_data = {"piece_id": piece_id, "piece_uuid": piece_uuid}

                return piece_data

    return None

def get_adjacent_pieces(brick_model, position):
    #print(position)
    brick_coordinate = position["brick_coordinate"]
    colour = position["metadata"]["colour"]
    all_layers = brick_model["all_layers"]
    x = brick_coordinate["x"]
    y = brick_coordinate["y"]
    z = brick_coordinate["z"]

    adjacent_pieces = []

    ##print("We got here")
    z_above = z - 1
    ##print("z_abo is {}".format(z_above))
    if z_above >= 0:
        piece_above = get_piece_data(brick_model, x, y, z_above, colour)
        if piece_above != None:
            adjacent_pieces.append(piece_above)
    
    z_below = z + 1
    if z_below < len(all_layers[y]):
        piece_below = get_piece_data(brick_model, x, y, z_below, colour)
        if piece_below != None:
            adjacent_pieces.append(piece_below)

    x_left = x - 1
    if x_left >= 0:
        piece_left = get_piece_data(brick_model, x_left, y, z, colour)
        if piece_left != None:  
            adjacent_pieces.append(piece_left)

    x_right = x + 1
    if x_right < len(all_layers[y][z]):
        piece_right = get_piece_data(brick_model, x_right, y, z, colour)
        if piece_right != None:
            adjacent_pieces.append(piece_right)

    return adjacent_pieces

def remove_piece_from_model(brick_model, piece_uuid):
    brick_model = copy.deepcopy(brick_model)

    brick_positions = brick_model["brick_positions"]
    #print("RED {}".format(brick_positions))
    for position in brick_positions:
        if position["id"] == piece_uuid:
            brick_positions.remove(position)
            break

    #.remove(piece_uuid)
    all_layers = brick_model["all_layers"]
    for layer in all_layers:
        for row in layer:
            for piece_position in row:
                if piece_position["needs_brick"]:
                    brick_in_place = piece_position["brick_in_place"]
                    if brick_in_place != None:
                        if brick_in_place["uuid"] == piece_uuid:
                            #print("Removing piece")
                            piece_position["brick_in_place"] = None

    return brick_model


def build2(brick_model, brick_colour_data, layer_index, brick_colour, filled_coordinates_list):

    if len(brick_model["layer_colours"]) > layer_index:
        print("")
    else:
        return 0

    layer_colours = brick_model["layer_colours"][layer_index]

    bricks_available = brick_colour_data[brick_colour]
    colour_positions = layer_colours[brick_colour]

    potential_brick_placements = []

    #print("colour_positions are {}".format(colour_positions))

    for position in colour_positions:
        z = position["z"]
        x = position["x"]
        
        for brick in bricks_available:
            brick_data = brick_shapes[brick]
            #if brick_data["height"] == 1:

            fits, positions_below, positions_filled = piece_fits_test(brick, brick_model, layer_index, z, x, brick_colour, False)

            fails = False
            if positions_filled != None:
                for filled in positions_filled:
                    if filled in filled_coordinates_list:
                        
                        fails = True
                        break
            if fails:
                continue

            if fits:
                piece_size = len(brick_data["positions"]) * brick_data["height"]
                overhang_stat = get_overhang_stats(positions_filled, brick_model, layer_index)
                if overhang_stat == -len(brick_data["positions"]):
                    overhang_stat = 0
                potential_brick_placements.append({"positions_filled": positions_filled, "brick_positions_under": positions_below, "piece": brick, "piece_size": piece_size, "overhang_stat": overhang_stat})

    #potential_brick_placements = sort_dict(potential_brick_placements, "overhang_stat")

    potential_brick_placements = sorted(potential_brick_placements, key = lambda x: (x["overhang_stat"], x["piece_size"]), reverse=True)
    ##print("PRIME PLACEMENTS ARE {}".format(potential_brick_placements))

    all_positions_filled = []
    for p in potential_brick_placements:
        positions_filled = p["positions_filled"]

        valid = True
        for position in positions_filled:
            if position in all_positions_filled:
                valid = False
                break

        if not valid:
            continue
        added = add_brick_to_model(brick_model, p, brick_colour, True)

        if added:
            all_positions_filled += positions_filled
    
    print_actual_brick_model_layer(brick_model["all_layers"][layer_index])

    

    

def build(brick_model, brick_colour_data, layer_index, brick_colour):
    bricks_added = 0
    print("Alpha build layer {}, colour {}".format(layer_index, brick_colour))

    if len(brick_model["layer_colours"]) <= layer_index:
        print("Exit because there are no bricks to place")
        return 0

    layer_colours = brick_model["layer_colours"][layer_index]
    print(layer_colours)
    print(brick_colour_data)

    bricks_available = brick_colour_data[brick_colour]
    colour_positions = layer_colours[brick_colour]
    print(bricks_available)

    potential_brick_placements = []

    for position in colour_positions:
        for brick in bricks_available:
            brick_data = brick_shapes[brick]
            #if brick_data["height"] == 1:
            z = position["z"]
            x = position["x"]


            print("Testing {}".format(brick))
            fits, positions_below, positions_filled = piece_fits(brick, brick_model, layer_index, z, x, brick_colour, True)

            if fits:
                print("Fits")
                piece_size = len(brick_data["positions"]) * brick_data["height"]
                overhang_stat = get_overhang_stats(positions_filled, brick_model, layer_index)
                if overhang_stat == -len(brick_data["positions"]):
                    overhang_stat = 0
                potential_brick_placements.append({"positions_filled": positions_filled, "brick_positions_under": positions_below, "piece": brick, "piece_size": piece_size, "overhang_stat": overhang_stat})
            else:
                print("Does not fit")
    #potential_brick_placements = sort_dict(potential_brick_placements, "overhang_stat")

    for p in potential_brick_placements:
        print(p)

    potential_brick_placements = sorted(potential_brick_placements, key = lambda x: (x["overhang_stat"], x["piece_size"]), reverse=True)
    print("The alpha placements for layer {} are {}\n".format(layer_index, potential_brick_placements))


    
    #print("Potential placements are {}".format(potential_brick_placements))

    all_positions_filled = []

    for p in potential_brick_placements:
        print("Analyze placement {}".format(p))
        
        positions_filled = p["positions_filled"]

        valid = True
        for position in positions_filled:
            if position in all_positions_filled:
                valid = False
                break

        if not valid:
            continue


        piece_id = p["piece"]
        piece_info = brick_shapes[piece_id]
        #print("PIECE INFO IS {}".format(piece_info))
        piece_height = piece_info["height"]

        #reduces_build_quality = False

        if piece_height > 1:
            reduces_build_quality = False
            for y in range(layer_index + 1, layer_index + piece_height):
                without_brick = test_build_layer(brick_model, brick_colour_data, y, [])
                print("layer {}: Num without is {}".format(layer_index, without_brick))
                with_brick = test_build_layer(brick_model, brick_colour_data, y, positions_filled)
                print("layer {}: Num with is {}".format(layer_index, with_brick))

                if with_brick < without_brick:
                    #print("bad at {}".format(y))
                    reduces_build_quality = True
                    break

            if reduces_build_quality == False:
                print("Try to add {}".format(p))
                added = add_brick_to_model(brick_model, p, brick_colour, True)
                all_positions_filled += positions_filled
                print_actual_brick_model(brick_model)
                print(added)
                if added:
                    print("Added the brick {} at coordinates {}".format(p["piece"], p["positions_filled"]))
                    bricks_added += 1
            else:
                print("Skip adding piece {}".format(p))
        else:
            added = add_brick_to_model(brick_model, p, brick_colour, True)
            all_positions_filled += positions_filled
            print("Try to add {}: {}".format(p, added))
            if added:
                print("Added the brick {} at coordinates {}".format(p["piece"], p["positions_filled"]))
                bricks_added += 1

    return bricks_added

    




def build_first_layer(brick_colour, potential_brick_placements, brick_model, layer_index):
    potential_brick_placements = sort_dict(potential_brick_placements, "piece_size")
    layer = brick_model["all_layers"][layer_index]
    layer_colours = brick_model["layer_colours"][layer_index]
    colour_positions = layer_colours[brick_colour]

    total_num_fills = len(colour_positions)
    num_filled = 0

    #print("posiutuibs are {}".format(colour_positions))
    # check if placing a block in any of these positions will cause a decrease in the number of potential overhangs at any layers it passes through
    for potential_placement in potential_brick_placements:
        # if height > 1
            # Do a test brick placement of bricks at each additional layer, with and without that brick placed
            # if having the brick placed causes the number of filled coordinates in any of the layers to decrease, reject this placement
        piece_id = potential_placement["piece"]
        piece_positions = potential_placement["positions_filled"]

        #print(piece_id)
        piece_data = brick_shapes[piece_id]
        #print(piece_data)
        piece_height = piece_data["height"]

        reduces_build_quality = False
        for y in range(layer_index, layer_index + piece_height):
            #print("Testing out piece {} at y {}".format(piece_id, y))
            without_brick = test_out_layer(brick_model, [], brick_colour_data, y, brick_colour)
            with_brick = test_out_layer(brick_model, piece_positions, brick_colour_data, y, brick_colour)
            #print("piece {} at y {} allows for {} fills, without {}".format(piece_id, y, with_brick, without_brick))

            if with_brick < without_brick:
                #print("bad at {}".format(y))
                reduces_build_quality = True
                break
        
        if reduces_build_quality == False:
            added = add_brick_to_model(brick_model, potential_placement, brick_colour, True)
            if added:
                piece_id = potential_placement["piece"]
                piece_data = brick_shapes[piece_id]
                piece_positions = piece_data["positions"]
                num_filled += len(piece_positions)

                if num_filled == total_num_fills:
                    #print("Exit early")
                    return

    # Maybe process after?

    #print(piece_ids)
    #print("stopping")
    #exit()
    ##print("stopping")

def test_build_layer(brick_model, brick_colour_data, layer_index, filled_coordinates_list):
    if len(brick_model["layer_colours"]) <= layer_index:
        return 0
    brick_model = copy.deepcopy(brick_model)
    #print("Testing layer {} excluding positions {}".format(layer_index, filled_coordinates_list))
    #print_actual_brick_model_layer(brick_model["all_layers"][layer_index])
    
    num_already_filled = 0
    for coordinate in filled_coordinates_list:
        if coordinate["y"] == layer_index:
            num_already_filled += 1


    all_layers = brick_model["all_layers"]
    layer_colours = brick_model["layer_colours"][layer_index]

    for brick_colour in layer_colours.keys():
        build2(brick_model, brick_colour_data, layer_index, brick_colour, filled_coordinates_list)
        #build_first_layer(brick_colour, potential_brick_placements, brick_model, layer_index)

    print_actual_brick_model_layer(all_layers[layer_index])
    num_filled, num_needed, positions_filled, positions_unfilled = count_filled_coordinates(brick_model, layer_index)

    return num_filled + num_already_filled

    
def rebuild_layer_up(brick_model, brick_colour_data, layer_index, banned_pieces):
    #print("ReBuilding layer {} wit banned pieces {}".format(layer_index, banned_pieces))
    brick_colour_data = copy.deepcopy(brick_colour_data)
    print_actual_brick_model_layer(brick_model["all_layers"][layer_index])
    copy_model = copy.deepcopy(brick_model)

    all_layers = brick_model["all_layers"]
    layer = all_layers[layer_index]
    layer_colours = brick_model["layer_colours"][layer_index]

    for brick_colour in layer_colours.keys():
        bricks_available = brick_colour_data[brick_colour]
        pieces_to_remove = []
        for brick in bricks_available:
            if brick in banned_pieces:
                pieces_to_remove.append(brick)

        for removed_piece in pieces_to_remove:
            bricks_available.remove(removed_piece)

        colour_positions = layer_colours[brick_colour]

        potential_brick_placements = []
        

        for position in colour_positions:
            z = position["z"]
            x = position["x"]

            for brick in bricks_available:
                brick_data = brick_shapes[brick]
                fits, positions_below, positions_filled = piece_fits(brick, brick_model, layer_index, z, x, brick_colour, True)
                if fits:
                    piece_size = len(brick_data["positions"]) * brick_data["height"]
                    potential_brick_placements.append({"positions_filled": positions_filled, "brick_positions_under": positions_below, "piece": brick, "piece_size": piece_size})
        build(brick_model, brick_colour_data, layer_index, brick_colour)
        #build_first_layer(brick_colour, potential_brick_placements, brick_model, layer_index)

    num_filled, num_needed, positions_filled, positions_unfilled = count_filled_coordinates(brick_model, layer_index)

    print_actual_brick_model_layer(brick_model["all_layers"][layer_index])
    #print("Rebuilding layer results in {} filled {} needed".format(num_filled, num_needed))
    

def build_layer_up(brick_model, brick_colour_data, layer_index):
    total_bricks_added = 0
    print("Start building layer {}, model is currently:".format(layer_index))
    print_actual_brick_model(brick_model)

    all_layers = brick_model["all_layers"]
    layer = all_layers[layer_index]
    layer_colours = brick_model["layer_colours"][layer_index]

    for brick_colour in layer_colours.keys():
        bricks_added = build(brick_model, brick_colour_data, layer_index, brick_colour)
        total_bricks_added += bricks_added

    num_filled, num_needed, positions_filled, positions_unfilled = count_filled_coordinates(brick_model, layer_index)

    print("PRINTING THE BRICK LAYER FOR {}".format(layer_index))
    print_actual_brick_model_layer(brick_model["all_layers"][layer_index])
    #print("{} filled {} needed".format(num_filled, num_needed))

    if num_filled == num_needed:
        return brick_model, total_bricks_added

    if num_filled < num_needed:
        pieces_to_test = dict()

        #print("Attempt to reconstruct layer")
        for position in positions_unfilled:
            #print(position)
            adjacent_pieces = get_adjacent_pieces(brick_model, position)
            #print("Adjacent pieces are {}".format(adjacent_pieces))
            for piece in adjacent_pieces:

                piece_uuid = piece["piece_uuid"]
                pieces_to_test[piece_uuid] = piece["piece_id"]
                
        if len(pieces_to_test.keys()) == 0:
            return brick_model, total_bricks_added
        #print(pieces_to_test)

        for piece in pieces_to_test.keys():
            #print(piece)
            #print("Generate a new model by removing {}: {}".format(piece, pieces_to_test[piece]))       
            new_model = remove_piece_from_model(brick_model, piece)
            print_actual_brick_model(new_model)

            #print("Now generate the layer again excluding {} pieces".format(pieces_to_test[piece]))

            excluded_piece = pieces_to_test[piece]

            rebuild_layer_up(new_model, brick_colour_data, layer_index, [excluded_piece])

            new_num_filled, new_num_needed, new_positions_filled, new_positions_unfilled = count_filled_coordinates(new_model, layer_index)
            #print("Rebuilding the layer allows for {} / {} position".format(new_num_filled, new_num_needed))

            if new_num_filled == new_num_needed:
                return new_model, total_bricks_added

            print_actual_brick_model(new_model)

    return brick_model, total_bricks_added


def is_brick_below(brick_model, y, z, x):
    all_layers = brick_model["all_layers"]
    y_below = y - 1
    if y_below <= 0:
        return True
    else:
        brick_position_below = all_layers[y_below][z][x]
        if brick_position_below["needs_brick"]:
            if brick_position_below["brick_in_place"] != None:
                return True

    return False


def create_layer_1_bricks(model, brick_model):

    for x in range (0, 12):
        for z in range (0, 12):
            element_id = model[x][0][z]["id"]
            above_element_id = model[x][1][z]["id"]


            brick_uuid = uuid.uuid4()
            if element_id in translated_blocks.keys():
                translated_element_id = translated_blocks[element_id]
                translated_lego_colour = lego_blocks[translated_element_id]
                if above_element_id == "air":
                    brick_model["brick_positions"].append({"x": x, "y": 0, "z": z, "id": brick_uuid, "piece_id": "1x1_tile", "colour": translated_lego_colour["colour"]})
            else:
                if above_element_id == "air":
                    brick_model["brick_positions"].append({"x": x, "y": 0, "z": z, "id": brick_uuid, "piece_id": "1x1_tile", "colour": "flame_yellowish_orange"})



def generate_lego_model(file_name):
    region = anvil.Region.from_file(file_name + ".mca")
    chunk = anvil.Chunk.from_region(region, 1, 30)

    model, all_elements = format_design(chunk)

    block_groupings = create_block_groupings(model)

    # Check the overhanging blocks within each individual group
    for block_type in block_groupings.keys():
        for group in block_groupings[block_type]:
            for block in group:
                for compared_block in group:
                    if block != compared_block:
                        if is_block_above(block, compared_block):
                            compared_block["block_above"] = True
                            block["block_below"] = True

            for compared_block_type in block_groupings.keys():
                for compared_group in block_groupings[compared_block_type]:
                    if compared_group != group:
                        for block in group:
                            for compared_block in compared_group:
                                if is_block_above(block, compared_block):
                                    compared_block["block_above"] = True
                                    block["block_below"] = True

    # Check overhanging blocks within every other group

    for block_type in block_groupings.keys():
        for group in block_groupings[block_type]:
            for block in group:
                if "block_above" not in block.keys():
                    block["block_above"] = False
                if "block_below" not in block.keys():

                    block["block_below"] = False



    block_model = create_block_model(block_groupings)

    print_block_model(block_model)

    brick_model = create_brick_model(block_model)

    #print_brick_model(brick_model#print(block_ids)

    print_brick_model(brick_model)


    total_bricks_added = 1
    while total_bricks_added > 0:
        total_bricks_added = 0
        for layer in range (0, 25):
            print(brick_model)
            print(brick_model["layer_colours"])
            if len(brick_model["layer_colours"]) > layer:
                #print("Access layer {}".format(layer))
                #print(brick_model["layer_colours"][layer])
                brick_model, bricks_added = build_layer_up(brick_model, brick_colour_data, layer)
                total_bricks_added += bricks_added
            #    #print(brick_model["layer_colours"][layer])

    create_layer_1_bricks(model, brick_model)


    if True:
        for y_index, y in enumerate(brick_model["all_layers"]):
            for z_index, z in enumerate(y):
                for x_index, x in enumerate(z):
                    if "needs_tile" in x.keys():
                        if is_brick_below(brick_model, y_index, z_index, x_index):
                            brick_uuid= uuid.uuid4()
                            brick_model["brick_positions"].append({"x": x_index, "y": y_index, "z": z_index, "id": brick_uuid, "piece_id": "1x1_tile", "colour": x["metadata"]["colour"]})
                            brick_model["all_layers"][y_index][z_index][x_index]["brick_in_place"] = {"piece": "1x1_tile", "uuid": brick_uuid}

    print_actual_brick_model(brick_model)
    build_model(brick_model, file_name)

#generate_lego_model("r.0.-1")