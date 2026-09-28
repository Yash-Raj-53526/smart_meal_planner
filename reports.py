"""
reports.py
Owner: Person E

Responsibility: summarize meal-planning usage over time and produce a
simple visualization. Reads from meal_history.csv (written by
meal_planner.py's save_meal_plan()).

This module also owns the overall main.py menu integration.
"""

import csv
from collections import Counter


def load_meal_history(filepath="meal_history.csv"):
    """Reads meal_history.csv into a list of dicts: [{"day":..., "slot":..., "recipe":...}, ...]"""
    history = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("recipe"):
                    history.append(row)
    except FileNotFoundError:
        pass
    return history


def most_cooked_recipes(history, top_n=5):
    """
    Count how many times each recipe appears in history and return the
    top_n most frequent as a list of (recipe_name, count) tuples,
    highest count first.
    """
    if not history:
        return []
    counts = Counter(entry["recipe"] for entry in history)
    return counts.most_common(top_n)


def category_breakdown(history, recipes_lookup):
    """
    Count how many planned meals fall into each category
    (breakfast/lunch/dinner) by cross-referencing each history entry's
    recipe name against the recipes dict. History entries whose recipe
    no longer exists in the recipe database (e.g. it was later deleted)
    are skipped rather than causing an error.

    Returns:
        dict like {"breakfast": 12, "lunch": 10, "dinner": 14}
    """
    breakdown = Counter()
    for entry in history:
        recipe_info = recipes_lookup.get(entry["recipe"])
        if recipe_info is None:
            continue
        breakdown[recipe_info["category"]] += 1
    return dict(breakdown)


def nutrition_summary(history, recipes_lookup):
    """
    Sum total calories planned, broken down per day, using recipes_lookup
    (from recipe_database.load_recipes()) for each recipe's calorie count.
    Recipes no longer in the database are skipped.

    Returns:
        dict: {
            "total_calories": int,
            "per_day": {day_name: total_calories_that_day, ...},
            "average_per_day": float,
        }
    """
    per_day = Counter()
    for entry in history:
        recipe_info = recipes_lookup.get(entry["recipe"])
        if recipe_info is None:
            continue
        per_day[entry["day"]] += recipe_info["calories"]

    total_calories = sum(per_day.values())
    num_days = len(per_day) if per_day else 0
    average_per_day = (total_calories / num_days) if num_days else 0.0

    return {
        "total_calories": total_calories,
        "per_day": dict(per_day),
        "average_per_day": round(average_per_day, 1),
    }


def plot_most_cooked(history, top_n=5, output_path="reports_chart.png"):
    """
    Draw a simple bar chart of the top_n most-cooked recipes and save it
    to output_path. Returns the output_path on success, or None if there
    is no history to plot (avoids crashing on an empty meal history).
    """
    ranked = most_cooked_recipes(history, top_n)
    if not ranked:
        print("No meal history yet - nothing to chart.")
        return None

    import matplotlib
    matplotlib.use("Agg")  # headless backend: works without a display
    import matplotlib.pyplot as plt

    names = [name for name, _ in ranked]
    counts = [count for _, count in ranked]

    plt.figure(figsize=(7, 4))
    plt.bar(names, counts, color="#4A90D9")
    plt.title("Most Cooked Recipes")
    plt.xlabel("Recipe")
    plt.ylabel("Times planned")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path


def reports_menu(recipes, history_filepath="meal_history.csv"):
    """
    Standalone submenu for reports. Called from main.py's 'View reports'
    option, or can be run directly for testing.
    """
    while True:
        print("\n--- Reports Menu ---")
        print("1. Most cooked recipes")
        print("2. Category breakdown")
        print("3. Nutrition summary")
        print("4. Generate bar chart (saves as reports_chart.png)")
        print("5. Back to main menu")
        choice = input("Choose an option (1-5): ").strip()

        history = load_meal_history(history_filepath)

        if choice == "1":
            ranked = most_cooked_recipes(history)
            if not ranked:
                print("No meal history yet. Generate a meal plan first (option 4 on the main menu).")
            else:
                print("\nMost cooked recipes:")
                for name, count in ranked:
                    print(f"  {name}: {count} time(s)")

        elif choice == "2":
            breakdown = category_breakdown(history, recipes)
            if not breakdown:
                print("No meal history yet.")
            else:
                print("\nCategory breakdown:")
                for category, count in breakdown.items():
                    print(f"  {category}: {count} meal(s)")

        elif choice == "3":
            summary = nutrition_summary(history, recipes)
            if summary["total_calories"] == 0:
                print("No meal history yet.")
            else:
                print(f"\nTotal calories planned: {summary['total_calories']}")
                print(f"Average calories per day: {summary['average_per_day']}")
                print("Per-day breakdown:")
                for day, cals in summary["per_day"].items():
                    print(f"  {day}: {cals} kcal")

        elif choice == "4":
            path = plot_most_cooked(history)
            if path:
                print(f"Chart saved to '{path}'. Open it to view.")

        elif choice == "5":
            break
        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    import recipe_database as rdb

    recipes = rdb.load_recipes("recipes.csv")
    history = load_meal_history("meal_history.csv")
    print(f"Loaded {len(history)} meal history entries.")
    reports_menu(recipes, "meal_history.csv")
