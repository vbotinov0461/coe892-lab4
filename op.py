import requests

# URL = "https://coe892-lab4.onrender.com/lab4/"
URL = "http://localhost:8000/lab4/"

def get_map(): return requests.get(URL + "map")
def update_map(arg1, arg2): return requests.put(URL + "map", json={"dim_v": arg2, "dim_h": arg1})
def get_mine(arg): return requests.get(URL + "mines" if arg == 0 else URL + f"mines/{arg}")
def delete_mine(arg): return requests.delete(URL + f"mines/{arg}")
def create_mine(arg): return requests.post(URL + "mines", json={"x": arg[2], "y": arg[3], "serial": arg[4]})
def update_mine(arg):
    payload = {}
    if arg[1] is not None: payload["x"] = arg[1]
    if arg[2] is not None: payload["y"] = arg[2]
    if arg[3] is not None: payload["serial"] = arg[3]
    return requests.put(URL + f"mines/{arg}", json=payload)
def get_rover(arg): return requests.get(URL + "rovers") if arg == 0 else requests.get(URL + f"rovers/{arg}") 
def create_rover(arg): return requests.post(URL + "rovers", json={"instructions": arg})
def delete_rover(arg): return requests.delete(URL + f"rovers/{arg}")
def send_rover(arg): return requests.put(URL + f"rovers/{arg[2]}", json={"instructions": arg[3]})
def dispatch_rover(arg): return requests.post(URL + f"rovers/{arg}/dispatch")


if __name__ == '__main__':
    start = ""
    while True:
        start = input("""\nType 
        'help' for a list of commands
        'go' to start the program
        'quit' to quit the program\n\n""")
        if start == "help":
            print("""\n\nCommand list:
                map get                                                         : Get map file
                map update {x} {y}                                              : Update x and y dimensions of map
                mine get                                                        : Get mine list
                mine get {id}                                                   : Get info of a specific mine
                mine delete {id}                                                : Delete a mine
                mine create {x} {y} {serial}                                    : Create a mine with coordinates and serial number
                mine update {id} {x}(optional) {y}(optional) {serial}(optional) : Update a mine's information
                rover get                                                       : Get all rover info
                rover get {id}                                                  : Get specific rover info
                rover create {commands}                                         : Create a rover and provide commandlist
                rover delete {id}                                               : Delete a rover
                rover send {id} {commands}                                      : Send a rover some commands
                rover dispatch {id}                                             : Dispatch a rover to execute its commands)""")

        elif (start == "go") or (start == "quit"): break
        else: print("Unrecognized command")

    if start == "go":
        while True:
            user_in = input("Please enter a command: ")
            args, result = user_in.split(), {}

            if args[0]=="map":
                if args[1]=="get": result = get_map() 
                elif (args[1]=="update") and (len(args) == 4): result = update_map(args[2], args[3])
                else: print("Invalid arguments.")

            elif args[0]=="mine":
                if (args[1]=="get") and (len(args) == 2): result = get_mine(0)
                elif args[1]=="get": result = get_mine(args[2])
                elif (args[1]=="delete") and (len(args) == 3): result = delete_mine(args[2])
                elif (args[1]=="create") and (len(args) == 5): result = create_mine(args)
                elif (args[1]=="update") and (len(args) == 5): result = update_mine(args)
                else: print("Invalid arguments")

            elif args[0]=="rover":
                if (args[1]=="get") and (len(args) == 2): result = get_rover(0)
                elif args[1]=="get": result = get_rover(args[2])
                elif (args[1]=="create") and (len(args) == 3): result = create_rover(args[2])
                elif (args[1]=="delete") and (len(args) == 3): result = delete_rover(args[2])
                elif (args[1]=="send") and (len(args) == 4): result = send_rover(args)
                elif (args[1]=="dispatch") and (len(args) == 3): result = dispatch_rover(args[2])
                else: print("Invalid arguments. Try again, please.")

            elif args[0]=="quit": break

            print("Invalid command. Try again") if not result else print(f"[Server Response] {result.json()}")


