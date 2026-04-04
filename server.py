from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import random
import string
import hashlib

chars = string.ascii_letters + string.digits  # String pool for PIN


# Global utility functions
def get_json(fname):
    try:
        if not os.path.exists(fname) or os.path.getsize(fname) == 0:
            return {}  # Or return the default structure for that specific file
        with open(fname, "r") as f: return json.load(f)
    except json.JSONDecodeError:
        return {}
# facing legend --> SOUTH=0, WEST=1, NORTH=2, EAST=3
def turn(ltr, d): 
    print("Turning!")
    return (d + (1 if ltr == "R" else -1)) % 4
def move(l, d):
    # Retrieve map boundaries
    data = get_json(map_file)
    x_bound, y_bound = data["cols"], data["rows"]

    # Execute movement
    if (d == 0) and (l[1] < (y_bound-1)): l[1] += 1
    elif (d == 1) and (l[0] > 0): l[0] -= 1
    elif (d == 2) and (l[1] > 0): l[1] -= 1
    elif (d == 3) and (l[0] < (x_bound-1)): l[0] += 1
    return l
def dig(l):
    sn = ""
    # Check if there's a mine here
    data = get_json(map_file)
    if data["grid"][l[1]][l[0]] == 1:
        print(f"Mine located at {l[0]}, {l[1]}")
        # Lookup the mine and retrieve SN
        mine_data = get_json(mines_file)
        for m in mine_data["mines"]:
            if (m[2][0] == l[0]) and (m[2][1] == l[1]):
                sn = m[1]
                mine_data["mines"].remove(m)
                break
        # Brute force using randomly generated PINs
        while 1:
            tmk = f"{''.join(random.choices(chars, k=4))}{sn}"
            key = hashlib.sha256(tmk.encode()).hexdigest()
            if key[:6] == "000000":
                print(key)
                map_data = get_json(map_file)
                map_data["grid"][l[1]][l[0]] = 0
                with open(map_file, "w") as f: json.dump(map_data, f, indent=4)
                with open(mines_file, "w") as f: json.dump(mine_data, f, indent=4)
                break
        print("Mine disarmed!")


# -- DEFINE JSON ASSETS --
map_file, mines_file = "map.json", "mines.json"
rovers, next_rover_id, next_mine_id = [], 1, 3

if not os.path.exists(map_file):
    with open(map_file, "w") as F:
        json.dump({"grid": [[0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]], "rows": 4, "cols": 3}, F)

if not os.path.exists(mines_file):
    with open(mines_file, "w") as F:
        json.dump({"mines": [[1, "x1y0", [1, 0]], [2, "x0y2", [0, 2]]]}, F)

# --- FastAPI Logic ---
app = FastAPI()


class Loc(BaseModel):
    dim_v: int
    dim_h: int
class MineInfo(BaseModel):
    x: int
    y:  int
    serial: str
class RoverInfo(BaseModel):
    instructions: str

# Map & Mines Endpoints
@app.get("/lab4/map")
def get_map(): return get_json(map_file)

@app.put("/lab4/map")
def put_map(loc: Loc):
    data = get_json(map_file)
    if loc.dim_v > data["rows"]:
        diff = data["rows"] - loc.dim_v          # grab addition magnitude
        pad = [0]*len(data["grid"][0])           # create pad row
        addition = [pad]*diff                    # create addition to grid list
        data["grid"].extend(addition)
        data["rows"] = loc.dim_v                 # update number of rows
    if loc.dim_h > data["cols"]:
        diff = data["cols"] - loc.dim_h
        pad = [0]*diff
        for r in data["grid"]: r.extend(pad)
        data["cols"] = loc.dim_h

    if loc.dim_v < data["rows"]:
        data["grid"] = data["grid"][:loc.dim_v]
        data["rows"] = loc.dim_v
    if loc.dim_h < data["cols"]:
        for r in data["rows"]: r = r[:loc.dim_h]
        data["cols"] = loc.dim_h

    with open(map_file, "w") as f: json.dump(data, f, indent=4)
    return {"Success": "Updated"}

@app.get("/lab4/mines")
def get_mines(): return get_json(mines_file)

@app.get("/lab4/mines/{mine_id}")
def get_mines_id(mine_id: int):
    data, flag = get_json(mines_file), False
    for m in data["mines"]:
        if m[0] == mine_id: result, flag = m, True
    if not flag: result = {"Failed": "Mine doesn't exist"}
    return result

@app.delete("/lab4/mines/{mine_id}")
def mine_delete(mine_id: int):
    data = get_json(mines_file)
    
    # Check existence
    coords = [-1]
    for m in data["mines"]: 
        if m[0] == mine_id: coords = m[2]
    if coords[0] == -1: return {"Failed": "Mine doesn't exist"}
    
    # Erase from map file
    map_data = get_json(map_file)
    map_data["grid"][coords[1]][coords[0]] = 0
    with open(map_file, "w") as f: json.dump(map_data, f, indent=4)
    
    # Erase from ref json
    original_len = len(data["mines"])
    data["mines"] = [m for m in data["mines"] if m[0] != mine_id]
    with open(mines_file, "w") as f: json.dump(data, f, indent=4)
    return {"Success": "Deleted"}

