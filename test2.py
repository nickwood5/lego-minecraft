import anvil

def are_blocks_adjacent(block1, block2):
    if (abs(block1["x"] - block2["x"])) == 1 and block1["y"] == block2["y"] and block1["z"] == block2["z"]:
        return True

    if (abs(block1["y"] - block2["y"])) == 1 and block1["x"] == block2["x"] and block1["z"] == block2["z"]:
        return True

    if (abs(block1["z"] - block2["z"])) == 1 and block1["y"] == block2["y"] and block1["x"] == block2["x"]:
        return True

    return False

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

def create_block_groupings(blocks, model):
    present_blocks = {}

    for x in range (0, 12):
        for z in range (0, 12):
            for y in range (1, 20):
                element_id = model[x][y][z]["id"]
                if element_id in blocks.keys():
                    if element_id not in present_blocks.keys():
                        present_blocks[element_id] = []
                    present_blocks[element_id].append({"x": x, "y": y, "z": z})

    block_groupings = {}

    for block in present_blocks.keys():
        if block in blocks.keys():
            block_groupings[block] = []


            stop = False
            block_num = 1
            update = False
            while len(present_blocks[block]) > 0 and stop == False:
                if (block_num + 1) > len(present_blocks[block]) or block_num > len(present_blocks[block]):
                    stop = True

                if stop == False:

                    block1 = present_blocks[block][block_num]
                    block2 = present_blocks[block][block_num - 1]

                    if are_blocks_adjacent(block1, block2):
                        block_groupings[block].append([block1, block2])
                        present_blocks[block].remove(block1)
                        present_blocks[block].remove(block2)
                        update = True

                    block_num += 1

                    if update == False:
                        stop = True
                

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

    return block_groupings


decorations = {
    "dandelion": {}
}

blocks = {
    "grass_block": {},
    "oak_log": {},
    "oak_planks": {},
    "birch_planks": {},
    "oak_slab": {},
    "granite": {}
}

region = anvil.Region.from_file('r.0.-1.mca')
chunk = anvil.Chunk.from_region(region, 1, 30)

model, all_elements = format_design(chunk)
print(all_elements)

block_groupings = create_block_groupings(blocks, model)


# Check the overhanging blocks within each individual group
for block_type in block_groupings.keys():
    for group in block_groupings[block_type]:
        for block in group:
            for compared_block in group:
                if block != compared_block:
                    if is_block_above(block, compared_block):
                        compared_block["block_above"] = True

print(block_groupings["granite"])