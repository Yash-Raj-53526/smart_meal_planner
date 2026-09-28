"""
recipe_database.py
Owner: Person A

Responsibility: manage the recipe collection - load/save from CSV,
add new recipes, view, edit and delete recipes, with input validation.

Data structure used:
    recipes = {
        "Tomato Pasta": {
            "ingredients": {"pasta", "tomato", "garlic", "olive oil", "basil"},
            "category": "dinner",
            "calories": 450,
            "cook_time": 25,
        },
        ...
    }
"""

import csv
import os


def load_recipes(filepath="recipes.csv"):
    """Read recipes.csv into the recipes dictionary described above.
    Already implemented so the rest of the team can build/test against it.
    """
    recipes = {}
    if not os.path.exists(filepath):
        return recipes

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = row["name"].strip()
                ingredients = {i.strip().lower() for i in row["ingredients"].split(";") if i.strip()}
                recipes[name] = {
                    "ingredients": ingredients,
                    "category": row["category"].strip().lower(),
                    "calories": int(row["calories"]),
                    "cook_time": int(row["cook_time"]),
                }
            except (KeyError, ValueError):
                print(f"  [Warning] Skipped a malformed row in {filepath}: {row}")
                continue
    return recipes


def save_recipes(recipes, filepath="recipes.csv"):
    """Write the recipes dictionary back out to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "ingredients", "category", "calories", "cook_time"])
        for name, info in recipes.items():
            writer.writerow([
                name,
                ";".join(sorted(info["ingredients"])),
                info["category"],
                info["calories"],
                info["cook_time"],
            ])


VALID_CATEGORIES = {"breakfast", "lunch", "dinner"}


def _read_positive_int(prompt):
    """Helper: keep asking until the user gives a valid positive whole number,
    or types 'cancel' to back out. Returns None on cancel."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            return None
        try:
            value = int(raw)
            if value <= 0:
                print("  Please enter a positive whole number.")
                continue
            return value
        except ValueError:
            print("  That's not a valid whole number. Try again (or type 'cancel').")


def _read_category(prompt):
    """Helper: keep asking until the user gives one of breakfast/lunch/dinner."""
    while True:
        raw = input(prompt).strip().lower()
        if raw == "cancel":
            return None
        if raw in VALID_CATEGORIES:
            return raw
        print(f"  Category must be one of {sorted(VALID_CATEGORIES)}. Try again (or type 'cancel').")


def add_recipe(recipes):
    """
    Prompt the user for a new recipe's details, validate everything, and
    add it to the recipes dict. Type 'cancel' at any prompt to back out
    without changing anything.

    Returns:
        the same `recipes` dict, updated in place (also returned for convenience)
    """
    print("\n--- Add a new recipe --- (type 'cancel' at any point to stop)")

    while True:
        name = input("Recipe name: ").strip()
        if name.lower() == "cancel":
            print("Cancelled.")
            return recipes
        if not name:
            print("  Name can't be empty.")
            continue
        if name in recipes:
            print(f"  A recipe called '{name}' already exists. Choose a different name.")
            continue
        break

    while True:
        raw_ingredients = input("Ingredients (comma-separated, e.g. rice, egg, onion): ").strip()
        if raw_ingredients.lower() == "cancel":
            print("Cancelled.")
            return recipes
        ingredients = {i.strip().lower() for i in raw_ingredients.split(",") if i.strip()}
        if not ingredients:
            print("  You must enter at least one ingredient.")
            continue
        break

    category = _read_category("Category (breakfast/lunch/dinner): ")
    if category is None:
        print("Cancelled.")
        return recipes

    calories = _read_positive_int("Calories (positive whole number): ")
    if calories is None:
        print("Cancelled.")
        return recipes

    cook_time = _read_positive_int("Cook time in minutes (positive whole number): ")
    if cook_time is None:
        print("Cancelled.")
        return recipes

    recipes[name] = {
        "ingredients": ingredients,
        "category": category,
        "calories": calories,
        "cook_time": cook_time,
    }
    print(f"  Added '{name}' to the recipe database.")
    return recipes


