# 1. planner_jidelnicku_final.py - основной файл
# -*- coding: utf-8 -*-
"""
PLÁNOVAČ JÍDELNÍČKU - SEMINÁRNÍ PRÁCE
Autor: Adil


Popis: Aplikace pro optimalizaci denního jídelníčku podle nutričních cílů
       s využitím algoritmu podobného problému batohu (knapsack-like).
       
Architektura:
- OOP: FoodItem, MealPlan, MealPlanBuilder
- Návrhový vzor: Builder pro postupnou konstrukci jídelníčku
- Algoritmus: Knapsack-like optimalizace
- FP: Funkcionální filtrování potravin
- Datové zdroje: CSV soubory
"""

import csv
from dataclasses import dataclass, field
from typing import List, Callable, Iterable, Dict, Optional, Tuple, Set
from collections import defaultdict

# ---------- DATA CLASSES ----------
@dataclass(frozen=True, eq=True)
class FoodItem:
    """Třída reprezentující potravinu s nutričními hodnotami."""
    name: str
    calories: int
    protein: float
    fat: float
    carbs: float
    meal_times: Set[str] = field(default_factory=lambda: {"breakfast", "lunch", "dinner", "snack"})
    tags: Set[str] = field(default_factory=set)

    def __repr__(self) -> str:
        return f"{self.name} ({self.calories} kcal)"

    def get_nutrient_value(self, nutrient: str) -> float:
        """Vrátí hodnotu živiny podle názvu (kalorie, protein, tuky, sacharidy)."""
        nutrient_map = {
            "calories": self.calories,
            "protein": self.protein,
            "fat": self.fat,
            "carbs": self.carbs
        }
        return nutrient_map.get(nutrient, 0.0)

# ---------- MEAL PLAN ----------
@dataclass
class MealPlan:
    """Třída reprezentující celodenní jídelníček."""
    breakfast: List[FoodItem]
    lunch: List[FoodItem]
    dinner: List[FoodItem]
    snacks: List[FoodItem]

    def all_items(self) -> List[FoodItem]:
        """Vrátí všechny potraviny v jídelníčku."""
        return self.breakfast + self.lunch + self.dinner + self.snacks

    def totals(self) -> Dict[str, float]:
        """Vypočítá celkové nutriční hodnoty jídelníčku."""
        items = self.all_items()
        return {
            "calories": sum(i.calories for i in items),
            "protein": sum(i.protein for i in items),
            "fat": sum(i.fat for i in items),
            "carbs": sum(i.carbs for i in items),
        }

    def __repr__(self) -> str:
        """Textová reprezentace jídelníčku."""
        t = self.totals()
        def names(xs): return ", ".join(i.name for i in xs) if xs else "—"
        return (
            "="*50 + "\n" +
            "OPTIMÁLNÍ JÍDELNÍČEK\n" +
            "="*50 + "\n" +
            f"• SNÍDANĚ:  {names(self.breakfast)}\n" +
            f"• OBĚD:     {names(self.lunch)}\n" +
            f"• VEČEŘE:   {names(self.dinner)}\n" +
            f"• SVAČINY:  {names(self.snacks)}\n" +
            "="*50 + "\n" +
            "CELKOVÉ HODNOTY:\n" +
            f"• Kalorie:     {t['calories']:>6} kcal\n" +
            f"• Bílkoviny:   {t['protein']:>6.1f} g\n" +
            f"• Tuky:        {t['fat']:>6.1f} g\n" +
            f"• Sacharidy:   {t['carbs']:>6.1f} g\n" +
            "="*50
        )

