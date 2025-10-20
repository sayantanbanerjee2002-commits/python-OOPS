from abc import ABC, abstractmethod
import json


# INVENTORY CLASS (COMPOSITION) 
class Inventory: # manage weapone and items for a character
  
    def __init__(self):
        self.weapons = []  # List to store weapons
        self.items = []    # List to store items
    
    def add_weapon(self, weapon): # Add a weapon to inventory
        
        self.weapons.append(weapon)
        print(f"Added weapon: {weapon}")
    
    def add_item(self, item): # Add an item to inventory
      
        self.items.append(item)
        print(f"Added item: {item}")
    
    def show_inventory(self): # Display all items in Inventory
        print("\n--- INVENTORY ---")
        print(f"Weapons: {', '.join(self.weapons) if self.weapons else 'None'}")
        print(f"Items: {', '.join(self.items) if self.items else 'None'}")


# ABSTRACT CHARACTER CLASS 
class Character(ABC): # Abstaract class for all characters
    
    def __init__(self, name, health=100, level=1, experience=0):
        self.name = name
        self._health = health      # Private variable represented by  underscore
        self._max_health = health  # Maximum health limit
        self.level = level
        self.experience = experience
        self.inventory = Inventory()  # call inventory method
    
    # PROPERTY DECORATOR FOR HEALTH :
    @property
    def health(self): # use health method as a variable 
        return self._health
    
    @health.setter
    def health(self, value):
       # set the value of health between 0 to maximum_health
        if value < 0:
            self._health = 0  # Cannot go below 0
        elif value > self._max_health:
            self._health = self._max_health  # Cannot exceed maximum
        else:
            self._health = value
    
    #  ABSTRACT METHOD (MUST BE IMPLEMENTED BY SUBCLASSES)
    @abstractmethod
    def special_ability(self):
        """Each character class must implement their unique special ability"""
        pass
    
    #  COMMON METHODS :
    def attack(self):
        """Basic attack method"""
        damage = 10 + (self.level * 2)
        print(f"{self.name} attacks for {damage} damage!")
        return damage
    
    def defend(self, damage): # Defend against incoming danger ,health value reduce 
      
        print(f"{self.name} is defending against {damage} damage!")
        self.health -= damage  # Uses property setter automatically
        print(f"{self.name}'s health: {self.health}/{self._max_health}")
    
    def level_up(self):
        """Increase character level and stats"""
        self.level += 1
        self._max_health += 20  # Increase max health
        self.health = self._max_health  # Restore to full health
        print(f" {self.name} leveled up to Level {self.level}!")
        print(f"Max health increased to {self._max_health}")
    
    def gain_experience(self, exp):
        """Add experience and level up if threshold reached"""
        self.experience += exp
        print(f"{self.name} gained {exp} experience! Total: {self.experience}")
        
        # Level up every 100 experience points
        if self.experience >= self.level * 100:
            self.level_up()
    
    # OPERATOR OVERLOADING (+) 
    def __add__(self, other): # combine two character states 
       
        if not isinstance(other, Character):
            raise TypeError("Can only add two Character objects")
        
        # Create a new combined character (generic type)
        combined_name = f"{self.name}+{other.name}"
        combined_health = self.health + other.health
        combined_level = (self.level + other.level) // 2  # Average level
        combined_exp = self.experience + other.experience
        
        # Create a temporary Warrior 
        combined = Warrior(combined_name, combined_health, combined_level, combined_exp)
        print(f"\n Combined {self.name} and {other.name} into {combined_name}!")
        return combined
    
    # CLASS METHOD TO LOAD FROM FILE 
    @classmethod
    def from_save_file(cls, filename): # class method to create character from JSON file
     
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            
            # Determine character type and create appropriate instance
            char_type = data.get('type', 'Warrior')
            
            if char_type == 'Warrior':
                character = Warrior(
                    data['name'],
                    data['health'],
                    data['level'],
                    data['experience']
                )
                character.strength = data.get('strength', 50)
                character.armor = data.get('armor', 30)
            
            elif char_type == 'Mage':
                character = Mage(
                    data['name'],
                    data['health'],
                    data['level'],
                    data['experience']
                )
                character.mana = data.get('mana', 100)
                character.spell_power = data.get('spell_power', 60)
            
            elif char_type == 'Archer':
                character = Archer(
                    data['name'],
                    data['health'],
                    data['level'],
                    data['experience']
                )
                character.agility = data.get('agility', 70)
                character.accuracy = data.get('accuracy', 80)
            
            print(f" Loaded {char_type} '{data['name']}' from {filename}")
            return character
        
        except FileNotFoundError:
            print(f" Error: File '{filename}' not found")
            return None
        except json.JSONDecodeError:
            print(f" Error: Invalid JSON format in '{filename}'")
            return None
    
    def save_to_file(self, filename):
        """Save character data to JSON file"""
        data = {
            'type': self.__class__.__name__,
            'name': self.name,
            'health': self.health,
            'level': self.level,
            'experience': self.experience
        }
        
        # Add class-specific attributes
        if isinstance(self, Warrior):
            data['strength'] = self.strength
            data['armor'] = self.armor
        elif isinstance(self, Mage):
            data['mana'] = self.mana
            data['spell_power'] = self.spell_power
        elif isinstance(self, Archer):
            data['agility'] = self.agility
            data['accuracy'] = self.accuracy
        
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f" Saved {self.name} to {filename}")
    
    def show_stats(self):
        """Display character statistics"""
        print(f"\n{'='*40}")
        print(f"CHARACTER: {self.name}")
        print(f"{'='*40}")
        print(f"Health: {self.health}/{self._max_health}")
        print(f"Level: {self.level}")
        print(f"Experience: {self.experience}")


