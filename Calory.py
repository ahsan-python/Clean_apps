import json
import os
from datetime import date

DATA_FILE = "fitness_data.json"

# --- HELPER FUNCTIONS FOR 7-WEEK STORAGE ---
def load_data():
    """File se purana history load karta hai"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_daily_data(calories, protein, steps, water):
    """Aaj ka data JSON file mein lock/save karta hai"""
    data = load_data()
    today = str(date.today())
    
    # Existing entry updates or new entry
    data[today] = {
        "calories": calories,
        "protein_g": round(protein, 1),
        "steps": steps,
        "water_ml": water
    }
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print("\n✅ Today's progress saved to 7-Week History!")

def view_analytics():
    """7-Week History ko Table format mein display karta hai"""
    data = load_data()
    if not data:
        print("\n⚠️ No history recorded yet! Track a day first.")
        return

    print("\n" + "="*55)
    print("      📊 7-WEEK FITNESS & BULK HISTORY TABLE      ")
    print("="*55)
    print(f"| {'Date':<12} | {'Calories':<10} | {'Protein (g)':<12} | {'Steps':<7} |")
    print("-" * 55)
    
    # Reverse sort taaki latest date sab se upar aaye
    for entry_date in sorted(data.keys(), reverse=True):
        entry = data[entry_date]
        cal = entry.get('calories', 0)
        prot = entry.get('protein_g', 0)
        steps = entry.get('steps', 0)
        print(f"| {entry_date:<12} | {cal:<10} | {prot:<12} | {steps:<7} |")
        
    print("="*55)
def main():
  while True:   
        print("\n--- WELCOME TO CALORY APP ---")
        print("1. Calorie & Macro Tracker")
        print("2. Step Counter")
        print("3. Water Intake Tracker")
        print("4. Morning check")
        print("5. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            calorie_tracker()
        elif choice == '2':
            total_step_taken()
        elif choice == '3':
            total_water_intake()
        elif choice == '4':
             morning_check_in()
        elif choice =='5':
            print("You have exited the app.")
            break
        else:
          
            print("Invalid choice! Please select between 1 and 4.")

def calorie_tracker():
    while True:
        try:
            # 1. Goal choose karein aur target base set karein
            decision = input("\nBulk, Cut, or Maintain? (type 'bulk' / 'cut' / 'maintain'): ").strip().lower()

            if decision == 'bulk':
                calorie_intake = 2500
            elif decision == 'cut':
                calorie_intake = 1800
            elif decision == 'maintain':
                calorie_intake = 2000
            else:
                print("Invalid input! Defaulting to Maintenance (2000 kcal).")
                calorie_intake = 2000

            print(f"--> Your target for today is: {calorie_intake} kcal")

            # 2. Meals log karne ka simple Loop
            calories_total = 0
            while True:
                meal_input = input("\nEnter meal calories (or type 'done' to calculate macros): ").strip().lower()
                
                if meal_input == 'done':
                    break  # Logging loop se bahar niklo
                
                # Check karein agar valid number hai
                if meal_input.isdigit():
                    calories_total += int(meal_input)
                    print(f"Total so far: {calories_total} / {calorie_intake} kcal")
                else:
                    print("Please enter a valid number or 'done'.")

            # 3. Final Target Status Check
            print("\n--- FINAL SUMMARY ---")
            if calories_total >= calorie_intake:
                print(f"🔥 Target Hit! You ate {calories_total} kcal (Goal was {calorie_intake} kcal).")
            else:
                needed = calorie_intake - calories_total
                print(f"⚠️ Target Missed! You ate {calories_total} kcal. You are still lacking {needed} kcal.")

            # 4. Macro Split (30% Protein, 40% Carbs, 30% Fats)
            show_macros = input("\nDo you want to see macro breakdown? (Press 'Enter' for Yes / type 'exit' to quit): ").strip().lower()

            if show_macros == 'exit':
                print("Keep grinding! ⚔️")
                break

            protein_g = (calories_total * 0.30) / 4
            carbs_g = (calories_total * 0.40) / 4
            fats_g = (calories_total * 0.30) / 9

            print(f"\n--- MACRO BREAKDOWN ({calories_total} kcal) ---")
            print(f"Protein : {protein_g:.1f}g")
            print(f"Carbs   : {carbs_g:.1f}g")
            print(f"Fats    : {fats_g:.1f}g")
            print("------------------------------------------")

            # Track end condition
            again = input("\nDo you want to track another day? (yes/no): ").strip().lower()
            if again != 'yes':
                print("System Offline. Stay consistent, warrior! ⚔️🔥")
                break

        except ValueError:
            print("Error! Please enter numbers only for calories.")





# --- FEATURE 2: STEP COUNTER (Tumhara Exact Code) ---
def total_step_taken(step=3000):
    steps_taken = int(input("Please write the number of steps taken:"))
    while steps_taken < step:
     remaining_steps = step - steps_taken
     more_steps = int(input(f"You are left with {remaining_steps}.Add more:"))
     steps_taken += more_steps

    print("You have completed your steps.")

    calories_burned = 0.0
    for _ in range(0, steps_taken, 10):
        calories_burned += 0.4
    calories_burned = round(calories_burned, 2)
    print(f"You have burned {calories_burned:.2f} calories!!")  
    
    total_distance_covered = steps_taken * .5
    print(f"You have covered {total_distance_covered}m")


# --- FEATURE 3: WATER INTAKE (Tumhara Exact Code) ---
def total_water_intake(water_goal=3000):
    water_added = int(input("Please enter how many ml of water you have consumed: "))
    total_consumed = water_added

    # Jab tak goal poora nahi hota, loop chalega
    while total_consumed < water_goal:
        remaining_water = water_goal - total_consumed
        print(f"You have left with {remaining_water}ml to reach your goal.")
        
        water_added = int(input("Add more water: "))
        total_consumed += water_added

    # Agar add karne ke baad goal hit ya exceed ho gaya, toh loop yahan rok do
    if total_consumed >= water_goal:
        print(f"Goal already reached! Total consumed: {total_consumed}ml. Congratulations! 🎉")
        return total_consumed
            

    print(f"You have completed your water intake! Total consumed today: {total_consumed}ml. Congratulations! 🎉")
  def morning_check_in():
    while True:
        try:
            sleep_time = float(input("Enter your total sleep time last night (hours): "))
            
            # Range logic matching our 8-hour target system
            if 7.5 <= sleep_time <= 10.0:
                print("Status: Peak Anabolic State 🔥 (Optimal 8h Sleep achieved)")
                break  # Successful input, exit the check-in loop
            elif 6.0 <= sleep_time < 7.5:
                print("Status: Moderate ⚡ (Slightly less sleep, keep intensity in check)")
                break
            elif 3.0 <= sleep_time < 6.0:
                print("Status: CNS Fatigue Warning ⚠️ (Low sleep. Prioritize form today)")
                break
            elif 0.0 <= sleep_time < 3.0:
                print("Status: Critical Alert 🛑 (Severe sleep deprivation. Take a nap before training)")
                break
            else:
                print("Error: Invalid hours entered. Please put a realistic number (0-24).")
                
        except ValueError:
            print("Invalid input! Please enter numbers only (e.g., 7.5).")
            # Loop will automatically continue to ask again
def morning_advice(sleep_time):
    # Ab numeric comparison hoga, string check nahi
    if 7.5 <= sleep_time <= 10.0:
        print("If you are feeling tired, drink water or go for a walk. "
              "If you are feeling fresh, carry on your day as normal.")
        
    elif 6.0 <= sleep_time < 7.5:
        print("If you are feeling tired, take a small 10 to 20 min nap. "
              "If you are feeling fresh, carry on your day as normal.")
        
    elif 3.0 <= sleep_time < 6.0:
        print("If you are feeling tired, take a small 10 to 20 min nap. "
              "If you are feeling fresh, carry on your day as normal.")
        
    else:
        print("Status: Severe sleep deprivation/Invalid range. Rest is top priority!")

# --- Execution ---
user_sleep = morning_check_in()  # Pehle check-in chalega
morning_advice(user_sleep)
      

main()
