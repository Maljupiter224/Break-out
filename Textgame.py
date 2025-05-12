class Item:
    def __init__(self, name, value=0, size=1, usable=False, description=""):
        self.name = name
        self.value = value
        self.size = size
        self.usable = usable
        self.description = description

class Room:
    def __init__(self, name, description, exits=None, containers=None):
        self.name = name
        self.description = description
        self.exits = exits if exits else {}
        self.containers = containers if containers else {}

class Game:
    def __init__(self):
        self.time_left = 60
        self.inventory = []
        self.max_inventory_slots = 10
        self.current_room = "Bedroom #2"
        self.rooms = self.create_rooms()
        self.master_bedroom_unlocked = False
        self.golden_chest_opened = False
        self.unlock_code = "nes"
        self.safe_code = "4729"

    def show_help(self):
        print("""
        📖 GAME HELP

        🕵️ STORY: 
        You are a professional thief, known only as "Shadow". After weeks of surveillance, 
        you’ve chosen the perfect time to strike — the owners of this wealthy home leave 
        for an exact 1-hour walk each evening. You have 60 minutes to loot as much as you 
        can and escape before they return.

        🎯 OBJECTIVE: - 
        Explore the house, steal valuable items, and escape through the front door before 
        time runs out. Your bag has a limited capacity — 10 slots. Some items take more 
        than 1 slot (like the laptop or gold bars). Plan wisely.

        🕹️ CONTROLS:
        - Movement: north, south, east, west (or n, s, e, w)
        - look [container]      : View what’s inside a specific place
        - take [item]           : Take an item from a container
        - use [item]            : Use usable items (e.g., crowbar, key)
        - inventory             : View current items and slots used
        - help                  : View this help screen
        - quit                  : End the game

        💡 TIPS:
        - Use the crowbar in the bathroom to unlock the Master Bedroom.
        - Use the bobby pin to pick locks — enter the correct 3-letter direction code.
        - Use the key to unlock the front door and escape.

        Good luck, Shadow.
            """) # Rajat did story, Shlok did objectives, Adish did controls and the tips section was together


    def create_item(self, name, value=0, size=1, usable=False, description=""):
        return Item(name, value, size, usable, description)

    def create_rooms(self):
        i = self.create_item
        return {
            "Garage": Room("Garage", "A dusty garage.",
                {"south": "Study"},
                {
                    "behind toolbox": [i("wooden chest")],
                    "garage storage": [i("rusty broken wrench", 0)]
                }),
            "Study": Room("Study", "A quiet study room.",
                {"north": "Garage", "east": "Living Room"},
                {
                    "study table": [i("pencil case", 0)],
                    "drawer": [i("laptop", 2100, 2)],
                    "bookshelf": []
                }),
            "Bedroom #2": Room("Bedroom #2", "Where your heist begins.",
                {"south": "Kitchen"},
                {
                    "bedside table top": [i("bobby pin", 0, 1, True)],
                    "bedside table inside": [],
                    "under the bed": [],
                    "mirror": []
                }),
            "Kitchen": Room("Kitchen", "A clean modern kitchen.",
                {"north": "Bedroom #2", "south": "Master Bedroom", "west": "Living Room"},
                {
                    "cabinet": [i("cutlery set", 40), i("monkey statue", 200)]
                }),
            "Living Room": Room("Living Room", "The heart of the house.",
                {"north": "Exit", "east": "Kitchen", "south": "Bathroom", "west": "Study"},
                {
                    "inside sofa": [i("phone", 800)],
                    "wall": [i("painting", 450)],
                    "digital clock": []
                }),
            "Laundry": Room("Laundry", "A damp laundry room.",
                {"east": "Bathroom"},
                {
                    "top shelves": [],
                    "clothes": [i("wallet", 100)],
                    "bottom shelves": [i("crowbar", 0, 1, True)]
                }),
            "Bathroom": Room("Bathroom", "Clean and minimalist.",
                {"north": "Living Room", "west": "Laundry"},
                {
                    "inside toilet": [],
                    "in the sink": [i("ruby ring", 1100)],
                    "sink cabinet": [i("key", 0, 1, True)]
                }),
            "Master Bedroom": Room("Master Bedroom", "A luxurious locked room.",
                {},  # Exits added after using crowbar
                {
                    "bedside table (on top)": [],
                    "bedside table (inside)": [i("button", 0)],
                    "mirror": [i("golden chest", 0, 1, True)],
                    "wardrobe": [i("diamond necklace", 7000)]
                }),
            "Exit": Room("Exit", "The front door. Escape when you're done.",
                {"south": "Living Room"}
            )
        }

    def inventory_space(self):
        return sum(item.size for item in self.inventory)

    def show_status(self):
        room = self.rooms[self.current_room]
        print(f"\n📍 You are in the {self.current_room}.")
        print(room.description)
        print("")
        print("🚪 Exits:", ', '.join(room.exits.keys()))
        print("")
        print("🗄️ Places to search:", ', '.join(room.containers.keys()))
        print("")
        print(f"⏳ Time left: {self.time_left} minutes")
        print(f"🎒 Inventory: {self.inventory_space()}/{self.max_inventory_slots} slots used")

    def move(self, direction):
        room = self.rooms[self.current_room]
        if direction in room.exits:
            destination = room.exits[direction]
            if destination == "Master Bedroom" and not self.master_bedroom_unlocked:
                print("🚪 The Master Bedroom is locked. Use a crowbar to break in.")
                return
            self.current_room = destination
            self.time_left -= 1
        else:
            print("❌ You can't go that way.")

    def look(self, location):
        room = self.rooms[self.current_room]
        if location in room.containers:
            contents = room.containers[location]
            if contents:
                print(f"🔍 Inside {location}, you find:")
                for item in contents:
                    print(f" - {item.name} (${item.value})")
            else:
                print(f"🔍 Nothing found in {location}.")
        else:
            print("❌ There's nothing like that here.")

    def take(self, item_name):
        room = self.rooms[self.current_room]
        for location, items in room.containers.items():
            for item in items:
                if item.name.lower() == item_name.lower():
                    if self.inventory_space() + item.size > self.max_inventory_slots:
                        print("🎒 Not enough space in your bag.")
                        return
                    self.inventory.append(item)
                    items.remove(item)
                    print(f"✅ You took {item.name} (${item.value})")
                    self.time_left -= 1
                    return
        print("❌ That item isn't here.")

    def use(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item or not item.usable:
            print("❌ You can't use that.")
            return

        if item.name.lower() == "crowbar" and self.current_room == "Bathroom":
            print("💪 You break open the Master Bedroom door with the crowbar!")
            self.master_bedroom_unlocked = True
            self.rooms["Bathroom"].exits["east"] = "Master Bedroom"
            self.rooms["Kitchen"].exits["south"] = "Master Bedroom"
            self.rooms["Master Bedroom"].exits["west"] = "Bathroom"
            self.rooms["Master Bedroom"].exits["north"] = "Kitchen"
            self.time_left -= 3
        elif item.name.lower() == "bobby pin":
            print("🔐 Attempting to pick the lock...")
            guess = input("Enter 3-letter code (e.g. nes): ").strip().lower()
            if guess == self.unlock_code:
                print("✅ Chest unlocked!")
                chest = Item("gold bars", 25000, 3)
                self.rooms[self.current_room].containers["mirror"].append(chest)
                self.golden_chest_opened = True
            else:
                print("❌ Incorrect code. You lose 5 minutes.")
                self.time_left -= 5
        elif item.name.lower() == "key" and self.current_room == "Exit":
            print("🔓 You unlock the front door and escape!")
            self.end_game()
        else:
            print("❌ That item can't be used here.")

    def show_inventory(self):
        print("🎒 Inventory:")
        for item in self.inventory:
            print(f" - {item.name} (${item.value}, size: {item.size})")
        print(f"Total value: ${sum(i.value for i in self.inventory)}")

    def end_game(self):
        print("\n🏁 You escaped with:")
        total_value = 0
        for item in self.inventory:
            print(f" - {item.name} (${item.value})")
            total_value += item.value
        print(f"\n💸 Total loot value: ${total_value}")
        print(f"⏳ Time remaining: {self.time_left} minutes")
        print("🛑 Game Over!")

    def play(self):
        print("💀 You're 'Shadow' the thief. You have 60 minutes to loot and escape.")
        print("Commands: n/s/e/w or full direction, look [container], take [item], use [item], inventory, help, quit")
        while self.time_left > 0:
            self.show_status()
            command = input("> ").strip().lower()
            dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
            if command in dirs:
                self.move(dirs[command])
            elif command in ["north", "south", "east", "west"]:
                self.move(command)
            elif command.startswith("look "):
                self.look(command.split(" ", 1)[1])
            elif command.startswith("take "):
                self.take(command.split(" ", 1)[1])
            elif command.startswith("use "):
                self.use(command.split(" ", 1)[1])
            elif command == "inventory":
                self.show_inventory()
            elif command == "help":
                self.show_help()
            elif command == "quit":
                print("👋 You left the house.")
                break
            else:
                print("❓ Invalid command.")
        else:
            print("⏰ Time's up! The owners are home!")
            self.end_game()

if __name__ == "__main__":
    game = Game()
    game.play()
