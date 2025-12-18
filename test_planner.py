# 3. test_planner.py - тестовый скрипт
"""
TESTY PRO PLÁNOVAČ JÍDELNÍČKU
Autor: Adil
"""

import sys
import os

from planner_jidelnicku_final import *

def test_data_loading():
    """Test načítání dat z CSV."""
    print("🧪 TEST: Načítání dat z CSV")
    foods = load_foods("jidla_cz.csv")
    
    assert len(foods) > 0, "Nenačteny žádné potraviny"
    assert isinstance(foods[0], FoodItem), "Neplatný typ potraviny"
    
    print(f"✅ Načteno {len(foods)} potravin")
    
    # Kontrola konkrétní potraviny
    chicken = next((f for f in foods if "Kuřecí" in f.name), None)
    assert chicken is not None, "Kuřecí prsa nenalezena"
    assert chicken.protein > 50, "Nízký obsah bílkovin v kuřecích prsou"
    
    print("✅ Data jsou validní")
    return True

def test_builder_pattern():
    """Test Builder patternu."""
    print("\n🧪 TEST: Builder pattern")
    
    # Vytvoření builderu
    builder = MealPlanBuilder()
    
    # Vytvoření testovací potraviny
    test_food = FoodItem(
        name="Testovací jídlo",
        calories=100,
        protein=20,
        fat=5,
        carbs=10,
        meal_times={"breakfast", "lunch"}
    )
    
    # Přidání potraviny
    builder.add_breakfast(test_food)
    
    # Sestavení plánu
    plan = builder.build()
    
    assert len(plan.breakfast) == 1, "Nesprávný počet položek v snídani"
    assert plan.breakfast[0].name == "Testovací jídlo", "Špatná potravina"
    
    print("✅ Builder pattern funguje správně")
    return True

def test_filtering():
    """Test funkcionálního filtrování."""
    print("\n🧪 TEST: Funkcionální filtrování")
    
    foods = load_foods("jidla_cz.csv")
    
    # Filtrování potravin pro snídani
    breakfast_foods = filter_items(foods, by_meal_time("breakfast"))
    
    # Kontrola, že všechny jsou vhodné pro snídani
    for food in breakfast_foods:
        assert "breakfast" in food.meal_times, f"{food.name} není vhodná pro snídani"
    
    print(f"✅ Nalezeno {len(breakfast_foods)} potravin pro snídani")
    
    # Filtrování podle tagu
    vegan_foods = filter_items(foods, by_tag("vegan"))
    for food in vegan_foods:
        assert "vegan" in food.tags, f"{food.name} nemá tag vegan"
    
    print(f"✅ Nalezeno {len(vegan_foods)} veganských potravin")
    return True

def test_optimization():
    """Test optimalizačního algoritmu."""
    print("\n🧪 TEST: Knapsack optimalizace")
    
    foods = load_foods("jidla_cz.csv")
    
    # Cíle pro test
    targets = {
        "calories": 2000,
        "protein": 100,
        "fat": 70,
        "carbs": 200
    }
    
    limits = {
        "calories": (1800, 2200)
    }
    
    weights = {
        "protein": 2.0
    }
    
    slot_caps = {
        "breakfast": (1, 2),
        "lunch": (1, 2),
        "dinner": (1, 2),
        "snack": (0, 1)
    }
    
    # Hledání optimálního plánu
    plan = find_optimal_plan(foods, targets, limits, weights, slot_caps)
    
    assert plan is not None, "Optimální plán nebyl nalezen"
    
    totals = plan.totals()
    print(f"✅ Plán vytvořen: {totals['calories']} kcal")
    
    # Kontrola, že plán má všechny sloty
    assert len(plan.breakfast) > 0, "Prázdná snídaně"
    assert len(plan.lunch) > 0, "Prázdný oběd"
    assert len(plan.dinner) > 0, "Prázdná večeře"
    
    print("✅ Optimalizace funguje správně")
    return True

def test_error_handling():
    """Test zpracování chyb."""
    print("\n🧪 TEST: Zpracování chyb")
    
    # Test načítání neexistujícího souboru
    foods = load_foods("neexistujici.csv")
    assert len(foods) == 0, "Mělo vrátit prázdný seznam"
    
    print("✅ Chyby jsou správně zpracovány")
    return True

def test_nutrition_calculation():
    """Test výpočtu nutričních hodnot."""
    print("\n🧪 TEST: Výpočet nutričních hodnot")
    
    # Vytvoření testovacích potravin
    food1 = FoodItem("Jídlo 1", 300, 20, 10, 30)
    food2 = FoodItem("Jídlo 2", 200, 15, 5, 25)
    
    # Vytvoření plánu
    plan = MealPlan(
        breakfast=[food1],
        lunch=[food2],
        dinner=[],
        snacks=[]
    )
    
    totals = plan.totals()
    
    assert totals["calories"] == 500, "Špatný výpočet kalorií"
    assert totals["protein"] == 35, "Špatný výpočet bílkovin"
    assert totals["fat"] == 15, "Špatný výpočet tuků"
    assert totals["carbs"] == 55, "Špatný výpočet sacharidů"
    
    print("✅ Výpočty nutričních hodnot jsou správné")
    return True

def run_all_tests():
    """Spustí všechny testy."""
    print("="*60)
    print("SPOUŠTĚNÍ TESTOVACÍ SUITY")
    print("="*60)
    
    tests = [
        test_data_loading,
        test_builder_pattern,
        test_filtering,
        test_optimization,
        test_error_handling,
        test_nutrition_calculation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} selhal: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("VÝSLEDKY TESTOVÁNÍ:")
    print(f"✅ Úspěšné: {passed}")
    print(f"❌ Selhalo: {failed}")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)