# ---------- BUILDER PATTERN ----------
class MealPlanBuilder:
    """
    Builder pro konstrukci jídelníčku.
    Návrhový vzor Builder umožňuje postupně přidávat potraviny
    s validací na konci procesu.
    """
    
    def __init__(self):
        self._breakfast: List[FoodItem] = []
        self._lunch: List[FoodItem] = []
        self._dinner: List[FoodItem] = []
        self._snacks: List[FoodItem] = []
        
        # Výchozí limity pro sloty (min, max)
        self._slot_caps = {
            "breakfast": (1, 2),
            "lunch": (1, 3),
            "dinner": (1, 3),
            "snack": (0, 2),
        }

    def set_slot_limits(self, slot: str, min_items: int, max_items: int):
        """Nastaví minimální a maximální počet položek pro slot."""
        self._slot_caps[slot] = (min_items, max_items)
        return self

    def add_to_slot(self, slot: str, item: FoodItem):
        """Přidá potravinu do daného slotu s validací."""
        # Validace: potravina musí být vhodná pro daný čas jídla
        if slot not in item.meal_times:
            raise ValueError(f"Potravina '{item.name}' není vhodná pro {slot}")
        
        # Přidání do správného slotu
        if slot == "breakfast":
            self._breakfast.append(item)
        elif slot == "lunch":
            self._lunch.append(item)
        elif slot == "dinner":
            self._dinner.append(item)
        elif slot == "snack":
            self._snacks.append(item)
            
        return self

    def add_breakfast(self, item: FoodItem):
        """Přidá potravinu k snídani."""
        return self.add_to_slot("breakfast", item)

    def add_lunch(self, item: FoodItem):
        """Přidá potravinu k obědu."""
        return self.add_to_slot("lunch", item)

    def add_dinner(self, item: FoodItem):
        """Přidá potravinu k večeři."""
        return self.add_to_slot("dinner", item)

    def add_snack(self, item: FoodItem):
        """Přidá potravinu jako svačinu."""
        return self.add_to_slot("snack", item)

    def build(self, 
              targets: Dict[str, Optional[float]] = None,
              limits: Dict[str, Tuple[Optional[float], Optional[float]]] = None) -> MealPlan:
        """
        Vytvoří a validuje finální jídelníček.
        
        Args:
            targets: Cílové nutriční hodnoty
            limits: Minimální/maximální limity
            
        Returns:
            MealPlan: Validovaný jídelníček
            
        Raises:
            ValueError: Pokud jídelníček nesplňuje omezení
        """
        try:
            # Validace počtu položek ve slotech
            for slot, (min_cap, max_cap) in self._slot_caps.items():
                items = self._get_slot_items(slot)
                if len(items) < min_cap:
                    raise ValueError(f"Slot '{slot}': příliš málo položek ({len(items)} < {min_cap})")
                if len(items) > max_cap:
                    raise ValueError(f"Slot '{slot}': příliš mnoho položek ({len(items)} > {max_cap})")
            
            # Vytvoření jídelníčku
            plan = MealPlan(
                breakfast=list(self._breakfast),
                lunch=list(self._lunch),
                dinner=list(self._dinner),
                snacks=list(self._snacks)
            )
            
            # Validace proti cílům a limitům
            if targets or limits:
                totals = plan.totals()
                
                # Validace limitů
                if limits:
                    for metric, (min_val, max_val) in limits.items():
                        val = totals.get(metric, 0.0)
                        if min_val is not None and val < min_val:
                            raise ValueError(f"{metric}: {val} < minimální hodnota {min_val}")
                        if max_val is not None and val > max_val:
                            raise ValueError(f"{metric}: {val} > maximální hodnota {max_val}")
            
            return plan
            
        except Exception as e:
            raise ValueError(f"Chyba při vytváření jídelníčku: {e}")

    def _get_slot_items(self, slot: str) -> List[FoodItem]:
        """Pomocná metoda pro získání položek ze slotu."""
        if slot == "breakfast":
            return self._breakfast
        elif slot == "lunch":
            return self._lunch
        elif slot == "dinner":
            return self._dinner
        elif slot == "snack":
            return self._snacks
        return []

# ---------- FUNCTIONAL PROGRAMMING FILTERS ----------
Predicate = Callable[[FoodItem], bool]

def filter_items(items: Iterable[FoodItem], *predicates: Predicate) -> List[FoodItem]:
    """
    Funkcionální filtrování potravin pomocí predikátů.
    Vrací seznam potravin splňující všechny predikáty.
    """
    def ok(item: FoodItem) -> bool:
        return all(predicate(item) for predicate in predicates)
    return list(filter(ok, items))

