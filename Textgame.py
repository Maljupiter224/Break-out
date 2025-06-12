#=================================================================================================================================#

# item class

class Item:
    def __init__(self, name, description, value=0, slots=1, usable=False, hidden=False): # Done by Adish
        self.name = name
        self.description = description
        self.value = value
        self.slots = slots
        self.usable = usable
        self.hidden = hidden

#=================================================================================================================================#

# Room class

class Room: 
    def __init__(self, name, description, locked=False, puzzle=None): # Done by Adish
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.containers = {}
        self.locked = locked
        self.puzzle = puzzle
        self.searched = False

    def connect(self, direction, room): # Done by Adish and Shlok
        self.exits[direction] = room

    def get_room_in_direction(self, direction): # Done by Adish
        return self.exits.get(direction, None)

#=================================================================================================================================#

# Player Class

class Player:
    def __init__(self, start_room): # Done by Adish
        self.location = start_room
        self.inventory = []
        self.max_slots = 10
        self.time_left = 120  # 2 hours in minutes
        self.score = 0
        self.has_backpack = False
        self.solved_puzzles = set()
        self.riddle = False
        self.secret_unlocked = False
        self.game_start_time = None

    def inventory_slots(self): # Done by Rajat
        return sum(item.slots for item in self.inventory)

    def can_carry(self, item): # Done by Rajat
        return self.inventory_slots() + item.slots <= self.max_slots
    
#=================================================================================================================================#

# Move Function

    def move(self, direction): # Done by Rajat
        if self.time_left <= 0:
            self.end_game(False)
            return

        direction_map = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'north': 'north', 'south': 'south', 'east': 'east', 'west': 'west',
            'up': 'up', 'down': 'down', 'u': 'up', 'd': 'down'
        }
        
        dir = direction_map.get(direction.lower(), None)
        if not dir:
            print("Invalid direction. Use north/south/east/west/up/down or n/s/e/w/u/d.")
            return

        new_room = self.location.get_room_in_direction(dir)
        if new_room:
            if new_room.locked:
                print(f"The {new_room.name} is locked. Find a way to unlock it.")
                return
            self.location = new_room
            self.time_left -= 1
            print(f"\nYou move to the {new_room.name}.")
        else:
            print("You can't go that way.")

#=================================================================================================================================#

# search function to find items in the containers 

    def search(self, container_name): # Done by Rajat, Adish and Shlok
        if self.time_left <= 0:
            self.end_game(False)
            return
        
        container_name = container_name.lower()
        container_found = None

        for container in self.location.containers:
            if container.lower() == container_name:
                container_found = container
                break

        if not container_found:
            print("That container doesn't exist here.")
            return

        self.time_left -= 1
        
        if container_name.lower() == "mirror" and self.location.name == "Master Bedroom":
            if "button_pressed" in self.solved_puzzles:
                print("The mirror slides open, revealing a ladder to the basement!")
                basement = self.location.get_room_in_direction('down')
                if basement:
                    basement.locked = False
                    print("You can now go down to the basement.")
            else:
                print("The mirror looks funny, but you can't see anything special about it.")
            return
        
        if container_found.lower() == "wooden chest" and self.location.name.lower() == "garage":
            print("The wooden chest seems locked. Maybe there is an item that can be used to unlock the chest.")
            print("Hint: You need a bobby pin")
            return
    
        
        if container_name.lower() == "bedside table (inside)" and self.location.name == "Master Bedroom":
            self.solve_button()
            return
        
        if container_name.lower() == "wardrobe" and self.location.name == "Bedroom #2":
            self.solve_riddle()
            return
        
        if container_name.lower() == "bookshelf" and self.location.name == "Bedroom #2":
            if self.riddle:
                self.solve_bookshelf()
            else:
                print("You find nothing interesting.")
            return
        
        if container_name.lower() == "oven" and self.location.name == "Kitchen": # Done by Shlok
            self.solve_oven()
            return
        
        if container_name.lower() == "painting" and self.location.name == "Living Room":
            print("The painting seems to be pretty interesting wiht 3 directions on the compass labelled N S E clockwise. ")
            return
        
        if container_name.lower() == "digital clock" and self.location.name == "Living Room":
            print("The digital clock is stuck displaying: 08:57")
            print("This might be useful for something...")
            return
        
        if container_name.lower() == "ancient statue" and self.location.name == "Basement":
            self.solve_basement_puzzles()
            return
        
        if container_name.lower() == "wardrobe" and self.location.name == "Master Bedroom":
            print("You find a mini safe inside the wardrobe!")
            self.solve_safe()
            return
        
        if container_name.lower() == "cracked wall" and self.location.name == "Basement":
            if "runes_placed" not in self.solved_puzzles:
                print("The wall has deep cracks, but nothing seems special yet.")
                print("Maybe activating something will reveal more...")
                return
                
            # After placing runes
            print("You focus on the cracked wall and notice one section crumbles easily!")
            print("A hidden weak spot is now exposed! (Try 'search weak wall')")
            
            # Add weak wall dynamically
            if "weak wall" not in self.location.containers:
                self.location.containers["weak wall"] = []
            return

        if container_name.lower() == "weak wall" and self.location.name == "Basement":
            print("You break through the weak spot, revealing a hidden lever!")
            print("It's too far to reach with your hands...")
            print("You need something long to flick the lever.")
            self.solved_puzzles.add("wall_searched")
            return

        # Default container search
        items = self.location.containers[container_found]
        if items:
            print(f"\nSearching {container_found}:")
            for item in items:
                if not item.hidden:
                    print(f"- {item.name}: {item.description}")
        else:
            print(f"You search the {container_found} but find nothing of interest.")


