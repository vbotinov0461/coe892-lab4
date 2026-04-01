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

# Rover Execution Functions
def turn(ltr, d): return (d + (1 if ltr == "R" else -1)) % 4


def move(l, d):
    # Retrieve map boundaries
    data = get_json(map_file)
    x_bound, y_bound = data["cols"], data["rows"]

    # Execute movement
    if (d == 0) and (l[1] < (y_bound-1)):
        l[1] += 1
    elif (d == 1) and (l[0] > 0):
        l[0] -= 1
    elif (d == 2) and (l[1] > 0):
        l[1] -= 1
    elif (d == 3) and (l[0] < (x_bound-1)):
        l[0] += 1
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
                break
        # Brute force using randomly generated PINs
        while 1:
            tmk = f"{''.join(random.choices(chars, k=4))}{sn}"
            key = hashlib.sha256(tmk.encode()).hexdigest()
            if key[:6] == "000000":
                print(key)
                map_data = get_json(map_file)
                map_data["grid"][l[1]][l[0]] = 0
                break
        print("Mine disarmed!")


# -- DEFINE JSON ASSETS --
rover_dir, map_file, mines_file = "./rovers/", "map.json", "mines.json"

if not os.path.exists(map_file):
    with open(map_file, "w") as F:
        json.dump({"grid": [[0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],
                   "rows": 4, "cols": 3, "next_id": 1}, F)

if not os.path.exists(mines_file):
    with open(mines_file, "w") as F:
        json.dump({"mines": [[1, "x1y0", [1, 0]], [2, "x0y2", [0, 2]]],
                   "next_id": 3}, F)

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
        for r in data["grid"]:
            r.extend(pad)
        data["cols"] = loc.dim_h

    if loc.dim_v < data["rows"]:
        data["grid"] = data["grid"][:loc.dim_v]
        data["rows"] = loc.dim_v
    if loc.dim_h < data["cols"]:
        for r in data["rows"]:
            r = r[:loc.dim_h]
        data["cols"] = loc.dim_h

    with open(map_file, "w") as f: json.dump(data, f, indent=4)


@app.get("/lab4/mines")
def get_mines(): return get_json(mines_file)


@app.get("/lab4/mines/{mine_id}")
def get_mines_id(mine_id: int):
    data, flag = get_json(mines_file), False
    for m in data["mines"]:
        if m[0] == mine_id:
            result, flag = m, True
    if not flag:
        raise HTTPException(status_code=404, details="Mine not found!")
    return result


@app.delete("/lab4/mines/{mine_id}")
def mine_delete(mine_id: int):
    data = get_json(mines_file)
    
    # Check existence
    coords = [-1]
    for m in data["mines"]:
        if m[0] == mine_id: coords = m[2]
    if coords[0] == -1: raise HTTPException(status_code=404, detail="Mine not found!")
    
    # Erase from map file
    map_data = get_json(map_file)
    map_data["grid"][coords[0]][coords[1]] = 0
    with open(map_file, "w") as f: json.dump(map_data, f, indent=4)
    
    # Erase from ref json
    original_len = len(data["mines"])
    data["mines"] = [m for m in data["mines"] if m[0] != mine_id]
    with open(mines_file, "w") as f: json.dump(data, f, indent=4)
    return {"message": "Deleted"}


@app.post("/lab4/mines")
def mine_create(body: MineInfo):
    data = get_json(mines_file)
    # Update map
    map_data = get_json(map_file)
    map_data["grid"][body.x][body.y] = 1
    with open(map_file, "w") as f: json.dump(map_data, f, indent=4)
    # Add json record
    data["mines"].append([data["next_id"], body.serial, [body.x, body.y]])
    data["next_id"]+=1
    with open(mines_file, "w") as f: json.dump(data, f, indent=4)
    return data["next_id"]-1


@app.put("/lab4/mines/{mine_id}")
def mine_update(mine_id: int, body: MineInfo):
    data, flag = get_json(mines_file), False
    # Check existence
    for m in data["mines"]:
        if m[0] == mine_id:
            flag = True
            break
    if not flag: raise HTTPException(status_code=404, details="Mine not found!")
    
    result = data
    for m in data["mines"]:
        if m[0] == mine_id:
            if body.serial is not None:
                m[1] = body.serial
            if (body.x is not None) and (body.y is not None):
                map_data = get_json(map_file)
                map_data["grid"][m[2][0]][m[2][1]] = 0
                map_data["grid"][body.x][body.y] = 1
                with (map_file, "w") as f:
                    json.dump(map_data, f, indent=4)
                m[2][0], m[2][1] = body.x, body.y
            elif body.x is not None:
                map_data = get_json(map_file)
                map_data["grid"][m[2][0]][m[2][1]] = 0
                map_data["grid"][body.x][m[2][1]] = 1
                with (map_file, "w") as f:
                    json.dump(map_data, f, indent=4)
                m[2][0] = body.x
            elif body.y is not None:
                map_data = get_json(map_file)
                map_data["grid"][m[2][0]][m[2][1]] = 0
                map_data["grid"][m[2][0]][body.y] = 1
                with (map_file, "w") as f:
                    json.dump(map_data, f, indent=4)
                m[2][1] = body.y
            result = m
            break
    with open(mines_file, "w") as f: json.dump(data, f, indent=4)
    return result


@app.get("/lab4/rovers")
def get_rovers():
    all_data = []
    # Send full rover list by reading all json in rover directory
    for file in os.listdir(rover_dir):
        all_data.append(get_json(os.path.join(rover_dir, file)))
    return all_data


@app.get("/lab4/rovers/{rover_id}")
def get_rover_id(rover_id: int):
    result = "Rover doesn't exist"
    filepath = os.path.join(rover_dir, f"rover_{rover_id}.json")
    if os.path.exists(filepath):
        result = get_json(filepath)
    return result


@app.post("/lab4/rovers")
def rover_create(body: RoverInfo):
    data = get_json(map_file)
    filepath = os.path.join(rover_dir, f"rover_{data['next_id']}.json")
    with open(filepath, "w") as f:
        json.dump({"rover": [data["next_id"], "Not Started", [0, 0], body.instructions]}, f)
    data["next_id"]+=1
    with open(map_file, "w") as f: json.dump(data, f, indent=4)
    return "Created Rover"


@app.delete("/lab4/rovers/{rover_id}")
def rover_delete(rover_id: int):
    result = f"Successfully deleted Rover {rover_id}"
    filepath = os.path.join(rover_dir, f"rover_{rover_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        result = f"Could not delete Rover {rover_id}"
    return result


@app.put("/lab4/rovers/{rover_id}")
def rover_sendInst(rover_id: int, body: RoverInfo):
    result = f"Successfully passed instructions to Rover {rover_id}"
    filepath = os.path.join(rover_dir, f"rover_{rover_id}.json")
    if os.path.exists(filepath):
        data = get_json(filepath)
        data["rover"][3] = body.instructions
        with open(filepath, "w") as f: json.dump(data, f, indent=4)
    else:
        result = f"Could not pass instructions to Rover {rover_id}"
    return result


@app.post("/lab4/rovers/{rover_id}/dispatch")
def rover_dispatch(rover_id: int):
    # local rover variables
    filepath = os.path.join(rover_dir, f"rover_{rover_id}.json")
    facing, data = 0, get_json(filepath)
    for c in data["rover"][3]:
        if (c == "L") or (c == "R"): facing = turn(c, facing)
        elif c == "M":
            # Check if we are leaving a mine
            map_data = get_json(map_file)
            if map_data["grid"][data["rover"][2][1]][data["rover"][2][0]] == 1: break
            else: data["rover"][2] = move(data["rover"][2], facing)
        elif c == "D": dig(data["rover"][2])
    
    # Mark as Finished
    data = get_json(filepath)
    if data["rover"][1] != "Eliminated": data["rover"][1] = "Finished"
    with open(filepath, "w") as f: json.dump(data, f, indent=4)
    return data
