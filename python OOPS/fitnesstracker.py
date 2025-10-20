from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class Workout(ABC): # Represent Abstract Base Class
    """
    Abstract base class for all workout types.
    """
    def __init__(self, date: str, duration: int, calories_burned: float):
     # Intialize common workout attributes
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.duration = duration  # in minutes
        self.calories_burned = calories_burned
    
    @abstractmethod
    def get_workout_summary(self) -> str:
        """Abstract method - must be implemented by all subclasses"""
        pass
    
    def __str__(self) -> str:
        """String representation of workout"""
        return f"Date: {self.date.strftime('%Y-%m-%d')}, Duration: {self.duration} mins, Calories: {self.calories_burned}"


# WORKOUT TYPES:-
class Running(Workout):
    """Represents a running workout"""
    
    def __init__(self, date: str, duration: int, calories_burned: float, 
                 distance: float, pace: float, terrain: str):
        """
        Initialize running workout.
        """
        super().__init__(date, duration, calories_burned)
        self.distance = distance  # in km
        self.pace = pace  # min/km
        self.terrain = terrain
    
    def get_workout_summary(self) -> str:
        """Return detailed running summary"""
        return (f" RUNNING: {self.distance}km at {self.pace} min/km pace "
                f"({self.terrain} terrain) - {self.calories_burned} cal")
    
    def __add__(self, other):
        """Operator overloading: combine two running workouts"""
        if isinstance(other, Running):
            return {
                'total_duration': self.duration + other.duration,
                'total_distance': self.distance + other.distance,
                'total_calories': self.calories_burned + other.calories_burned,
                'avg_pace': (self.pace + other.pace) / 2
            }
        return NotImplemented


class Cycling(Workout):
    """Represents a cycling workout"""
    
    def __init__(self, date: str, duration: int, calories_burned: float,
                 distance: float, speed: float, resistance_level: int):
        """
        Initialize cycling workout.
        """
        super().__init__(date, duration, calories_burned)
        self.distance = distance
        self.speed = speed  # km/h
        self.resistance_level = resistance_level
    
    def get_workout_summary(self) -> str:
        """Return detailed cycling summary"""
        return (f" CYCLING: {self.distance}km at {self.speed} km/h "
                f"(Resistance: {self.resistance_level}) - {self.calories_burned} cal")
    
    def __add__(self, other):
        """Operator overloading: combine two cycling workouts"""
        if isinstance(other, Cycling):
            return {
                'total_duration': self.duration + other.duration,
                'total_distance': self.distance + other.distance,
                'total_calories': self.calories_burned + other.calories_burned,
                'avg_speed': (self.speed + other.speed) / 2
            }
        return NotImplemented


class Swimming(Workout):
    """Represents a swimming workout"""
    
    def __init__(self, date: str, duration: int, calories_burned: float,
                 laps: int, stroke_type: str, pool_length: int):
        """
        Initialize swimming workout.
        """
        super().__init__(date, duration, calories_burned)
        self.laps = laps
        self.stroke_type = stroke_type
        self.pool_length = pool_length  # in meters
    
    def get_workout_summary(self) -> str:
        """Return detailed swimming summary"""
        total_distance = (self.laps * self.pool_length) / 1000  # convert to km
        return (f" SWIMMING: {self.laps} laps ({total_distance:.2f}km) "
                f"using {self.stroke_type} - {self.calories_burned} cal")
    
    def __add__(self, other):
        """Operator overloading: combine two swimming workouts"""
        if isinstance(other, Swimming):
            return {
                'total_duration': self.duration + other.duration,
                'total_laps': self.laps + other.laps,
                'total_calories': self.calories_burned + other.calories_burned,
                'total_distance_km': ((self.laps * self.pool_length + 
                                      other.laps * other.pool_length) / 1000)
            }
        return NotImplemented