#  WARRIOR CLASS :
class Warrior(Character):
    """
    Warrior character - strong melee fighter
    """
    
    def __init__(self, name, health=100, level=1, experience=0, strength=50, armor=30):
        super().__init__(name, health, level, experience)  # Call parent constructor
        self.strength = strength
        self.armor = armor
    
    def special_ability(self):
        """Warrior's special ability: Heavy Strike"""
        damage = self.strength * 2 + self.level * 5
        print(f" {self.name} uses HEAVY STRIKE!")
        print(f"   Deals {damage} massive damage!")
        return damage
    
    def show_stats(self):
        """Override to show Warrior-specific stats"""
        super().show_stats()
        print(f"Strength: {self.strength}")
        print(f"Armor: {self.armor}")
        print(f"Class: Warrior")


# MAGE CLASS 
class Mage(Character):
    """
    Mage character - magical spellcaster
    """
    
    def __init__(self, name, health=80, level=1, experience=0, mana=100, spell_power=60):
        super().__init__(name, health, level, experience)
        self.mana = mana
        self.spell_power = spell_power
    
    def special_ability(self):
        """Mage's special ability: Fireball"""
        if self.mana >= 20:
            damage = self.spell_power * 1.5 + self.level * 3
            self.mana -= 20
            print(f" {self.name} casts FIREBALL!")
            print(f"   Deals {damage} fire damage! (Mana: {self.mana})")
            return damage
        else:
            print(f" {self.name} doesn't have enough mana!")
            return 0
    
    def show_stats(self):
        """Override to show Mage-specific stats"""
        super().show_stats()
        print(f"Mana: {self.mana}")
        print(f"Spell Power: {self.spell_power}")
        print(f"Class: Mage")


# ARCHER CLASS :
class Archer(Character):
    """
    Archer character - agile ranged attacker
    """
    
    def __init__(self, name, health=90, level=1, experience=0, agility=70, accuracy=80):
        super().__init__(name, health, level, experience)
        self.agility = agility
        self.accuracy = accuracy
    
    def special_ability(self):
        """Archer's special ability: Multi-Shot"""
        num_arrows = 3
        damage_per_arrow = (self.agility + self.accuracy) // 10 + self.level * 2
        total_damage = damage_per_arrow * num_arrows
        print(f" {self.name} uses MULTI-SHOT!")
        print(f"   Fires {num_arrows} arrows for {damage_per_arrow} damage each!")
        print(f"   Total damage: {total_damage}")
        return total_damage
    
    def show_stats(self):
        """Override to show Archer-specific stats"""
        super().show_stats()
        print(f"Agility: {self.agility}")
        print(f"Accuracy: {self.accuracy}")
        print(f"Class: Archer")


# TESTING :
if __name__ == "__main__":
    print(" RPG CHARACTER SYSTEM DEMO\n")
    
    # 1. Create characters
    print(" Creating Characters:")
    warrior = Warrior("Vhim", strength=60, armor=40)
    mage = Mage("Ben 10", mana=120, spell_power=70)
    archer = Archer("Raju", agility=80, accuracy=90)
    
    # 2. Show stats
    print("\n Character Stats:")
    warrior.show_stats()
    mage.show_stats()
    archer.show_stats()
    
    # 3. Test attacks
    print("\n Testing Attacks:")
    warrior.attack()
    mage.attack()
    archer.attack()
    
    # 4. Test special abilities
    print("\n Testing Special Abilities:")
    warrior.special_ability()
    mage.special_ability()
    archer.special_ability()
    
    # 5. Test defend
    print("\n Testing Defend:")
    warrior.defend(30)
    mage.defend(25)
    
    # 6. Test health property (cannot go below 0)
    print("\n Testing Health Property:")
    print(f"Warrior health: {warrior.health}")
    warrior.health = -50  # Try to set negative
    print(f"After setting to -50: {warrior.health} (stays at 0)")
    warrior.health = 200  # Try to exceed max
    print(f"After setting to 200: {warrior.health} (capped at max)")
    
    # 7. Test experience and leveling
    print("\n Testing Experience & Leveling:")
    warrior.gain_experience(120)
    
    # 8. Test inventory
    print("\n Testing Inventory:")
    warrior.inventory.add_weapon("Sword of Destiny")
    warrior.inventory.add_weapon("Shield of Valor")
    warrior.inventory.add_item("Health Potion")
    warrior.inventory.show_inventory()
    
    # 9. Test operator overloading (+)
    print("\n Testing Operator Overloading (+):")
    combined = warrior + mage
    combined.show_stats()
    
    # 10. Test save/load
    print("\n Testing Save/Load:")
    archer.save_to_file("archer_save.json")
    loaded_archer = Character.from_save_file("archer_save.json")
    if loaded_archer:
        loaded_archer.show_stats()
    
    print("\n Demo Complete!")