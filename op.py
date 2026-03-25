import requests


def get_map():
    url = f"http://127.0.0.1:8000/lab4/map"
    map_data = requests.get(url)
    print(f"Got map {map_data.json()}")


def update_map(arg1, arg2):
    url = f"http://127.0.0.1:8000/lab4/map"
    payload = {arg1, arg2}
    response = requests.put(url, json=payload)
    print(f"Updated {response.json()}")


def get_mine(arg):
    if arg == 0:
        url = f"http://127.0.0.1:8000/lab4/mines"
    else:
        url = f"http://127.0.0.1:8000/lab4/mines/{arg}"
    response = requests.get(url)
    print(f"Response to mine request: {response.json()}")


def delete_mine(arg):
    url = f"http://127.0.0.1:8000/lab4/mines/{arg}"
    response = requests.delete(url)
    print(f"Deleted mine {response.json()}")


def create_mine(arg):
    url = f"http://127.0.0.1:8000/lab4/mines"
    payload = {arg[2], arg[3], arg[4]}
    response = requests.post(url, json=payload)
    print(f"Created mine {response.json()}")


def update_mine(arg):
    url = f"http://127.0.0.1:8000/lab4/mines{arg}"
    payload = {}
    if arg[1] is not None:
        payload["x"] = arg[1]
    if arg[2] is not None:
        payload["y"] = arg[2]
    if arg[3] is not None:
        payload["serial"] = arg[3]

    response = requests.put(url, json=payload)
    print(f"Updated mine: {response.json()}")


def get_rover(arg):
    if arg == 0:
        url = f"http://127.0.0.1:8000/lab4/rovers"
    else:
        url = f"http://127.0.0.1:8000/lab4/rovers/{arg}"
    response = requests.get(url)
    print(f"Response to rover request: {response.json()}")


def create_rover(arg):
    url = f"http://127.0.0.1:8000/lab4/rovers"
    payload = {arg[2]}
    response = requests.post(url, json=payload)
    print(f"Created rover: {response.json()}")


def delete_rover(arg):
    url = f"http://127.0.0.1:8000/lab4/rovers/{arg}"
    response = requests.delete(url)
    print(f"Deleted rover: {response.json()}")


def send_rover(arg):
    url = f"http://127.0.0.1:8000/lab4/{arg[2]}"
    payload = {arg[3]}
    response = requests.put(url, json=payload)
    print(f"HANDLE THIS RESPONSE: {response.json()}")


def dispatch_rover(arg):
    url = f"http://127.0.0.1:8000/lab4/rovers/{arg[2]}/dispatch"
    response = requests.post(url)
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

        elif (start == "go") | (start == "quit"):
            break
        else:
            print("Unrecognized command")

    if start == "go":
        while True:
            user_in = input("Please enter a command: ")
            args = user_in.split()

            if "map" in args:
                if "get" in args:
                    get_map()
                elif ("update" in args) & (len(args) == 4):
                    update_map(args[2], args[3])
                else:
                    print("Invalid arguments.")

            elif "mine" in args:
                if ("get" in args) & (len(args) == 2):
                    get_mine(0)
                elif "get" in args:
                    get_mine(args[2])
                elif "delete" in args:
                    delete_mine(args[2])
                elif ("create" in args) & (len(args) == 5):
                    create_mine(args)
                elif ("update" in args) & (len(args) == 5):
                    update_mine(args)
                else:
                    print("Invalid arguments")

            elif "rover" in args:
                if ("get" in args) & (len(args) == 2):
                    get_rover(0)
                elif "get" in args:
                    get_rover(args[2])
                elif ("create" in args) & (len(args) > 2):
                    create_rover(args[2])
                elif ("delete" in args) & (len(args) > 2):
                    if len(args) < 3:
                        print("Please provide parameters")
                    else:
                        delete_rover(args[2])
                elif ("send" in args) & (len(args) > 2):
                    send_rover(args)
                elif ("dispatch" in args) & (len(args) > 2):
                    dispatch_rover(args[2])
                else:
                    print("Invalid arguments. Try again, please.")

            else:
                print("Could not recognize arguments. Try again.")