#  EXERCISE CLASS :-
class Exercise:
    """Represents an individual exercise in a gym session"""
    
    def __init__(self, name: str, muscle_group: str, difficulty: str, 
                 calories_per_minute: float):
        """
        Initialize an exercise.
        """
        self.name = name
        self.muscle_group = muscle_group
        self.difficulty = difficulty
        self.calories_per_minute = calories_per_minute
    
    def __str__(self) -> str:
        return f"{self.name} ({self.muscle_group}) - {self.difficulty}"


class GymSession(Workout):
    """
    Represents a gym workout session.
    Uses COMPOSITION: contains multiple Exercise objects.
    """
    
    def __init__(self, date: str, duration: int):
        """
        Initialize gym session.
        Calories will be calculated based on exercises added.
        """
        self.exercises_list: List[Tuple[Exercise, int, int, float]] = []  # (exercise, sets, reps, weight)
        super().__init__(date, duration, 0)  # calories calculated later
    
    def add_exercise(self, exercise: Exercise, sets: int, reps: int, weight: float):
        """
        Add an exercise to the gym session.
        """
        self.exercises_list.append((exercise, sets, reps, weight))
        # Calculate calories for this exercise
        exercise_duration = sets * reps * 0.05  # rough estimate: 3 seconds per rep
        self.calories_burned += exercise.calories_per_minute * exercise_duration
    
    def get_total_weight_lifted(self) -> float:
        """Calculate total weight lifted in session"""
        total = 0
        for exercise, sets, reps, weight in self.exercises_list:
            total += sets * reps * weight
        return total
    
    def get_workout_summary(self) -> str:
        """Return detailed gym session summary"""
        exercise_names = [ex[0].name for ex in self.exercises_list]
        total_weight = self.get_total_weight_lifted()
        return (f" GYM SESSION: {len(self.exercises_list)} exercises "
                f"({', '.join(exercise_names[:3])}...) - "
                f"Total weight: {total_weight}kg, {self.calories_burned:.1f} cal")
    
    def __add__(self, other):
        """Operator overloading: combine two gym sessions"""
        if isinstance(other, GymSession):
            return {
                'total_duration': self.duration + other.duration,
                'total_exercises': len(self.exercises_list) + len(other.exercises_list),
                'total_weight': self.get_total_weight_lifted() + other.get_total_weight_lifted(),
                'total_calories': self.calories_burned + other.calories_burned
            }
        return NotImplemented


# NUTRITION LOG :-
class NutritionLog:
    """Tracks daily nutrition and meals"""
    
    def __init__(self, date: str, meal_time: str):
        """
        Initialize nutrition log.
        """
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.meal_time = meal_time
        self.food_items: List[str] = []
        self.calories = 0
        self.macros = {'protein': 0, 'carbs': 0, 'fat': 0}  # in grams
    
    def add_food(self, food_name: str, calories: float, protein: float, 
                 carbs: float, fat: float):
        """
        Add a food item to the meal.
        """
        self.food_items.append(food_name)
        self.calories += calories
        self.macros['protein'] += protein
        self.macros['carbs'] += carbs
        self.macros['fat'] += fat
    
    def __str__(self) -> str:
        return (f"{self.meal_time} on {self.date.strftime('%Y-%m-%d')}: "
                f"{', '.join(self.food_items)} - {self.calories} cal "
                f"(P:{self.macros['protein']}g C:{self.macros['carbs']}g F:{self.macros['fat']}g)")