def compose_predicates(*predicates: Predicate) -> Predicate:
    """Vytvoří nový predikát jako kompozici zadaných predikátů."""
    def composed(item: FoodItem) -> bool:
        return all(predicate(item) for predicate in predicates)
    return composed

# Základní predikáty
def by_meal_time(meal_time: str) -> Predicate:
    """Vrací predikát pro filtrování podle času jídla."""
    return lambda item: meal_time in item.meal_times

def by_tag(tag: str) -> Predicate:
    """Vrací predikát pro filtrování podle tagu."""
    return lambda item: tag in item.tags

def not_tag(tag: str) -> Predicate:
    """Vrací predikát pro vyloučení podle tagu."""
    return lambda item: tag not in item.tags

def max_nutrient(nutrient: str, value: float) -> Predicate:
    """Vrací predikát pro maximální hodnotu živiny."""
    return lambda item: item.get_nutrient_value(nutrient) <= value

def min_nutrient(nutrient: str, value: float) -> Predicate:
    """Vrací predikát pro minimální hodnotu živiny."""
    return lambda item: item.get_nutrient_value(nutrient) >= value

# ---------- DATA LOADING ----------
def load_foods(csv_file: str) -> List[FoodItem]:
    """
    Načte potraviny z CSV souboru.
    
    Args:
        csv_file: Cesta k CSV souboru
        
    Returns:
        List[FoodItem]: Seznam potravin
        
    Raises:
        FileNotFoundError: Pokud soubor neexistuje
        ValueError: Pokud data nejsou validní
    """
    foods: List[FoodItem] = []
    
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Validace povinných polí
                    required_fields = ['name', 'calories', 'protein', 'fat', 'carbs']
                    for field in required_fields:
                        if field not in row:
                            raise ValueError(f"Chybí pole '{field}' v řádku {row_num}")
                    
                    # Parsování hodnot
                    name = row['name'].strip()
                    calories = int(float(row['calories']))
                    protein = float(row['protein'])
                    fat = float(row['fat'])
                    carbs = float(row['carbs'])
                    
                    # Parsování meal_times
                    meal_times = {"breakfast", "lunch", "dinner", "snack"}
                    if 'meal_times' in row and row['meal_times'].strip():
                        meal_times = set(part.strip() for part in row['meal_times'].split('|'))
                    
                    # Parsování tags
                    tags = set()
                    if 'tags' in row and row['tags'].strip():
                        tags = set(part.strip() for part in row['tags'].split('|'))
                    
                    # Vytvoření FoodItem
                    food = FoodItem(name, calories, protein, fat, carbs, meal_times, tags)
                    foods.append(food)
                    
                except (ValueError, KeyError) as e:
                    print(f"Varování: Řádek {row_num} přeskočen - {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Chyba: Soubor '{csv_file}' nebyl nalezen.")
        return []
    except Exception as e:
        print(f"Chyba při čtení CSV: {e}")
        return []
    
    print(f"✅ Načteno {len(foods)} potravin z '{csv_file}'")
    return foods