@app.post("/lab4/mines")
def mine_create(body: MineInfo):
    global next_mine_id
    data = get_json(mines_file)

    # Check if spot is taken
    map_data = get_json(map_file)
    if map_data["grid"][body.y][body.x]==1: return {"Failed": "There's already a mine there"}
    
    # Update map
    map_data["grid"][body.y][body.x] = 1
    with open(map_file, "w") as f: json.dump(map_data, f, indent=4)
    
    # Add json record
    data["mines"].append([next_mine_id, body.serial, [body.x, body.y]])
    next_mine_id+=1
    with open(mines_file, "w") as f: json.dump(data, f, indent=4)
    return {"Success": f"New mine ID is: {next_mine_id-1}"}

@app.put("/lab4/mines/{mine_id}")
def mine_update(mine_id: int, body: MineInfo):
    data, flag = get_json(mines_file), False
    # Check existence
    for m in data["mines"]:
        if m[0] == mine_id: flag = True
    if not flag: return {"Failed": "Mine doesn't exist"}
    
    result = data
    for m in data["mines"]:
        if m[0] == mine_id:
            if body.serial is not None: m[1] = body.serial
            map_data = get_json(map_file)
            if (body.x is not None) and (body.y is not None):
                map_data["grid"][m[2][1]][m[2][0]] = 0
                map_data["grid"][body.y][body.x] = 1
                m[2][0], m[2][1] = body.x, body.y
            elif body.x is not None:
                map_data["grid"][m[2][1]][m[2][0]] = 0
                map_data["grid"][body.y][m[2][0]] = 1
                m[2][0] = body.x
            elif body.y is not None:
                map_data["grid"][m[2][1]][m[2][0]] = 0
                map_data["grid"][m[2][1]][body.x] = 1
                m[2][1] = body.y
            with (map_file, "w") as f: json.dump(map_data, f, indent=4)
            result = m
            break
    with open(mines_file, "w") as f: json.dump(data, f, indent=4)
    return result

@app.get("/lab4/rovers")
def get_rovers():
    global rovers
    return {"Rover list is": "EMPTY"} if len(rovers)==0 else rovers

@app.get("/lab4/rovers/{rover_id}")
def get_rover_id(rover_id: int):
    global rovers
    result = {"Failed": "Rover doesn't exist"}
    if not(len(rovers)==0):
        for r in rovers:
            if r["id"] == rover_id: result = r
    return result

@app.post("/lab4/rovers")
def rover_create(body: RoverInfo):
    global rovers, next_rover_id
    rovers.append({"id": next_rover_id, "status": "Not Started", "coords": [0, 0], "facing": 0, "instructions": body.instructions})
    next_rover_id+=1
    return {"Success": f"Created Rover {next_rover_id-1}"}

@app.delete("/lab4/rovers/{rover_id}")
def rover_delete(rover_id: int):
    global rovers
    original_len = len(rovers)
    rovers = [r for r in rovers if r["id"] != rover_id]
    return {"Failed": "Rover doesn't exist"} if original_len==len(rovers) else {"Success": f"Successfully deleted Rover {rover_id}"}

@app.put("/lab4/rovers/{rover_id}")
def rover_sendInst(rover_id: int, body: RoverInfo):
    global rovers
    found = False
    for r in rovers:
        if r["id"]==rover_id:
            r["instructions"] = body.instructions
            found = True
    return {"Success": f"Successfully passed instructions to Rover {rover_id}"} if found else {"Failed": f"Could not pass instructions to Rover {rover_id}"}

@app.post("/lab4/rovers/{rover_id}/dispatch")
def rover_dispatch(rover_id: int):
    global rovers
    target = {}
    for r in rovers:
        if r["id"]==rover_id: target = r
    if not target: return {"Failed": "Rover doesn't exist"}

    target["status"] = "Moving"
    for c in target["instructions"]:
        if (c == "L") or (c == "R"): target["facing"] = turn(c, target["facing"])
        elif c == "M":
            # Check if we are leaving a mine
            map_data = get_json(map_file)
            if map_data["grid"][target["coords"][1]][target["coords"][0]] == 1: 
                print(f"[R{target['id']}] Blew UP!")
                map_data["grid"][target["coords"][1]][target["coords"][0]] = 0
                with open(map_file, "w") as f: json.dump(map_data, f, indent=4) 
                target["status"] = "Eliminated"
                break
            else: target["coords"] = move(target["coords"], target["facing"])
        elif c == "D": dig(target["coords"])
    
    # Mark as Finished
    if target["status"] != "Eliminated": target["status"] = "Finished"
    return target
