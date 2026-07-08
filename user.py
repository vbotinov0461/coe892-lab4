import requests
import time

# URL = "https://coe892-lab4.onrender.com/lab4/"
URL = "http://localhost:8000/"


# UI text assets
start_msg = """\nType 
        'help' for a list of commands
        'go' to start the program
        'quit' to quit the program\n\n"""

command_list = """\n\nCommand list:
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
                rover dispatch {id}                                             : Dispatch a rover to execute its commands)"""



# User request endpoints 
def get_map(): return requests.get(URL + "map")
def update_map(arg1, arg2): return requests.put(URL + "map", json={"dim_v": arg2, "dim_h": arg1})
def get_mine(arg): return requests.get(URL + "mines" if arg == 0 else URL + f"mines/{arg}")
def delete_mine(arg): return requests.delete(URL + f"mines/{arg}")
def create_mine(arg): return requests.post(URL + "mines", json={"x": arg[2], "y": arg[3], "serial": arg[4]})
def update_mine(arg): return requests.put(URL + f"mines/{arg}", json={"x": arg[1], "y": arg[2], "serial": arg[3]}) # Please test this
def get_rover(arg): return requests.get(URL + "rovers") if arg == 0 else requests.get(URL + f"rovers/{arg}") 
def create_rover(arg): return requests.post(URL + "rovers", json={"instructions": arg})
def delete_rover(arg): return requests.delete(URL + f"rovers/{arg}")
def send_rover(arg): return requests.put(URL + f"rovers/{arg[2]}", json={"instructions": arg[3]})
def dispatch_rover(arg): return requests.post(URL + f"rovers/{arg}/dispatch")


if __name__ == '__main__':
    app.run(debug=False, port=5000, use_reloader=False)
    
    # Parse arguments and call the relevant handlers
    # Consider changing mechanism to argparse
    start = ""
    print(start_msg)
    while True:
        start = input("Please enter a command: ")
        args, result = start.split(), {}
        
        match args[0]:
            case "help": print(command_list)
            case "quit": break
            case "map":
                match args[1]:
                    case "get": result = get_map() # 0 params
                    case "update": result = update_map(args[2], args[3]) # 2 params
                print(f"[Server Response] {result.json()}")
            case "mine":
                match args[1]:
                    case ["get", *options] if options: result = get_mine(options)
                    case ["get", *options]: result = get_mine(0)
                    case "create": result = create_mine(args)
                    case "update": result = update_mine(args)
                    case "delete": result = delete_mine(args[2])
                print(f"[Server Response] {result.json()}")
            case "rover": 
                match args[1]:
                    case ["get", *options] if options: result = get_rover(options)
                    case ["get", *options]: result = get_rover(0)
                    case ["create", *options] if options: result = create_rover(options)
                    case ["create", *options]: result = create_rover(0)
                    case "delete": result = delete_rover(args[2])
                    case "send": result = send_rover(args)
                    case "dispatch": result = dispatch_rover(args[2])
                print(f"[Server Response] {result.json()}")
            case _:
                print("Invalid argument.")
                sleep(3)

        


