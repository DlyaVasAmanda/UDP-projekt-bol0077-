
import csv
from itertools import combinations

class FoodItem:
    def __init__(self, name, calories, protein, fat, carbs):
        self.name = name
        self.calories = int(calories)
        self.protein = float(protein)
        self.fat = float(fat)
        self.carbs = float(carbs)

    def __repr__(self):
        return f"{self.name} ({self.calories} kcal)"

class MealPlan:
    def __init__(self, items):
        self.items = items

    def total_calories(self):
        return sum(item.calories for item in self.items)

    def total_macros(self):
        protein = sum(item.protein for item in self.items)
        fat = sum(item.fat for item in self.items)
        carbs = sum(item.carbs for item in self.items)
        return protein, fat, carbs

    def __repr__(self):
        protein, fat, carbs = self.total_macros()
        return (f"Plán jídel: {', '.join(item.name for item in self.items)} |"
                f"Kalorie: {self.total_calories()} kcal | "
                f"Bílkoviny: {protein:.1f} g | Tuky: {fat:.1f} g | Sacharidy: {carbs:.1f} g")

class MealPlanner:
    def __init__(self, csv_file):
        self.food_items = []
        self.load_data(csv_file)

    def load_data(self, csv_file):
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.food_items.append(FoodItem(row['name'], row['calories'], row['protein'], row['fat'], row['carbs']))
        except Exception as e:
            print(f"Chyba při načítání dat: {e}")

    def generate_plan(self, target_calories, max_items=5):
        best_plan = None
        best_diff = float('inf')
        for r in range(2, max_items + 1):
            for combo in combinations(self.food_items, r):
                total = sum(item.calories for item in combo)
                diff = abs(target_calories - total)
                if diff < best_diff:
                    best_diff = diff
                    best_plan = combo
        return MealPlan(best_plan) if best_plan else None

def menu():
    planner = MealPlanner("jidla.csv")
    while True:
        print("[Plánovač jídelníčku]")
        print("1) Zobrazit všechny potraviny")
        print("2) Vygenerovat jídelníček")
        print("0) Konec")
        choice = input("> ").strip()
        if choice == "1":
            for item in planner.food_items:
                print(item)
        elif choice == "2":
            try:
                target = int(input("Zadejte cílový počet kalorií: "))
                plan = planner.generate_plan(target)
                if plan:
                    print("Váš jídelníček:")
                    print(plan)
                else:
                    print("Nepodařilo se sestavit plán.")
            except Exception as e:
                print(f"Chyba: {e}")
        elif choice == "0":
            break
        else:
            print("Neplatná volba.")

if __name__ == "__main__":
    menu()