#=================================================================================================================================#

# take function to take items you find from containers

    def take(self, item_name): # Done by Adish, edited by Shlok
        if self.time_left <= 0:
            self.end_game(False)
            return

        item_found = None
        for item in self.location.items:
            if item.name.lower() == item_name.lower() and not item.hidden:
                item_found = item
                break
        
        if not item_found:
            for container_name, items in self.location.containers.items():
                for item in items[:]:  # Iterate over a copy to allow removal
                    if item.name.lower() == item_name.lower() and not item.hidden:
                        item_found = item
                        items.remove(item)  # Remove from container
                        break
                if item_found:
                    break
                
        if not item_found:
            print("That item isn't here or is hidden.")
            return
        
        if self.can_carry(item_found):
            self.inventory.append(item_found)
            self.location.items.remove(item_found)
            self.time_left -= 1
            print(f"You took the {item_found.name}.")
            
            if item_found.name == "Backpack":
                self.max_slots += 10
                self.has_backpack = True
                print("Your inventory capacity increased by 10 slots!")
        else:
            print("Not enough space in your inventory.")

#=================================================================================================================================#

# drop function to drop unwanted items

    def drop(self, item_name): # Done by Shlok
        if self.time_left <= 0:
            self.end_game(False)
            return

        item_found = None
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                item_found = item
                break
        
        if not item_found:
            print("You don't have that item.")
            return
        
        self.inventory.remove(item_found)
        self.location.items.append(item_found)
        self.time_left -= 1
        print(f"You dropped the {item_found.name}.")
        
        if item_found.name == "Backpack":
            self.max_slots -= 10
            self.has_backpack = True
            print("Your inventory capacity decreased by 10 slots!")

#=================================================================================================================================#

# Show inventory function which allows the player to see their inventory and its values

    def show_inventory(self): # Done by Rajat
        print("\nInventory:")
        if not self.inventory:
            print("Empty")
            return
            
        total_value = 0
        slots_used = 0
        for item in self.inventory:
            print(f"- {item.name} ({item.slots} slot{'s' if item.slots > 1 else ''}): ${item.value}")
            total_value += item.value
            slots_used += item.slots
        
        print(f"\nTotal value: ${total_value}")
        print(f"Slots used: {slots_used}/{self.max_slots}")

#=================================================================================================================================#