# USER CLASS :-
class User:
    """
    Represents a fitness app user.
    Contains workout history and personal information.
    """
    
    def __init__(self, name: str, age: int, weight: float, height: float, 
                 fitness_goal: str):
        """
        Initialize user profile.
        """
        self.name = name
        self.age = age
        self.weight = weight  # in kg
        self.height = height  # in cm
        self.fitness_goal = fitness_goal
        self.workout_history: List[Workout] = []
        self.nutrition_logs: List[NutritionLog] = []
    
    def calculate_bmi(self) -> float:
        """
        Calculate Body Mass Index.
        Formula: BMI = weight(kg) / (height(m))^2
        """
        height_m = self.height / 100  # convert cm to meters
        bmi = self.weight / (height_m ** 2)
        return round(bmi, 2)
    
    def get_bmi_category(self) -> str:
        """Get BMI category based on WHO standards"""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def calculate_recommended_calories(self) -> int:
        """
        Calculate recommended daily calorie intake
        """
        # Calculate Basal Metabolic Rate (BMR)
        bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        
        # Adjust based on fitness goal
        if self.fitness_goal == "weight_loss":
            return int(bmr * 1.2 - 500)  # deficit for weight loss
        elif self.fitness_goal == "muscle_gain":
            return int(bmr * 1.5 + 300)  # surplus for muscle gain
        else:  # endurance or maintenance
            return int(bmr * 1.4)
    
    def add_workout(self, workout: Workout):
        """Add a workout to user's history"""
        self.workout_history.append(workout)
    
    def add_nutrition_log(self, nutrition_log: NutritionLog):
        """Add a nutrition log to user's history"""
        self.nutrition_logs.append(nutrition_log)
    
    def compare_workouts(self, workout_type: type) -> Dict:
        """
        Compare current vs previous workout of same type.
        Shows progress tracking.
        """
        workouts_of_type = [w for w in self.workout_history if isinstance(w, workout_type)]
        
        if len(workouts_of_type) < 2:
            return {"message": "Not enough workouts to compare"}
        
        # Get last two workouts
        previous = workouts_of_type[-2]
        current = workouts_of_type[-1]
        
        comparison = {
            'previous_date': previous.date.strftime('%Y-%m-%d'),
            'current_date': current.date.strftime('%Y-%m-%d'),
            'duration_change': current.duration - previous.duration,
            'calories_change': current.calories_burned - previous.calories_burned
        }
        
        # Type-specific comparisons
        if workout_type == Running:
            comparison['distance_change'] = current.distance - previous.distance
            comparison['pace_change'] = current.pace - previous.pace
        elif workout_type == Cycling:
            comparison['distance_change'] = current.distance - previous.distance
            comparison['speed_change'] = current.speed - previous.speed
        elif workout_type == Swimming:
            comparison['laps_change'] = current.laps - previous.laps
        elif workout_type == GymSession:
            comparison['weight_change'] = (current.get_total_weight_lifted() - 
                                          previous.get_total_weight_lifted())
        
        return comparison
    
    def generate_weekly_report(self) -> Dict:
        """
        Generate weekly workout report.
        Shows last 7 days of activity.
        """
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        # Filter workouts from last week
        weekly_workouts = [w for w in self.workout_history 
                          if w.date >= week_ago and w.date <= today]
        
        if not weekly_workouts:
            return {"message": "No workouts in the last week"}
        
        # Calculate statistics
        total_duration = sum(w.duration for w in weekly_workouts)
        total_calories = sum(w.calories_burned for w in weekly_workouts)
        workout_types = {}
        
        for workout in weekly_workouts:
            workout_type = type(workout).__name__
            workout_types[workout_type] = workout_types.get(workout_type, 0) + 1
        
        return {
            'period': f'{week_ago.strftime("%Y-%m-%d")} to {today.strftime("%Y-%m-%d")}',
            'total_workouts': len(weekly_workouts),
            'total_duration_minutes': total_duration,
            'total_calories_burned': round(total_calories, 1),
            'workout_breakdown': workout_types,
            'avg_calories_per_workout': round(total_calories / len(weekly_workouts), 1)
        }
    
    def generate_monthly_report(self) -> Dict:
        """
        Generate monthly workout report.
        Shows last 30 days of activity.
        """
        today = datetime.now()
        month_ago = today - timedelta(days=30)
        
        # Filter workouts from last month
        monthly_workouts = [w for w in self.workout_history 
                           if w.date >= month_ago and w.date <= today]
        
        if not monthly_workouts:
            return {"message": "No workouts in the last month"}
        
        # Calculate statistics
        total_duration = sum(w.duration for w in monthly_workouts)
        total_calories = sum(w.calories_burned for w in monthly_workouts)
        workout_types = {}
        
        for workout in monthly_workouts:
            workout_type = type(workout).__name__
            workout_types[workout_type] = workout_types.get(workout_type, 0) + 1
        
        # Calculate weekly average
        weeks = 4
        avg_workouts_per_week = len(monthly_workouts) / weeks
        
        return {
            'period': f'{month_ago.strftime("%Y-%m-%d")} to {today.strftime("%Y-%m-%d")}',
            'total_workouts': len(monthly_workouts),
            'total_duration_minutes': total_duration,
            'total_duration_hours': round(total_duration / 60, 1),
            'total_calories_burned': round(total_calories, 1),
            'workout_breakdown': workout_types,
            'avg_workouts_per_week': round(avg_workouts_per_week, 1),
            'avg_calories_per_workout': round(total_calories / len(monthly_workouts), 1)
        }
    
    def track_goal_progress(self) -> Dict:
        """
        Track progress towards fitness goal.
        Provides insights based on goal type.
        """
        if not self.workout_history:
            return {"message": "No workout data available"}
        
        weekly_report = self.generate_weekly_report()
        
        if self.fitness_goal == "weight_loss":
            recommended_cal = self.calculate_recommended_calories()
            weekly_calories_burned = weekly_report.get('total_calories_burned', 0)
            
            return {
                'goal': 'Weight Loss',
                'bmi': self.calculate_bmi(),
                'bmi_category': self.get_bmi_category(),
                'recommended_daily_calories': recommended_cal,
                'weekly_calories_burned': weekly_calories_burned,
                'weekly_calorie_deficit': weekly_calories_burned,
                'estimated_weight_loss_kg': round(weekly_calories_burned / 7700, 2),  # 1kg ≈ 7700 cal
                'recommendation': 'Keep maintaining calorie deficit with regular cardio'
            }
        
        elif self.fitness_goal == "muscle_gain":
            gym_sessions = [w for w in self.workout_history if isinstance(w, GymSession)]
            if gym_sessions:
                avg_weight = sum(w.get_total_weight_lifted() for w in gym_sessions[-4:]) / min(len(gym_sessions), 4)
                return {
                    'goal': 'Muscle Gain',
                    'bmi': self.calculate_bmi(),
                    'recommended_daily_calories': self.calculate_recommended_calories(),
                    'weekly_gym_sessions': weekly_report.get('workout_breakdown', {}).get('GymSession', 0),
                    'avg_weight_lifted_recent': round(avg_weight, 1),
                    'recommendation': 'Focus on progressive overload and protein intake (2g per kg bodyweight)'
                }
        
        elif self.fitness_goal == "endurance":
            cardio_workouts = [w for w in self.workout_history 
                              if isinstance(w, (Running, Cycling, Swimming))]
            if cardio_workouts:
                avg_duration = sum(w.duration for w in cardio_workouts[-5:]) / min(len(cardio_workouts), 5)
                return {
                    'goal': 'Endurance',
                    'weekly_cardio_sessions': len([w for w in self.workout_history[-7:] 
                                                   if isinstance(w, (Running, Cycling, Swimming))]),
                    'avg_workout_duration': round(avg_duration, 1),
                    'recommendation': 'Gradually increase workout duration by 10% each week'
                }
        
        return {"message": "Goal tracking data unavailable"}