# ---------- KNAPSACK ALGORITHM ----------
class MealOptimizer:
    """
    Třída pro optimalizaci výběru potravin pomocí knapsack-like algoritmu.
    Algoritmus se snaží maximalizovat splnění nutričních cílů při dodržení omezení.
    """
    
    @staticmethod
    def knapsack_optimize(
        foods: List[FoodItem],
        targets: Dict[str, float],
        limits: Dict[str, Tuple[Optional[float], Optional[float]]],
        weights: Dict[str, float],
        max_items: int = 10
    ) -> List[FoodItem]:
        """
        Knapsack-like algoritmus pro výběr potravin.
        
        Algoritmus:
        1. Pro každou potravinu vypočítá skóre (jak přispívá k cílům)
        2. Seřadí potraviny podle skóre (sestupně)
        3. Vybere potraviny dokud nejsou překročeny limity
        
        Args:
            foods: Seznam dostupných potravin
            targets: Cílové nutriční hodnoty
            limits: Omezení (min, max)
            weights: Váhy důležitosti živin
            max_items: Maximální počet vybraných potravin
            
        Returns:
            List[FoodItem]: Optimalizovaný výběr potravin
        """
        if not targets or not foods:
            return []
        
        nutrients = ["calories", "protein", "fat", "carbs"]
        
        # Výpočet skóre pro každou potravinu
        item_scores = []
        for food in foods:
            score = 0.0
            
            for nutrient in nutrients:
                if nutrient in targets and targets[nutrient] > 0:
                    nutrient_val = food.get_nutrient_value(nutrient)
                    target_val = targets[nutrient]
                    weight = weights.get(nutrient, 1.0)
                    
                    # Skóre = jak blízko jsme cíli (1 = perfektní, 0 = daleko)
                    ratio = nutrient_val / max(target_val, 1)
                    
                    if ratio > 1.5:  # Příliš vysoká hodnota
                        contribution = -weight * (ratio - 1)
                    else:
                        # Penalizace odchylky od cíle
                        contribution = weight * (1 - abs(1 - ratio))
                    
                    score += contribution
            
            # Normalizace skóre
            score = score / len(nutrients)
            item_scores.append((score, food))
        
        # Seřazení podle skóre (nejlepší první)
        item_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Výběr potravin s kontrolou limitů
        selected = []
        current_totals = {nutrient: 0.0 for nutrient in nutrients}
        
        for score, food in item_scores:
            if len(selected) >= max_items:
                break
            
            # Simulace přidání potraviny
            temp_totals = current_totals.copy()
            for nutrient in nutrients:
                temp_totals[nutrient] += food.get_nutrient_value(nutrient)
            
            # Kontrola limitů
            within_limits = True
            for nutrient, (min_val, max_val) in limits.items():
                val = temp_totals[nutrient]
                if min_val is not None and val < min_val:
                    continue  # Můžeme přidat, jsme pod minimem
                if max_val is not None and val > max_val:
                    within_limits = False
                    break
            
            if within_limits:
                selected.append(food)
                current_totals = temp_totals
        
        return selected
    
    @staticmethod
    def distribute_to_slots(
        foods: List[FoodItem],
        slot_caps: Dict[str, Tuple[int, int]]
    ) -> Dict[str, List[FoodItem]]:
        """
        Rozdělí potraviny do časových slotů podle jejich vhodnosti.
        Respektuje kulturní zvyklosti (např. maso není na snídani).
        
        Args:
            foods: Seznam potravin k rozdělení
            slot_caps: Kapacity slotů (min, max)
            
        Returns:
            Dict[str, List[FoodItem]]: Rozdělení potravin podle slotů
        """
        distribution = {slot: [] for slot in slot_caps.keys()}
        
        for food in foods:
            assigned = False
            
            # 1. Pokus o přiřazení podle přirozených časů jídla
            for slot in ["breakfast", "lunch", "dinner", "snack"]:
                if slot in food.meal_times:
                    current_count = len(distribution[slot])
                    max_count = slot_caps[slot][1]
                    
                    # Kulturní pravidla
                    if slot == "breakfast" and "meat" in food.tags:
                        continue  # Maso obvykle ne na snídani
                    
                    if current_count < max_count:
                        distribution[slot].append(food)
                        assigned = True
                        break
            
            # 2. Pokud nebylo přiřazeno, přiřaď kamkoliv s volnou kapacitou
            if not assigned:
                for slot in ["breakfast", "lunch", "dinner", "snack"]:
                    current_count = len(distribution[slot])
                    max_count = slot_caps[slot][1]
                    if current_count < max_count:
                        distribution[slot].append(food)
                        break
        
        return distribution