# use function to use the items that can be used in different locations

    def use(self, item_name): # Done by Shlok
        if self.time_left <= 0:
            self.end_game(False)
            return

        item_found = None
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                item_found = item
                break
        
        if not item_found:
            print("You don't have that item.")
            return
        
        if not item_found.usable:
            print(f"You can't use the {item_found.name}.")
            return
        
        self.time_left -= 1
        
        if item_found.name == "Crowbar" and self.location.name == "Master Bedroom":
            if not self.location.locked:
                print("The door is already unlocked.")
                return
                
            print("You use the crowbar to force open the Master Bedroom door!")
            self.location.locked = True
            self.time_left -= 3  # Takes extra time
            print("You tried to force your way to the master bedroom but unfortunately it didnt work and it wasted time.")
            return
        
        if item_found.name == "Key" and (self.location.name == "Kitchen" or self.location.name == "Bathroom"):
            master_bedroom = None
            # Find the Master Bedroom connection
            for direction, room in self.location.exits.items():
                if room.name == "Master Bedroom":
                    master_bedroom = room
                    break
        
            if master_bedroom:
                if not master_bedroom.locked:
                    print("The Master Bedroom is already unlocked.")
                    return
                
                print("You try the key in the Master Bedroom door... it works!")
                master_bedroom.locked = False
                self.time_left -= 2
                return
            else:
                print("There's no Master Bedroom door to unlock here.")
                return
        
        if item_found.name == "Silver Key" and self.location.name == "Exit":
            print("You try the key in the front door... it doesnt works! You fell for the trap")
            self.location.locked = True
            self.time_left -= 2
            return
        
        if item_found.name == "Bobby Pin" and self.location.name == "Garage":
            self.solve_lockpick()
            return
        
        if item_found.name in ["Red Rune", "Blue Rune"] and self.location.name == "Basement":
            print(f"You place the {item_found.name} in the statue's hand.")
            self.inventory.remove(item_found)
            self.location.items.append(item_found)
            self.time_left -= 1
            self.solve_basement_puzzles()  # Check puzzle progress
            return
                  
        
        print(f"You use the {item_found.name}, but nothing happens.")

#=================================================================================================================================#

