class Room:
    def __init__(self, name, description, exits, containers=None):
        self.name = name
        self.description = description
        self.exits = exits  # dict like {'north': 'Garage'}
        self.containers = containers or {}  # {'bed': ['item1'], 'cabinet': ['item2']}

class Game:
    def __init__(self):
        self.time_left = 60  # minutes
        self.inventory = []
        self.max_items = 10
        self.current_room = "Bedroom #2"
        self.rooms = self.create_rooms()
    
    def create_rooms(self):
        return {
            "Garage": Room("Garage", "A dusty garage with tools and a cabinet.",
                           {"south": "Study"},
                           {"cabinet": ["crowbar"]}),
            "Study": Room("Study", "A quiet room with a desk and drawers.",
                          {"north": "Garage", "east": "Living Room"},
                          {"drawers": ["wallet"]}),
            "Bedroom #2": Room("Bedroom #2", "A cozy bedroom with a bed and drawers.",
                               {"south": "Kitchen"},
                               {"bed": ["phone"], "drawers": ["ruby ring"]}),
            "Living Room": Room("Living Room", "A well-decorated living room.",
                                {"north": "Exit", "east": "Kitchen", "south": "Bathroom", "west": "Study"},
                                {"cabinet": ["painting"]}),
            "Kitchen": Room("Kitchen", "A clean kitchen with a fridge and cabinets.",
                            {"north": "Bedroom #2", "south": "Master Bedroom", "west": "Living Room"},
                            {"cabinet": ["bobby pin", "golden monkey statue"]}),
            "Laundry": Room("Laundry", "A small laundry with a cabinet.",
                            {"east": "Bathroom"},
                            {"cabinet": ["key"]}),
            "Bathroom": Room("Bathroom", "A tiled bathroom with a cabinet.",
                             {"north": "Living Room", "east": "Master Bedroom", "west": "Laundry"},
                             {"cabinet": ["diamond necklace"]}),
            "Master Bedroom": Room("Master Bedroom", "A luxurious bedroom with a golden chest.",
                                   {"north": "Kitchen", "west": "Bathroom"},
                                   {"bed": [], "drawers": [], "cabinet": ["golden chest"]}),
            "Exit": Room("Exit", "The front door. You can leave now if you're done.",
                         {"south": "Living Room"}),
        }

    def show_status(self):
        room = self.rooms[self.current_room]
        print("\n📍 You are in the", self.current_room + ".")
        print(room.description)
        print("🚪 Exits:", ', '.join(room.exits.keys()))
        print("👀 What you can see:", ', '.join(room.containers.keys()) or "Nothing")
        print(f"⏳ Time left: {self.time_left} minutes")

    def move(self, direction):
        room = self.rooms[self.current_room]
        if direction in room.exits:
            self.current_room = room.exits[direction]
            self.time_left -= 1
        else:
            print("❌ You can't go that way.")

    def look(self, container):
        room = self.rooms[self.current_room]
        if container in room.containers:
            items = room.containers[container]
            if items:
                print(f"🔍 Inside the {container}, you find: {', '.join(items)}")
                self.time_left -= 1
            else:
                print(f"🔍 The {container} is empty.")
                self.time_left -= 1
        else:
            print("❌ No such container here.")

    def take(self, item):
        if len(self.inventory) >= self.max_items:
            print("❌ You can't carry any more items.")
            return
        room = self.rooms[self.current_room]
        for container, items in room.containers.items():
            if item in items:
                self.inventory.append(item)
                items.remove(item)
                print(f"✅ You took the {item}.")
                self.time_left -= 1
                return
        print("❌ That item isn't here.")

    def use(self, item):
        if item not in self.inventory:
            print("❌ You don't have that item.")
            return
        room = self.rooms[self.current_room]
        if item == "bobby pin":
            for container, contents in room.containers.items():
                if "golden chest" in contents:
                    print("🔐 You attempt to pick the lock on the golden chest using your bobby pin...")
                    correct_pattern = "nness"
                    for attempt in range(3):
                        guess = input("Enter the 5-direction code (e.g., neswe): ").strip().lower()
                        if guess == correct_pattern:
                            print("✅ Click! The lock opens. Inside the golden chest, you find gold bars and a laptop!")
                            contents.remove("golden chest")
                            contents.extend(["gold bars", "laptop"])
                            self.time_left -= 5
                            return
                        else:
                            self.time_left -= 5
                            print("❌ Wrong sequence! You waste 5 minutes.")
                    print("💥 You failed to pick the lock.")
                    return
            print("❌ There's nothing here to pick with the bobby pin.")
        elif item == "crowbar":
            for container, contents in room.containers.items():
                if "wooden chest" in contents:
                    print("💪 You pry open the wooden chest and find a wallet.")
                    contents.remove("wooden chest")
                    contents.append("wallet")
                    self.time_left -= 2
                    return
        elif item == "key":
            if self.current_room == "Exit":
                print("🔓 You unlock the front door and escape with your loot!")
                self.end_game()
                return
            else:
                print("❌ Nothing to unlock here with a key.")
        else:
            print("❌ You can't use that here.")


    def show_inventory(self):
        print("🎒 Inventory:", ', '.join(self.inventory) or "Empty")

    def end_game(self):
        print("\n💰 You escaped with the following items:")
        for item in self.inventory:
            print(f" - {item}")
        print(f"⏳ Time remaining: {self.time_left} minutes")
        print("🏁 Game Over!")
        exit()

    def play(self):
        print("💀 You're a thief. Steal as much as you can before the owners return.")
        print("🏃‍♂️ Commands: n/s/e/w or north/south/east/west, look [container], take [item], use [item], inventory, quit")

        while self.time_left > 0:
            self.show_status()
            command = input("> ").strip().lower()
            direction_map = {"n": "north", "s": "south", "e": "east", "w": "west"}
            if command in direction_map:
                self.move(direction_map[command])
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
            elif command == "quit":
                print("👋 You have chosen to get caught by the owner. Good Bye.")
                break
            else:
                print("❓ Unknown command.")
        else:
            print("⏰ Time's up! The owners are back!")
            self.end_game()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.play()