# ---------- MAIN OPTIMIZATION FUNCTION ----------
def find_optimal_plan(
    foods: List[FoodItem],
    targets: Dict[str, Optional[float]],
    limits: Dict[str, Tuple[Optional[float], Optional[float]]],
    weights: Dict[str, float],
    slot_caps: Dict[str, Tuple[int, int]]
) -> Optional[MealPlan]:
    """
    Hlavní funkce pro nalezení optimálního jídelníčku.
    
    Postup:
    1. Filtrace potravin podle slotů
    2. Optimalizace pro každý slot zvlášť
    3. Rozdělení výsledků do slotů
    4. Sestavení jídelníčku pomocí Builder patternu
    
    Args:
        foods: Všechny dostupné potraviny
        targets: Cílové nutriční hodnoty
        limits: Omezení
        weights: Váhy důležitosti
        slot_caps: Kapacity slotů
        
    Returns:
        MealPlan: Optimální jídelníček nebo None
    """
    try:
        # Filtrace potravin podle slotů
        slot_foods = {}
        for slot in slot_caps.keys():
            slot_foods[slot] = filter_items(foods, by_meal_time(slot))
        
        # Cíle pro celý den
        daily_targets = {k: v for k, v in targets.items() if v is not None}
        
        all_selected = []
        
        if daily_targets:
            # Optimalizace pro každý slot zvlášť
            slot_distribution = {
                "breakfast": 0.25,  # 25% denního cíle
                "lunch": 0.35,      # 35% denního cíle
                "dinner": 0.30,     # 30% denního cíle
                "snack": 0.10       # 10% denního cíle
            }
            
            for slot, percentage in slot_distribution.items():
                slot_items = slot_foods[slot]
                if not slot_items:
                    continue
                
                # Cíle pro tento slot
                slot_targets = {}
                for nutrient, target in daily_targets.items():
                    slot_targets[nutrient] = target * percentage
                
                # Optimalizace pro slot
                selected = MealOptimizer.knapsack_optimize(
                    slot_items,
                    slot_targets,
                    limits,
                    weights,
                    max_items=slot_caps[slot][1]
                )
                
                all_selected.extend(selected[:slot_caps[slot][1]])
        else:
            # Bez cílů - jednoduché přiřazení
            for slot in ["breakfast", "lunch", "dinner", "snack"]:
                slot_items = slot_foods[slot]
                if slot_items:
                    all_selected.extend(slot_items[:slot_caps[slot][1]])
        
        # Rozdělení do slotů
        distribution = MealOptimizer.distribute_to_slots(all_selected, slot_caps)
        
        # Sestavení jídelníčku pomocí Builder patternu
        builder = MealPlanBuilder()
        
        # Nastavení limitů slotů
        for slot, (min_cap, max_cap) in slot_caps.items():
            builder.set_slot_limits(slot, min_cap, max_cap)
        
        # Přidání potravin
        for food in distribution.get("breakfast", []):
            builder.add_breakfast(food)
        for food in distribution.get("lunch", []):
            builder.add_lunch(food)
        for food in distribution.get("dinner", []):
            builder.add_dinner(food)
        for food in distribution.get("snack", []):
            builder.add_snack(food)
        
        return builder.build(targets=targets, limits=limits)
        
    except Exception as e:
        print(f"❌ Chyba při hledání optimálního plánu: {e}")
        return None