# function to solve each puzzle 

    def solve_lockpick(self): # Done by Adish and Rajat
        if "lockpick_solved" in self.solved_puzzles:
            print("You've already picked this lock.")
            return
        
        print("\nLockpicking Puzzle:")
        print("The wooden chest has a 3-directional lock (N/S/E/W).")
        print("You need to enter the correct 3-letter combination without repeats.")
        print("Hint: Check the painting in the Living Room for clues.")
        
        guess = input(f"\nEnter combination (e.g. SEW): ").strip().upper()
            
        if len(guess) != 3 or any(c not in 'NSEW' for c in guess):
            print("Invalid input. Use only N, S, E, W with no repeats.")
                
        if len(set(guess)) != 3:
            print("No repeats allowed!")
                
        self.time_left -= 2
            
        if guess == "NSE":
            print("Click! The lock opens.")
            print("Inside the chest you find the Key to the Master Bedroom!")
            key = Item("Key", "Unlocks the Master Bedroom", 0, 1, True)
            self.location.items.append(key)
            self.solved_puzzles.add("lockpick_solved")
            return
        else:
            print("The lock doesn't budge.")
        
        print("The lock remains closed.")

    def solve_oven(self):
        if "oven_solved" in self.solved_puzzles:
            print("The oven is already open with the Monkey Statue inside.")
            return
        
        print("The oven is locked with a temperature dial (1-100).")
        print("You'll need to guess the right temperature to open it.")
        print("Type 'quit' to stop trying.")
        
        target_temp = 71
        
        while True:
            try:
                guess = input("\nAttempt to set temperature to (1-100 or 'quit'): ").strip()
                
                if guess.lower() == 'quit':
                    print("You stop fiddling with the oven.")
                    return
                    
                guess = int(guess)
                
                if guess < 1 or guess > 100:
                    print("Please enter a number between 1 and 100.")
                    continue
                    
                self.time_left -= 1
                    
                if guess == target_temp:
                    print("Click! The oven unlocks and opens.")
                    print("Inside there is a Monkey statue worth $900")
                    monkey_statue = Item("Monkey Statue", "An ornate statue worth $900", 900)
                    self.location.items.append(monkey_statue)
                    self.solved_puzzles.add("oven_solved")
                    return
                elif abs(guess - target_temp) <= 5:
                    print("Very hot!")
                elif abs(guess - target_temp) <= 15:
                    print("Hot")
                elif abs(guess - target_temp) <= 25:
                    print("Warm")
                else:
                    print("Cold")
                    
                # Show status after each guess
                print(f"\nTime left: {self.time_left} minutes")
                
            except ValueError:
                print("Please enter a valid number between 1 and 100, or 'quit' to stop.")
                continue
    
    def solve_riddle(self): # Done by Rajat
        print("Inside the wardrobe, you find a riddle:")
        print("\"Orphaned young with a scar to show,"
        "Famous in ways he didn't know."
        "Chosen by fate, with wand in hand," 
        "Who is the boy that made a stand?\"")
        
        answer = input("Your answer: ").strip().lower()
        self.time_left -= 2
        if "harry potter" in answer:
            print("Correct! The answer is a Harry Potter. Maybe you should search the bookshelf.")
            self.riddle = True
        else:
            print("That doesn't seem right. Keep thinking.")
        return
    
    def solve_bookshelf(self): # Done by Rajat
        print("You see a collection of books. One title catches your eye: 'Harry Potter'")
        action = input("Take the Harry Potter book? (yes/no): ").strip().lower()
        if action == "yes":
            print("As you pull the book, you hear a click! A secret compartment opens.")
            designer_handbag = Item("Designer Handbag", "A luxury handbag worth $3000", 3000)
            print("Inside the secret compartment is a luxury designer handbag worth $3000")
            self.location.items.append(designer_handbag)
            self.solved_puzzles.add("bookshelf_solved")
            self.time_left -= 3
        return
    
    def solve_button(self): # Done by Rajat and Adish
        print("You search inside the bedside table and find a fake bottom!")
        print("You push on it and it opens.")
        print("Underneath it, there's a small button.")
        action = input("Press the button? (yes/no): ").strip().lower()
        if action == "yes":
            self.solved_puzzles.add("button_pressed")
            print("You hear a click! The mirror in the room seems different now.")
            self.time_left -= 2
        return
    
    def solve_safe(self):
        if "safe_solved" in self.solved_puzzles:
            print("The safe is already open.")
            return
            
        print("\nMini Safe Puzzle:")
        print("The safe requires a 4-digit code.")
        print("Hint: Check the digital clock in the Living Room.")
        
        while self.time_left > 0:
            try:
                code = input("Enter 4-digit code (or 'quit' to cancel): ").strip()
                
                if code.lower() == 'quit':
                    print("You stop trying to open the safe.")
                    return
                    
                if len(code) != 4 or not code.isdigit():
                    print("Please enter exactly 4 digits.")
                    continue
                    
                self.time_left -= 1
                
                if code == "0857":
                    print("Click! The safe unlocks.")
                    print("Inside you find a Diamond Necklace!")
                    necklace = Item("Diamond Necklace", "A sparkling necklace worth $7000", 7000, 1)
                    self.location.items.append(necklace)
                    self.solved_puzzles.add("safe_solved")
                    return
                else:
                    print("Incorrect code. Try again.")
                    print(f"Time left: {self.time_left} minutes")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nYou stop trying to open the safe.")
                return

    def solve_basement_puzzles(self):
        # Check current puzzle state
        if "basement_solved" in self.solved_puzzles:
            print("The basement puzzles have already been solved.")
            return
        
        # Stage 1: Check if both runes are placed
        if "runes_placed" not in self.solved_puzzles:
            red_rune_placed = False
            blue_rune_placed = False
            
            if not (red_rune_placed and blue_rune_placed):
                print("An ancient statue stands in the center with outstretched hands.")
                print("You need to place both the Red Rune and Blue Rune in its hands.")
                return
             
            print("\nAs you place the final rune, the statue's eyes begin to glow!")
            print("It speaks: 'To escape this room, break where the light is dim,'")
            print("'Find the tool to reach beyond, and freedom shall be granted to him.'")
            self.solved_puzzles.add("runes_placed")
            self.location.containers["weak wall"] = []  # Add weak wall to searchable areas
            return
        
        # Stage 2: Check if weak wall has been searched
        if "wall_searched" in self.solved_puzzles:
            if "Sword" in [item.name for item in self.inventory]:
                print("You use the Sword to flip the lever!")
                print("The statue crumbles, revealing a Golden Key!")
                print("A ladder suddenly drops from the ceiling, leading back up!")

                # Add exit to Master Bedroom
                master_bedroom = None
                for room in self.location.exits.values():
                    if room.name == "Master Bedroom":
                        master_bedroom = room
                        break

                if master_bedroom:
                    self.location.connect("up", master_bedroom)  # Add the exit

                key = Item("Golden Key", "Unlocks the front door", 0, 1, True)
                self.location.items.append(key)
                self.solved_puzzles.add("basement_solved")


