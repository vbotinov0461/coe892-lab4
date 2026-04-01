import requests

URL = "https://coe892-lab4.onrender.com/lab4/"

def get_map():
    map_data = requests.get(URL + "map")
    print(f"Got map {map_data.json()}")


def update_map(arg1, arg2):
    response = requests.put(URL + "map", json={arg1, arg2})
    print(f"Updated {response.json()}")


def get_mine(arg):
    url = URL + "mines" if arg == 0 else URL + f"mines/{arg}"
    response = requests.get(url)
    print(f"Response to mine request: {response.json()}")


def delete_mine(arg):
    response = requests.delete(URL + f"mines/{arg}")
    print(f"Deleted mine {response.json()}")


def create_mine(arg):
    response = requests.post(URL + "mines", json={arg[2], arg[3], arg[4]})
    print(f"Created mine {response.json()}")


def update_mine(arg):
    payload = {}
    if arg[1] is not None: payload["x"] = arg[1]
    if arg[2] is not None: payload["y"] = arg[2]
    if arg[3] is not None: payload["serial"] = arg[3]
    response = requests.put(URL + f"mines/{arg}", json=payload)
    print(f"Updated mine: {response.json()}")


def get_rover(arg):
    response = requests.get(URL + "rovers") if arg == 0 else requests.get(URL + f"rovers/{arg}") 
    print(f"Response to rover request: {response.json()}")


def create_rover(arg):
    response = requests.post(URL + "rovers", json={arg[2]})
    print(f"Created rover: {response.json()}")


def delete_rover(arg):
    response = requests.delete(URL + f"rovers/{arg}")
    print(f"Deleted rover: {response.json()}")


def send_rover(arg):
    response = requests.put(URL + f"{arg[2]}", json={arg[3]})
    print(f"HANDLE THIS RESPONSE: {response.json()}")


def dispatch_rover(arg):
    response = requests.post(URL + f"rovers/{arg[2]}/dispatch")
    print(f"Dispatched rover! {response.json()}")


if __name__ == '__main__':
    start = ""
    while True:
        start = input("""\nType 
        'help' for a list of commands
        'go' to start the program
        'quit' to quit the program\n\n""")
        if start == "help":
            print("""\n\nCommand list:
                map get : Get map file
                map update {x} {y} : Update x and y dimensions of map
                mine get : Get mine list
                mine get {id}                                                   : Get info of a specific mine
                mine delete {id}                                                : Delete a mine
                mine create {x} {y} {serial}                                    : Create a mine with coordinates and serial number
                mine update {id} {x}(optional) {y}(optional) {serial}(optional) : Update a mine's information
                rover get : Get all rover info
                rover get {id} : Get specific rover info
                rover create {commands} : Create a rover and provide commandlist
                rover delete {id} : Delete a rover
                rover send {commands} : Send a rover some commands
                rover dispatch {id} : Dispatch a rover to execute its commands)""")

        elif (start == "go") or (start == "quit"): break
        else: print("Unrecognized command")

    if start == "go":
        while True:
            user_in, args = input("Please enter a command: "), user_in.split()

            if "map" in args:
                if "get" in args: get_map()
                elif ("update" in args) & (len(args) == 4): update_map(args[2], args[3])
                else: print("Invalid arguments.")

            elif "mine" in args:
                if ("get" in args) & (len(args) == 2): get_mine(0)
                elif "get" in args: get_mine(args[2])
                elif "delete" in args: delete_mine(args[2])
                elif ("create" in args) & (len(args) == 5): create_mine(args)
                elif ("update" in args) & (len(args) == 5): update_mine(args)
                else: print("Invalid arguments")

            elif "rover" in args:
                if ("get" in args) & (len(args) == 2): get_rover(0)
                elif "get" in args: get_rover(args[2])
                elif ("create" in args) & (len(args) > 2): create_rover(args[2])
                elif ("delete" in args) & (len(args) > 2): delete_rover(args[2])
                elif ("send" in args) & (len(args) > 2): send_rover(args)
                elif ("dispatch" in args) & (len(args) > 2): dispatch_rover(args[2])
                else: print("Invalid arguments. Try again, please.")

            else: print("Could not recognize arguments. Try again.")
