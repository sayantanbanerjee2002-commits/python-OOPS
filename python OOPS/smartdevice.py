class SmartDevice:
    
    
    def __init__(self, name, brand, energy_consumption):
        
        self.name = name
        self.brand = brand
        self.power_status = False  # Device starts as OFF
        self.energy_consumption = energy_consumption  # in watts
    
    def turn_on(self): # turn the device on
        
        self.power_status = True
        print(f" {self.name} is now ON")
    
    def turn_off(self):# turn the device off
        
        self.power_status = False
        print(f" {self.name} is now OFF")
    
    def get_energy_cost(self, hours_per_day=24):
       
        if not self.power_status: # negatation logic is used
            return 0.0  # No cost if device is OFF
        
        kilowatts = self.energy_consumption / 1000
        daily_cost = kilowatts * hours_per_day * 0.12
        return round(daily_cost, 2)
    
    def __str__(self):
        
        status = "ON" if self.power_status else "OFF"
        return f"{self.name} ({self.brand}) - Status: {status}, Energy: {self.energy_consumption}W"


# Child Class 1 - Smart Light
class SmartLight(SmartDevice):
    
    
    def __init__(self, name, brand, energy_consumption, brightness=0, color="white"):
      # additional attributes are brightness ,color
        super().__init__(name, brand, energy_consumption)  # Call parent constructor
        self.brightness = brightness
        self.color = color
    
    def turn_on(self):
        
        self.power_status = True
        if self.brightness == 0:
            self.brightness = 50  # Set default brightness when turning on
        print(f" {self.name} is now ON at {self.brightness}% brightness ({self.color})")
    
    def turn_off(self):
        
        self.power_status = False
        print(f" {self.name} is now OFF")
    
    def set_brightness(self, level):#Set brightness level (0-100)
        
        if 0 <= level <= 100:
            self.brightness = level
            print(f"Brightness set to {level}%")
        else:
            print("Brightness must be between 0 and 100")
    
    def set_color(self, color):#Change light color
        
        self.color = color
        print(f"Color changed to {color}")
    
    def __str__(self):
        
        status = "ON" if self.power_status else "OFF"
        return f"{self.name} ({self.brand}) - Status: {status}, Brightness: {self.brightness}%, Color: {self.color}, Energy: {self.energy_consumption}W"


# Child Class 2 - Smart Thermostat
class SmartThermostat(SmartDevice):
   
    
    def __init__(self, name, brand, energy_consumption, temperature=72, mode="auto"):
        # additional attributes are temperture and mode
        super().__init__(name, brand, energy_consumption)
        self.temperature = temperature
        self.mode = mode
    
    def turn_on(self): # Turn on the thermostat
        
        self.power_status = True
        print(f"  {self.name} is now ON - Mode: {self.mode.upper()}, Target: {self.temperature}°F")
    
    def turn_off(self):# Turn off the thermostat
        
        self.power_status = False
        print(f"  {self.name} is now OFF")
    
    def set_temperature(self, temp): # set thermostat temperature
        
        if 60 <= temp <= 90:
            self.temperature = temp
            print(f"Temperature set to {temp}°F")
        else:
            print("Temperature must be between 60-90°F")
    
    def set_mode(self, mode): # set the mode of Thermostat
        
        if mode.lower() in ["heat", "cool", "auto"]:
            self.mode = mode.lower()
            print(f"Mode set to {self.mode.upper()}")
        else:
            print("Mode must be 'heat', 'cool', or 'auto'")
    
    def __str__(self):
        status = "ON" if self.power_status else "OFF"
        return f"  {self.name} ({self.brand}) - Status: {status}, Mode: {self.mode.upper()}, Temp: {self.temperature}°F, Energy: {self.energy_consumption}W"


# Child Class 3 - Smart Speaker
class SmartSpeaker(SmartDevice):
    
    
    def __init__(self, name, brand, energy_consumption, volume=0, current_song=None):
       # additional attributes are volume and current song
        super().__init__(name, brand, energy_consumption)
        self.volume = volume
        self.current_song = current_song
    
    def turn_on(self): # turn the speaker on
       
        self.power_status = True
        if self.volume == 0:
            self.volume = 30  # Set default volume when turning on
        song_info = f" Playing: {self.current_song}" if self.current_song else ""
        print(f"{self.name} is now ON - Volume: {self.volume}%{song_info}")
    
    def turn_off(self): # Turn the speaker off
        
        self.power_status = False
        self.current_song = None  # Stop playing when turned off
        print(f" {self.name} is now OFF")
    
    def set_volume(self, level):# Set volume level (0-100)
        
        if 0 <= level <= 100:
            self.volume = level
            print(f"Volume set to {level}%")
        else:
            print("Volume must be between 0 and 100")
    
    def play_song(self, song_name):
        """Play a song"""
        if self.power_status:
            self.current_song = song_name
            print(f" Now playing: {song_name}")
        else:
            print("Please turn on the speaker first")
    
    def __str__(self):
        
        status = "ON" if self.power_status else "OFF"
        song_info = f", Playing: {self.current_song}" if self.current_song else ", Idle"
        return f"{self.name} ({self.brand}) - Status: {status}, Volume: {self.volume}%{song_info}, Energy: {self.energy_consumption}W"



def main():
    """Demonstrate the smart home system"""
    
    print("=" * 60)
    print(" SMART HOME SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Create devices
    print("\n Creating Smart Devices...")
    light = SmartLight("Living Room Light", "Philips Hue", 10, brightness=0, color="white")
    thermostat = SmartThermostat("Main Thermostat", "Nest", 50, temperature=72, mode="auto")
    speaker = SmartSpeaker("Kitchen Speaker", "Amazon Echo", 15, volume=0)
    
    print(f"\n{light}")
    print(f"{thermostat}")
    print(f"{speaker}")
    
    # Turn on devices
    print("\n\n Turning ON Devices...")
    print("-" * 60)
    light.turn_on()
    thermostat.turn_on()
    speaker.turn_on()
    
    # Control devices
    print("\n\n  Controlling Devices...")
    print("-" * 60)
    light.set_brightness(80)
    light.set_color("warm yellow")
    
    thermostat.set_temperature(68)
    thermostat.set_mode("cool")
    
    speaker.set_volume(50)
    speaker.play_song("Dui prithibi")
    
    # Display updated status
    print("\n\n Current Device Status...")
    print("-" * 60)
    print(light)
    print(thermostat)
    print(speaker)
    
    # Calculate energy costs
    print("\n\n Daily Energy Costs (24 hours usage)...")
    print("-" * 60)
    print(f"{light.name}: ${light.get_energy_cost(24)}/day")
    print(f"{thermostat.name}: ${thermostat.get_energy_cost(24)}/day")
    print(f"{speaker.name}: ${speaker.get_energy_cost(24)}/day")
    
    total_cost = light.get_energy_cost(24) + thermostat.get_energy_cost(24) + speaker.get_energy_cost(24)
    print(f"\n Total Daily Cost: ${total_cost}")
    print(f"Monthly Cost: ${round(total_cost * 30, 2)}")
    
    # Turn off devices
    print("\n\n Turning OFF Devices...")
    print("-" * 60)
    light.turn_off()
    thermostat.turn_off()
    speaker.turn_off()
    
    print("\n" + "=" * 60)
    print(" Smart Home System Demo Complete!")
    print("=" * 60)


# Run the demonstration
if __name__ == "__main__":
    main()