#=================================================================================================================================#

# Status Bar

    def show_status(self): # Done by Adish
        print(f"\n📍 You are in the {self.location.name}.")
        print("")
        print("🚪 Exits: ")
        for direction, room in self.location.exits.items():
             print(f"- {direction.capitalize()} to {room.name}")
        print("")
        print("🗄️ Places to search:", ', '.join(self.location.containers))
        print("")
        print(f"⏳ Time left: {self.time_left} minutes")
        print(f"🎒 Inventory: {self.inventory_slots()}/{self.max_slots} slots used")
        print("")
        
#=================================================================================================================================#
# Help Screen which shows the users all the funcitons   
    
    def show_help(self): # Rajat did story, Shlok did objectives, Adish did controls and the tips section was done by all of us
        print("""
        === Shadow Heist - Help ===

        🕵️ STORY: 
        You are a professional thief, known only as "Shadow". After weeks of surveillance, 
        you’ve chosen the perfect time to strike — the owners of this wealthy home leave 
        for an exact 2-hour walk each evening. You have 120 minutes to loot as much as you 
        can and escape before they return.

        🎯 OBJECTIVE: - 
        Explore the house, steal valuable items, and escape through the front door before 
        time runs out. Your bag has a limited capacity — 10 slots. Some items take more 
        than 1 slot (like the laptop or gold bars). Plan wisely.

        🕹️ CONTROLS:
        - Movement: north, south, east, west, up and down(for basement) (or n, s, e, w, u, d)
        - l / search [container] : View what’s inside a specific place
        - t / take [item]        : Take an item from a container or room
        - p / drop [item]        : Drop an item in the current room
        - u / use [item]         : Use usable items (e.g., bobby pin, key)
        - i / inventory          : View current items and slots used
        - h / help               : View this help screen
        - q / quit               : End the game

        💡 TIPS:
        - Use the crowbar in the bathroom to unlock the Master Bedroom.
        - Use the bobby pin to pick locks — enter the correct 3-letter direction code.
        - Use the key to unlock the front door and escape.

        Good luck, Shadow.
        """)

#=================================================================================================================================#  
# End game Function   
    
    def end_game(self, escaped): # Done by Rajat
        print("\n=== GAME OVER ===")
        
        total_value = sum(item.value for item in self.inventory)
        
        if escaped:
            print("Congratulations! You escaped successfully!")
            print(f"You stole items worth ${total_value}!")
            
            if total_value >= 20000:
                print("Legendary heist! You're a master thief!")
            elif total_value >= 10000:
                print("Great score! The criminal underworld will respect this.")
            elif total_value >= 5000:
                print("Decent haul. You'll live comfortably for a while.")
            else:
                print("Barely worth the risk. Better luck next time.")
        else:
            if self.time_left <= 0:
                print("Time's up! The homeowners caught you!")
            else:
                print("You were caught!")
            
            print(f"You managed to gather ${total_value} worth of loot before getting caught.")
        
        print("\nThanks for playing Shadow Heist!")
        exit()

#=================================================================================================================================#

# Function to create rooms and its location in the map

