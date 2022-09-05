import json, os
from uuid import uuid4

f = open('config3.json')
colour_codes = json.load(f)

def generic_brick(length, width, piece_code, x, y, z, colour, is_vertical):
    z_brick = (length * 10) + (z * 20) 
    y_brick = -24 + (y * -8)
    x_brick = (width * 10) + (x * 20)

    if is_vertical:
        string = "1 {} {} {} {} 1 0 0 0 1 0 0 0 1 {}.DAT".format(colour, z_brick, y_brick, x_brick, piece_code)
    else:
        string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 {}.DAT".format(colour, z_brick, y_brick, x_brick, piece_code)
    print(string)

    return string

def generic_plate(length, width, piece_code, x, y, z, colour, is_vertical):
    z_brick = (length * 10) + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = (width * 10) + (x * 20)

    if is_vertical:
        string = "1 {} {} {} {} 1 0 0 0 1 0 0 0 1 {}.DAT".format(colour, z_brick, y_brick, x_brick, piece_code)
    else:
        string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 {}.DAT".format(colour, z_brick, y_brick, x_brick, piece_code)
    print(string)

    return string

def tile_1x1(x, y, z, colour):
    return generic_plate(1, 1, "3070b", x, y, z, colour, False)

def plate_1x1(x, y, z, colour):
    return generic_plate(1, 1, 3024, x, y, z, colour, False)

def plate_1x2_horizontal(x, y, z, colour):
    return generic_plate(1, 2, 3023, x, y, z, colour, False)

def plate_2x3_horizontal(x, y, z, colour):
    return generic_plate(2, 3, 3021, x, y, z, colour, False)

def plate_2x3_vertical(x, y, z, colour):
    return generic_plate(3, 2, 3021, x, y, z, colour, True)

def plate_1x3_vertical(x, y, z, colour):
    return generic_plate(3, 1, 3623, x, y, z, colour, True)

def brick_2x4_vertical(x, y, z, colour):
    return generic_brick(4, 2, 3001, x, y, z, colour, True)

def brick_2x4_horizontal(x, y, z, colour):
    return generic_brick(2, 4, 3001, x, y, z, colour, False)

def brick_2x2(x, y, z, colour):
    return generic_brick(2, 2, 3003, x, y, z, colour, False)

def plate_1x2_vertical(x, y, z, colour):
    return generic_plate(2, 1, 3023, x, y, z, colour, True)

def plate_1x5_vertical(x, y, z, colour):
    return generic_plate(5, 1, 78329, x, y, z, colour, True)

def plate_1x5_horizontal(x, y, z, colour):
    return generic_plate(1, 5, 78329, x, y, z, colour, False)



def brick_1x1(x, y, z, colour):
    z_brick = 10 + (z * 20) 
    y_brick = -24 + (y * -8)
    x_brick = 10 + (x * 20)



    #print("a")
    string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 3005.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

#brick_1x1(1, 2, 3, "Rrr")

def plate_4x4(x, y, z, colour):
    z_brick = 40 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 40 + (x * 20)

    string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 3031.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

def plate_2x6_horizontal(x, y, z, colour):
    z_brick = 20 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 60 + (x * 20)



    #print("a")
    string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 3795.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

def plate_2x2(x, y, z, colour):
    z_brick = 20 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 20 + (x * 20)

    string = "1 {} {} {} {} 1 0 0 0 1 0 0 0 1 3022.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

def plate_2x4_vertical(x, y, z, colour):
    z_brick = 40 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 20 + (x * 20)



    #print("a")
    string = "1 {} {} {} {} 1 0 0 0 1 0 0 0 1 3020.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

def plate_2x4_horizontal(x, y, z, colour):
    z_brick = 20 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 40 + (x * 20)

    string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 3020.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

def plate_1x4_vertical(x, y, z, colour):
    z_brick = 40 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 10 + (x * 20)


    #print("a")
    string = "1 {} {} {} {} 1 0 0 0 1 0 0 0 1 3710.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string



def plate_1x4_horizontal(x, y, z, colour):
    z_brick = 10 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 40 + (x * 20)


    #print("a")
    string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 3710.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

def plate_1x3_horizontal(x, y, z, colour):
    z_brick = 10 + (z * 20) 
    y_brick = -8 + (y * -8)
    x_brick = 30 + (x * 20)


    string = "1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 3623.DAT".format(colour, z_brick, y_brick, x_brick)
    print(string)
    return string

lookup = {
    "1x1_brick": brick_1x1,
    "4x4_plate": plate_4x4,
    "2x6_plate_horizontal": plate_2x6_horizontal,
    "2x4_plate_vertical": plate_2x4_vertical,
    "1x4_plate_vertical": plate_1x4_vertical,
    "1x4_plate_horizontal": plate_1x4_horizontal,
    "1x3_plate_horizontal": plate_1x3_horizontal,
    "2x4_plate_horizontal": plate_2x4_horizontal,
    "2x2_plate": plate_2x2,
    "1x2_plate_vertical": plate_1x2_vertical,
    "2x2_brick": brick_2x2,
    "1x2_plate_horizontal": plate_1x2_horizontal,
    "1x1_plate": plate_1x1,
    "1x3_plate_vertical": plate_1x3_vertical,
    "2x3_plate_vertical": plate_2x3_vertical,
    "2x3_plate_horizontal": plate_2x3_horizontal,
    "2x4_brick_horizontal": brick_2x4_horizontal,
    "2x4_brick_vertical": brick_2x4_vertical,
    "1x1_tile": tile_1x1,
    "1x5_plate_vertical": plate_1x5_vertical,
    "1x5_plate_horizontal": plate_1x5_horizontal
}


local = True
UPLOAD_FOLDER = '/home/nickwood5/lego_minecraft/generated_models'

def build_model(brick_model, file_name):
    bricks = brick_model["brick_positions"]

    if local:

        f = open("generated_models/" + file_name + ".ldr", "w")
    else:
        file_path = os.path.join(UPLOAD_FOLDER, file_name + ".ldr")
        f = open(file_path, "w")
    for brick in bricks:
        piece_id = brick["piece_id"]
        piece_colour = brick["colour"]
        colour_id = colour_codes[piece_colour]
        x = brick["x"]
        y = brick["y"]
        z = brick["z"]
        
        builder_function = lookup[piece_id]
        line = builder_function(x=x, y=y, z=z, colour=colour_id)    
        f.write(line)
        f.write("\n")

    f.close()