#  DEMO USAGE :-
def demo_fitness_tracker():
    """Demonstration of the fitness tracker system"""
    
    print("=" * 60)
    print("FITNESS & WORKOUT TRACKER DEMO")
    print("=" * 60)
    
    # Create a user
    user = User(
        name="Sayantan Banerjee",
        age=22,
        weight=70,
        height=172,
        fitness_goal="muscle_gain"
    )
    
    print(f"\n USER PROFILE: {user.name}")
    print(f"Age: {user.age}, Weight: {user.weight}kg, Height: {user.height}cm")
    print(f"BMI: {user.calculate_bmi()} ({user.get_bmi_category()})")
    print(f"Recommended Daily Calories: {user.calculate_recommended_calories()} cal")
    print(f"Fitness Goal: {user.fitness_goal}")
    
    # Create exercises for gym session
    bench_press = Exercise("Bench Press", "Chest", "Medium", 7.5)
    squats = Exercise("Squats", "Legs", "Hard", 8.0)
    deadlift = Exercise("Deadlift", "Back", "Hard", 8.5)
    
    # Create workouts
    print("\n" + "=" * 60)
    print("ADDING WORKOUTS")
    print("=" * 60)
    
    # Running workout
    run1 = Running(
        date="2024-10-10",
        duration=45,
        calories_burned=450,
        distance=6.0,
        pace=6.0,
        terrain="flat"
    )
    user.add_workout(run1)
    print(f"\n {run1.get_workout_summary()}")
    
    # Cycling workout
    cycle1 = Cycling(
        date="2024-10-12",
        duration=35,
        calories_burned=450,
        distance=25.0,
        speed=25.0,
        resistance_level=5
    )
    user.add_workout(cycle1)
    print(f" {cycle1.get_workout_summary()}")
    
    # Swimming workout
    swim1 = Swimming(
        date="2024-10-14",
        duration=20,
        calories_burned=340,
        laps=20,
        stroke_type="freestyle",
        pool_length=25
    )
    user.add_workout(swim1)
    print(f" {swim1.get_workout_summary()}")
    
    # Gym session with composition
    gym1 = GymSession(date="2024-10-16", duration=70)
    gym1.add_exercise(bench_press, sets=4, reps=12, weight=50)
    gym1.add_exercise(squats, sets=4, reps=15, weight=80)
    gym1.add_exercise(deadlift, sets=2, reps=10, weight=100)
    user.add_workout(gym1)
    print(f" {gym1.get_workout_summary()}")
    
    # Add another running workout for comparison
    run2 = Running(
        date="2024-10-18",
        duration=30,
        calories_burned=350,
        distance=5.5,
        pace=5.8,
        terrain="hilly"
    )
    user.add_workout(run2)
    print(f" {run2.get_workout_summary()}")
    
    # Operator overloading demo
    print("\n" + "=" * 60)
    print("OPERATOR OVERLOADING DEMO (+ operator)")
    print("=" * 60)
    combined_runs = run1 + run2
    print(f"\n Combined Running Stats:")
    for key, value in combined_runs.items():
        print(f"  {key}: {value}")
    
    # Nutrition logging
    print("\n" + "=" * 60)
    print("NUTRITION TRACKING")
    print("=" * 60)
    
    breakfast = NutritionLog(date="2024-10-18", meal_time="Breakfast")
    breakfast.add_food("Oatmeal", 300, 10, 54, 6)
    breakfast.add_food("Banana", 105, 1, 27, 0)
    user.add_nutrition_log(breakfast)
    print(f"\n {breakfast}")
    
    # Progress tracking
    print("\n" + "=" * 60)
    print("PROGRESS TRACKING (Running)")
    print("=" * 60)
    progress = user.compare_workouts(Running)
    print(f"\n Comparing {progress['previous_date']} vs {progress['current_date']}:")
    print(f"  Distance improvement: +{progress['distance_change']:.1f} km")
    print(f"  Pace improvement: {progress['pace_change']:.1f} min/km (negative is better)")
    print(f"  Calories burned change: +{progress['calories_change']:.1f} cal")
    
    # Weekly report
    print("\n" + "=" * 60)
    print("WEEKLY REPORT")
    print("=" * 60)
    weekly = user.generate_weekly_report()
    print(f"\n Period: {weekly['period']}")
    print(f"Total Workouts: {weekly['total_workouts']}")
    print(f"Total Duration: {weekly['total_duration_minutes']} minutes")
    print(f"Total Calories Burned: {weekly['total_calories_burned']} cal")
    print(f"Workout Breakdown: {weekly['workout_breakdown']}")
    
    # Goal tracking
    print("\n" + "=" * 60)
    print("GOAL PROGRESS")
    print("=" * 60)
    goal_progress = user.track_goal_progress()
    print(f"\n Goal: {goal_progress['goal']}")
    for key, value in goal_progress.items():
        if key != 'goal':
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)


# Run the demo
if __name__ == "__main__":
    demo_fitness_tracker()