def create_world(): # Done by Shlok and Adish
    # Create all rooms
    bedroom2 = Room("Bedroom #2", "A modest bedroom with a window you entered through. The bed is neatly made.")
    kitchen = Room("Kitchen", "A modern kitchen with stainless steel appliances. The oven looks interesting.")
    living_room = Room("Living Room", "An elegant living area with expensive-looking furniture. A painting catches your eye.")
    bathroom = Room("Bathroom", "A luxurious bathroom with marble finishes. The sink cabinet might contain something.")
    master_bedroom = Room("Master Bedroom", "The opulent master suite. The door is locked, and a large mirror hangs on the wall.", True)
    laundry = Room("Laundry Room", "A utility room with washer, dryer, and storage shelves.")
    garage = Room("Garage", "A cluttered space with tools and boxes. A wooden chest sits in the corner.")
    study = Room("Study", "A home office with a desk and bookshelves. Looks like someone works here.")
    basement = Room("Basement", "A dark, mysterious basement. An ancient statue stands in the center.", True)
    
    # Connect rooms through directions by taking arguments - Done by Shlok and Adish
    bedroom2.connect('south', kitchen)
    
    kitchen.connect('north', bedroom2)
    kitchen.connect('south', master_bedroom)
    kitchen.connect('west', living_room)
    
    living_room.connect('east', kitchen)
    living_room.connect('south', bathroom)
    living_room.connect('west', study)
    living_room.connect('north', Room("Exit", "The front door to freedom!", True))  # Locked until solved (Won't be solved with toilet key.)
    
    bathroom.connect('north', living_room)
    bathroom.connect('east', master_bedroom)
    bathroom.connect('west', laundry)
    
    master_bedroom.connect('north', kitchen)
    master_bedroom.connect('west', bathroom)
    master_bedroom.connect('down', basement)
    basement.locked = True
    
    laundry.connect('east', bathroom)
    
    garage.connect('south', study)
    
    study.connect('north', garage)
    study.connect('east', living_room)
    
    # Add items to their respective rooms - Done by Shlok and Adish
    # It uses the class item which has the attributes name, description, value, inventory slots and if it can be used in a puzzle.
    bedroom2.items = [
        Item("Bobby Pin", "Could be useful for picking locks", 0, 1, True)
    ]
    
    kitchen.items = [
        Item("Cutlery Set", "Silver cutlery, not very valuable", 40, 1),
        Item("Old Food", "Expired and smelly", 0, 1)
    ]
    
    living_room.items = [
        Item("Painting", "A small but valuable artwork with the direction order of NSE", 450, 2),
        Item("Phone", "An old smartphone", 800, 1)
    ]
    
    bathroom.items = [
        Item("Ruby Ring", "A beautiful gemstone ring", 1100, 1),
        Item("Silver Key", "A mysterious key, might be used to unlock the front door", 0, 1, True)
    ]
    
    garage.items = [
        Item("Rusty Broken Wrench", "Useless junk", 0, 1)
    ]
    
    study.items = [
        Item("Laptop", "A high-end business laptop", 2100, 2),
        Item("Backpack", "A worthless bag. Might be be useful for extra space", 0, 0,),
        Item("Pencil Case", "Just ordinary pencils", 0, 1)
    ]
    
    # Add containers with hidden items
    bedroom2.containers = {
        "bedside table": [Item("Bobby Pin", "Could be useful for picking locks", 0, 1, True)],
        "wardrobe": [],
        "bookshelf": []
    }

    basement.containers = {
        "ancient statue": [],
        "broken bricks": [Item("Red Rune", "...", 0, 1, True)],
        "dusty corner": [Item("Blue Rune", "...", 0, 1, True)],
        "wooden crate": [Item("Sword", "...", 0, 2, True)],
        "cracked wall": [],  # Only this wall exists initially
        "hidden alcove": []
        }
    
    master_bedroom.containers = {
        "bedside table (inside)": [],
        "mirror": [],
        "wardrobe": [Item("Mini Safe", "A small safe needing a 4-digit code", 0, 0, False, False)]
    }
    
    kitchen.containers = {
        "fridge": [Item("Old Food", "Expired and smelly", 0, 1)],
        "oven": [Item("Monkey Statue", "An ornate statue", 900, 1, False, True)],
        "drawers": [Item("Cutlery Set", "Silver cutlery", 40, 1)]
    }
    
    living_room.containers = {
        "sofa": [Item("Phone", "An old smartphone", 800, 1)],
        "painting": [Item("Painting", "A small but valuable artwork with the direction order of NSE", 450, 2)],
        "digital clock": []
    }
    
    laundry.containers = {
        "top shelves": [],
        "clothes": [Item("Wallet", "Contains some cash", 100, 1)],
        "washing machine": [],
        "bottom shelves": [Item("Crowbar", "Could force open locked doors", 0, 2, True)]
    }
    
    garage.containers = {
        "tool box": [],
        "wooden chest": [Item("Key", "Unlocks the Master Bedroom", 0, 1, True, True)],
        "garage storage": [Item("Rusty Broken Wrench", "Useless junk", 0, 1)]
    }
    
    study.containers = {
        "study table": [Item("Pencil Case", "Just ordinary pencils", 0, 1)],
        "drawer": [Item("Laptop", "A high-end business laptop", 2100, 2)],
        "shelf": [Item("Backpack", "A useful item that might allow extra inventory slots", 0, 0)]
    }
    
    bathroom.containers = {
        "toilet": [],
        "sink": [Item("Ruby Ring", "A beautiful gemstone ring", 1100, 1)],
        "sink cabinet": [Item("Silver Key", "A mysterious key, might be used to unlock the front door", 0, 1, True)]
    }
    
    # Special items
    master_bedroom.items = [
        Item("Diamond Necklace", "A sparkling necklace (in safe)", 7000, 1, False, True)
    ]

    basement.items = [
        Item("Ancient Statue", "A mysterious statue with outstretched hands", 0, 0, False),
        Item("Red Rune", "A glowing red rune", 0, 1, True),
        Item("Blue Rune", "A glowing blue rune", 0, 1, True),
        Item("Sword", "An ancient-looking sword", 0, 2, True),
        Item("Golden Key", "Might be the real key to unlock the front door", 0, 1, True, True)
    ]
    
    return bedroom2  # Starting room