# ---------- USER INTERFACE ----------
def interactive_menu():
    """Interaktivní uživatelské rozhraní."""
    print("\n" + "="*60)
    print("PLÁNOVAČ JÍDELNÍČKU - INTERAKTIVNÍ REŽIM")
    print("="*60)
    
    # Načtení dat
    try:
        foods = load_foods("jidla_cz.csv")
        if not foods:
            print("❌ Nelze pokračovat bez dat o potravinách.")
            return
    except Exception as e:
        print(f"❌ Chyba při načítání dat: {e}")
        return
    
    # Nastavení cílů
    print("\n📊 NASTAVENÍ NUTRIČNÍCH CÍLŮ")
    print("   (zadejte hodnotu nebo Enter pro přeskočení)")
    
    targets = {}
    weights = {}
    
    nutrients = [
        ("kalorie", "calories", "kcal"),
        ("bílkoviny", "protein", "g"),
        ("tuky", "fat", "g"),
        ("sacharidy", "carbs", "g")
    ]
    
    for cz_name, eng_name, unit in nutrients:
        try:
            value = input(f"\n  {cz_name.capitalize()} ({unit}): ").strip()
            if value:
                targets[eng_name] = float(value)
                
                # Nastavení váhy
                weight = input(f"  ➤ Váha důležitosti pro {cz_name} (1.0 = standard): ").strip()
                weights[eng_name] = float(weight) if weight else 1.0
            else:
                targets[eng_name] = None
        except ValueError:
            print(f"  ⚠️ Neplatná hodnota, přeskočeno")
            targets[eng_name] = None
    
    # Nastavení limitů
    print("\n⚖️ NASTAVENÍ LIMITŮ")
    print("   (formát: min,max nebo jen ,max nebo min,)")
    
    limits = {}
    for cz_name, eng_name, unit in nutrients:
        limit_input = input(f"\n  {cz_name.capitalize()} (např. '50,100' nebo ',80'): ").strip()
        if limit_input:
            parts = limit_input.split(',')
            if len(parts) == 2:
                min_val = float(parts[0].strip()) if parts[0].strip() else None
                max_val = float(parts[1].strip()) if parts[1].strip() else None
                limits[eng_name] = (min_val, max_val)
    
    # Výchozí limity kalorií
    if "calories" not in limits and "calories" in targets and targets["calories"]:
        cal = targets["calories"]
        limits["calories"] = (cal * 0.9, cal * 1.1)
    
    # Nastavení slotů
    print("\n🍽️ NASTAVENÍ JÍDEL")
    
    slot_caps = {}
    slots = [
        ("snídaně", "breakfast", 1, 2),
        ("oběd", "lunch", 1, 3),
        ("večeře", "dinner", 1, 3),
        ("svačiny", "snack", 0, 2)
    ]
    
    for cz_name, eng_name, default_min, default_max in slots:
        cap_input = input(f"\n  {cz_name.capitalize()} (min,max, default {default_min},{default_max}): ").strip()
        if cap_input and ',' in cap_input:
            parts = cap_input.split(',')
            min_cap = int(parts[0].strip()) if parts[0].strip() else default_min
            max_cap = int(parts[1].strip()) if parts[1].strip() else default_max
        else:
            min_cap, max_cap = default_min, default_max
        slot_caps[eng_name] = (min_cap, max_cap)
    
    # Optimalizace
    print("\n" + "="*60)
    print("🔍 HLEDÁM OPTIMÁLNÍ JÍDELNÍČEK...")
    print("="*60)
    
    plan = find_optimal_plan(foods, targets, limits, weights, slot_caps)
    
    if plan:
        print(plan)
        
        # Porovnání s cíli
        if any(v is not None for v in targets.values()):
            print("\n📈 POROVNÁNÍ S CÍLI:")
            print("-"*30)
            totals = plan.totals()
            
            for nutrient, target in targets.items():
                if target is not None:
                    actual = totals.get(nutrient, 0)
                    diff = actual - target
                    diff_pct = (diff / target * 100) if target > 0 else 0
                    
                    status = "✅" if abs(diff_pct) < 10 else "⚠️" if abs(diff_pct) < 20 else "❌"
                    print(f"{status} {nutrient}: {actual:.1f} vs {target:.1f} ({diff_pct:+.1f}%)")
    else:
        print("❌ Nepodařilo se sestavit vhodný jídelníček.")
        print("\n💡 Tipy:")
        print("  • Zkuste uvolnit limity")
        print("  • Zvyšte počet potravin v CSV")
        print("  • Upravte cílové hodnoty")