def view_recipes(recipes, category=None):
    """
    Print all recipes in a readable table. If `category` is given
    (breakfast/lunch/dinner), only recipes in that category are shown.
    """
    if category:
        category = category.strip().lower()
        filtered = {n: r for n, r in recipes.items() if r["category"] == category}
    else:
        filtered = recipes

    if not filtered:
        print("No recipes to show." if not category else f"No recipes found in category '{category}'.")
        return

    print(f"\n{'Recipe':<25}{'Category':<12}{'Calories':<10}{'Time (min)':<12}Ingredients")
    print("-" * 100)
    for name, info in sorted(filtered.items()):
        ingredients_str = ", ".join(sorted(info["ingredients"]))
        print(f"{name:<25}{info['category']:<12}{info['calories']:<10}{info['cook_time']:<12}{ingredients_str}")
    print(f"\n{len(filtered)} recipe(s) shown.")


def edit_recipe(recipes, name):
    """
    Let the user update ingredients/category/calories/cook_time for an
    existing recipe. Pressing Enter on any field keeps its current value.
    Returns True if the recipe was updated, False if it wasn't found or
    the edit was cancelled.
    """
    if name not in recipes:
        print(f"  No recipe called '{name}' found.")
        return False

    current = recipes[name]
    print(f"\n--- Editing '{name}' --- (press Enter to keep current value, or type 'cancel' to stop)")

    raw_ingredients = input(
        f"Ingredients [{', '.join(sorted(current['ingredients']))}]: "
    ).strip()
    if raw_ingredients.lower() == "cancel":
        print("Cancelled.")
        return False
    if raw_ingredients:
        new_ingredients = {i.strip().lower() for i in raw_ingredients.split(",") if i.strip()}
        if new_ingredients:
            current["ingredients"] = new_ingredients

    raw_category = input(f"Category [{current['category']}]: ").strip().lower()
    if raw_category == "cancel":
        print("Cancelled.")
        return False
    if raw_category:
        if raw_category not in VALID_CATEGORIES:
            print(f"  Invalid category, keeping '{current['category']}'.")
        else:
            current["category"] = raw_category

    raw_calories = input(f"Calories [{current['calories']}]: ").strip()
    if raw_calories.lower() == "cancel":
        print("Cancelled.")
        return False
    if raw_calories:
        try:
            value = int(raw_calories)
            if value > 0:
                current["calories"] = value
            else:
                print("  Must be positive, keeping previous value.")
        except ValueError:
            print("  Not a valid number, keeping previous value.")

    raw_cook_time = input(f"Cook time in minutes [{current['cook_time']}]: ").strip()
    if raw_cook_time.lower() == "cancel":
        print("Cancelled.")
        return False
    if raw_cook_time:
        try:
            value = int(raw_cook_time)
            if value > 0:
                current["cook_time"] = value
            else:
                print("  Must be positive, keeping previous value.")
        except ValueError:
            print("  Not a valid number, keeping previous value.")

    print(f"  '{name}' updated.")
    return True


def delete_recipe(recipes, name):
    """
    Remove a recipe by name after confirmation.
    Returns True if deleted, False if the name wasn't found or the
    user backed out of the confirmation.
    """
    if name not in recipes:
        print(f"  No recipe called '{name}' found.")
        return False

    confirm = input(f"Are you sure you want to delete '{name}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return False

    del recipes[name]
    print(f"  '{name}' deleted.")
    return True


def recipe_menu(recipes, filepath="recipes.csv"):
    """
    Standalone submenu for recipe management. Called from main.py's
    'View / manage recipes' option, or can be run directly for testing.
    Saves to `filepath` whenever the list changes.
    """
    while True:
        print("\n--- Recipe Menu ---")
        print("1. View all recipes")
        print("2. View recipes by category")
        print("3. Add a recipe")
        print("4. Edit a recipe")
        print("5. Delete a recipe")
        print("6. Back to main menu")
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            view_recipes(recipes)
        elif choice == "2":
            category = input("Category (breakfast/lunch/dinner): ").strip()
            view_recipes(recipes, category=category)
        elif choice == "3":
            add_recipe(recipes)
            save_recipes(recipes, filepath)
        elif choice == "4":
            name = input("Name of recipe to edit: ").strip()
            if edit_recipe(recipes, name):
                save_recipes(recipes, filepath)
        elif choice == "5":
            name = input("Name of recipe to delete: ").strip()
            if delete_recipe(recipes, name):
                save_recipes(recipes, filepath)
        elif choice == "6":
            break
        else:
            print("Invalid option. Please choose 1-6.")


if __name__ == "__main__":
    # Quick manual test while building/testing this module standalone
    data = load_recipes("recipes.csv")
    print(f"Loaded {len(data)} recipes.")
    recipe_menu(data, "recipes.csv")
