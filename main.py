"""
main.py

Smart Recipe & Meal Planner - Command Line Application
Ties all 5 modules into a single menu:
  1. Recipe Database   (recipe_database.py)  - Person A
  2. Pantry Manager     (pantry_manager.py)   - Person B
  3. Matching Engine    (matching_engine.py)  - Person C  [core computational feature]
  4. Meal Planner       (meal_planner.py)     - Person D
  5. Reports            (reports.py)          - Person E

Run: python main.py
"""

import recipe_database as rdb
import pantry_manager as pm
import matching_engine as me
import meal_planner as mp
import reports as rpt

RECIPES_FILE = "recipes.csv"
PANTRY_FILE = "pantry.csv"
HISTORY_FILE = "meal_history.csv"


def print_menu():
    print("\n" + "=" * 50)
    print(" Smart Recipe & Meal Planner")
    print("=" * 50)
    print("1. View / manage recipes")
    print("2. View / manage pantry")
    print("3. Find recipes I can cook now (match & rank)")
    print("4. Generate weekly meal plan + shopping list")
    print("5. View reports (most cooked, nutrition summary)")
    print("6. Exit")


def handle_matching(recipes, pantry):
    """Core feature: rank every recipe by how ready the user is to cook it."""
    print("\nFilter by category? (breakfast/lunch/dinner or press Enter for all)")
    category = input("> ").strip().lower() or None

    pantry_names = pm.get_ingredient_names(pantry)
    ranked = me.rank_recipes(recipes, pantry_names, category=category)

    if not ranked:
        print("No recipes found for that category.")
        return

    me.print_ranked_recipes(ranked)


def handle_meal_plan(recipes, pantry):
    """Generate a full weekly meal plan, show it, build the shopping list,
    and optionally save it to meal history for the reports module."""
    pantry_names = pm.get_ingredient_names(pantry)

    if not recipes:
        print("No recipes in the database yet. Add some first (option 1).")
        return

    plan = mp.generate_meal_plan(recipes, pantry_names)
    mp.print_meal_plan(plan)

    shopping_list = mp.build_shopping_list(plan)
    if shopping_list:
        print("\nShopping list (ingredient - number of planned recipes needing it):")
        for ingredient, count in shopping_list:
            print(f"  {ingredient} (x{count})")
    else:
        print("\nNo shopping needed - every planned recipe is fully covered by your pantry!")

    save = input("\nSave this plan to meal history for reports? (y/n): ").strip().lower()
    if save == "y":
        mp.save_meal_plan(plan, HISTORY_FILE)
        print("Saved.")


def main():
    recipes = rdb.load_recipes(RECIPES_FILE)
    pantry = pm.load_pantry(PANTRY_FILE)
    print(f"Loaded {len(recipes)} recipes and {len(pantry)} pantry items.")

    while True:
        print_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            rdb.recipe_menu(recipes, RECIPES_FILE)

        elif choice == "2":
            pm.pantry_menu(pantry, PANTRY_FILE)

        elif choice == "3":
            handle_matching(recipes, pantry)

        elif choice == "4":
            handle_meal_plan(recipes, pantry)

        elif choice == "5":
            rpt.reports_menu(recipes, HISTORY_FILE)

        elif choice == "6":
            print("Goodbye! Bon appetit.")
            break

        else:
            print("Invalid option. Please choose 1-6.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n\nGoodbye! Bon appetit.")