def demo_mode():
    """Demonstrační režim s přednastavenými hodnotami."""
    print("\n" + "="*60)
    print("PLÁNOVAČ JÍDELNÍČKU - DEMO REŽIM")
    print("="*60)
    
    # Načtení dat
    foods = load_foods("jidla_cz.csv")
    if not foods:
        print("❌ Nelze spustit demo bez dat.")
        return
    
    print("\n📋 DEMO SCÉNÁŘ: VYSOKOPROTEINOVÁ DIETA")
    print("   (pro sportovce a aktivní jedince)")
    
    # Přednastavené hodnoty
    targets = {
        "calories": 2500,
        "protein": 150,  # Vysoký obsah bílkovin
        "fat": 80,
        "carbs": 200
    }
    
    weights = {
        "calories": 1.0,
        "protein": 2.5,  # Vysoká důležitost bílkovin
        "fat": 1.0,
        "carbs": 1.0
    }
    
    limits = {
        "calories": (2300, 2700),
        "fat": (None, 90),
        "carbs": (180, 220)
    }
    
    slot_caps = {
        "breakfast": (1, 2),
        "lunch": (1, 3),
        "dinner": (1, 3),
        "snack": (1, 2)
    }
    
    print(f"\n🎯 CÍLE:")
    for k, v in targets.items():
        print(f"  • {k}: {v}")
    
    print(f"\n⚖️ VÁHY:")
    for k, v in weights.items():
        print(f"  • {k}: {v}")
    
    print("\n" + "="*60)
    print("🔍 OPTIMALIZUJI...")
    print("="*60)
    
    plan = find_optimal_plan(foods, targets, limits, weights, slot_caps)
    
    if plan:
        print(plan)
        
        # Analýza bílkovin
        totals = plan.totals()
        protein_ratio = totals["protein"] / targets["protein"] * 100
        print(f"\n📊 ANALÝZA BÍLKOVIN:")
        print(f"   Cíl: {targets['protein']} g")
        print(f"   Skutečnost: {totals['protein']:.1f} g")
        print(f"   Splnění: {protein_ratio:.1f}%")
    else:
        print("❌ Demo selhalo. Zkontrolujte data v CSV.")

def run_tests():
    """Spustí testovací scénáře."""
    print("\n" + "="*60)
    print("🧪 TESTY FUNKCIONALITY")
    print("="*60)
    
    foods = load_foods("jidla_cz.csv")
    if not foods:
        print("❌ Testy nelze spustit bez dat.")
        return
    
    # Test 1: Filtrování
    print("\n1. TEST FILTROVÁNÍ:")
    breakfast_foods = filter_items(foods, by_meal_time("breakfast"))
    print(f"   Potraviny pro snídani: {len(breakfast_foods)}")
    
    # Test 2: Builder
    print("\n2. TEST BUILDER PATTERN:")
    try:
        builder = MealPlanBuilder()
        if foods:
            builder.add_breakfast(foods[0])
            plan = builder.build()
            print(f"   Builder vytvořen: {len(plan.breakfast)} položka")
    except Exception as e:
        print(f"   Chyba: {e}")
    
    # Test 3: Načtení dat
    print("\n3. TEST NAČTENÍ DAT:")
    print(f"   Celkem potravin: {len(foods)}")
    print(f"   Ukázka: {foods[0].name if foods else 'žádná'}")
    
    print("\n✅ Základní testy dokončeny")

# ---------- MAIN ----------
def main():
    """Hlavní funkce programu."""
    print("\n" + "="*60)
    print("🥗 PLÁNOVAČ JÍDELNÍČKU v1.0")
    print("="*60)
    print("   Optimalizace výživy pomocí algoritmů")
    print("   © 2023 Seminární práce")
    print("="*60)
    
    while True:
        print("\n📋 HLAVNÍ MENU:")
        print("   1. Interaktivní plánování")
        print("   2. Demo režim (vysokoproteinová dieta)")
        print("   3. Spustit testy")
        print("   4. O programu")
        print("   5. Konec")
        
        try:
            choice = input("\n   Vaše volba (1-5): ").strip()
            
            if choice == "1":
                interactive_menu()
            elif choice == "2":
                demo_mode()
            elif choice == "3":
                run_tests()
            elif choice == "4":
                print("\n📘 O PROGRAMU:")
                print("   Plánovač jídelníčku - Seminární práce")
                print("   Autor: Student")
                print("   Třída: IT/Programování")
                print("   Funkce:")
                print("   • OOP s třídami FoodItem, MealPlan")
                print("   • Návrhový vzor Builder")
                print("   • Knapsack-like optimalizační algoritmus")
                print("   • Funkcionální programování pro filtrování")
                print("   • Načítání dat z CSV")
            elif choice == "5":
                print("\n👋 Ukončuji program. Na shledanou!")
                break
            else:
                print("⚠️ Neplatná volba, zkuste znovu.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Program přerušen uživatelem.")
            break
        except Exception as e:
            print(f"\n❌ Neočekávaná chyba: {e}")

if __name__ == "__main__":
    main()