#=================================================================================================================================#

# Game loop: Input from user - Commands

def play(): # Done by Rajat, Shlok and Adish
    print("""
                                SHADOW HEIST 
    
    You are 'Shadow', a professional thief. After weeks of surveillance, you've found
    the perfect time to strike - the homeowners are away for exactly 2 hours.
    
    Objective:
    - Loot as many valuables as you can
    - Solve puzzles to access hidden areas
    - Escape before time runs out
          
    🕹️ CONTROLS:
    - Movement: north, south, east, west, up and down(for basement) (or n, s, e, w, u, d)
    - search [container] : View what’s inside a specific place
    - take [item]        : Take an item from a container or room
    - drop [item]        : Drop an item in the current room
    - use [item]         : Use usable items (e.g., bobby pin, key)
    - i / inventory      : View current items and slots used
    - h / help           : View this help screen
    - q / quit           : End the game
    
    You start in Bedroom #2. Good luck!
    """)
    
    starting_room = create_world()
    player = Player(starting_room)
    
    # Game loop
    while player.time_left > 0:
        player.show_status()
        
        try:
            command = input("\nWhat do you want to do? ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGame aborted.")
            return
        
        if not command:
            continue
            
        if command in ['n', 's', 'e', 'w', 'u', 'd', 
                      'north', 'south', 'east', 'west', 'up', 'down']:
            player.move(command)
        elif command.startswith('search '):
            container = command[7:]
            player.search(container)
        elif command.startswith('take '):
            item = command[5:]
            player.take(item)
        elif command.startswith('drop '):
            item = command[5:]
            player.drop(item)
        elif command.startswith('use '):
            item = command[4:]
            player.use(item)
        elif command in ['i', 'inv', 'inventory']:
            player.show_inventory()
        elif command in ['h', 'help']:
            player.show_help()
        elif command in ['q', 'quit', 'exit']:
            print("You abandon the heist and got caught trying to sneak out empty handed.")
            break
        else:
            print("Unknown command. Type 'help' or 'h' for instructions.")
    
    if player.time_left <= 0:
        player.end_game(False)

if __name__ == "__main__": 
    play()
    
