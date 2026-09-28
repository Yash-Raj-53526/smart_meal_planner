"""
meal_planner.py
Owner: Person D

Responsibility: turn the recipe database + pantry into an actual 7-day
meal plan, avoiding repeats where possible, and build a shopping list
of everything missing for the chosen recipes.

Data structure used:
    meal_plan = [
        {"day": "Monday", "slot": "breakfast", "recipe": "Masala Omelette",
         "status": "Ready now", "missing": set()},
        ...
    ]
"""

import csv
import os

import matching_engine as me

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOTS = ["breakfast", "lunch", "dinner"]


def generate_meal_plan(recipes, pantry_ingredients, days=None, slots=None, avoid_repeat_days=3):
    """
    Build a meal plan covering every day/slot combination.

    For each day and slot, the best-ranked recipe in that slot's category
    (breakfast/lunch/dinner) is chosen, preferring recipes that have NOT
    been used in the last `avoid_repeat_days` days. If every suitable
    recipe has been used too recently, the repeat restriction is relaxed
    for that slot rather than leaving it empty (a sensible fallback for
    a small recipe database). If no recipe exists at all for a category,
    a placeholder entry explains that.

    Args:
        recipes (dict): as produced by recipe_database.load_recipes()
        pantry_ingredients (set[str]): as produced by
            pantry_manager.get_ingredient_names()
        days (list[str]): defaults to DAYS (7 days)
        slots (list[str]): defaults to SLOTS (breakfast/lunch/dinner)
        avoid_repeat_days (int): minimum number of days that must pass
            before a recipe can be scheduled again (e.g. 3 means a recipe
            used on day index N cannot be reused until day index N+3 or later)

    Returns:
        list[dict]: one entry per day/slot combination, in order
    """
    days = days or DAYS
    slots = slots or SLOTS

    # Rank once per category up-front (ranking doesn't change during planning)
    ranked_by_slot = {slot: me.rank_recipes(recipes, pantry_ingredients, category=slot) for slot in slots}

    last_used_day = {}   # recipe_name -> day index it was last scheduled
    meal_plan = []

    for day_index, day in enumerate(days):
        for slot in slots:
            candidates = ranked_by_slot[slot]

            if not candidates:
                meal_plan.append({
                    "day": day, "slot": slot, "recipe": None,
                    "status": "No suitable recipe found", "missing": set(),
                })
                continue

            chosen = None
            for candidate in candidates:
                last_day = last_used_day.get(candidate["name"])
                if last_day is None or (day_index - last_day) >= avoid_repeat_days:
                    chosen = candidate
                    break

            # Fallback: every candidate was used too recently (small recipe
            # database) -> relax the repeat rule rather than skip the slot
            if chosen is None:
                chosen = candidates[0]

            meal_plan.append({
                "day": day, "slot": slot, "recipe": chosen["name"],
                "status": chosen["status"], "missing": set(chosen["missing"]),
            })
            last_used_day[chosen["name"]] = day_index

    return meal_plan


def build_shopping_list(meal_plan):
    """
    Collect every missing ingredient across the whole meal plan.

    Returns:
        list[tuple[str, int]]: (ingredient, how many planned recipes need it),
        sorted by how many recipes need it (most-needed first), then name.
    """
    from collections import Counter

    counts = Counter()
    for entry in meal_plan:
        if entry["recipe"] is None:
            continue
        for ingredient in entry["missing"]:
            counts[ingredient] += 1

    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))


def print_meal_plan(meal_plan, slots=None):
    """Print the week's plan as a readable grid: Day | Breakfast | Lunch | Dinner."""
    slots = slots or SLOTS

    by_day = {}
    for entry in meal_plan:
        by_day.setdefault(entry["day"], {})[entry["slot"]] = entry

    col_width = 24
    header = f"{'Day':<12}" + "".join(f"{slot.capitalize():<{col_width}}" for slot in slots)
    print(f"\n{header}")
    print("-" * len(header))

    for day, slot_entries in by_day.items():
        row = f"{day:<12}"
        for slot in slots:
            entry = slot_entries.get(slot)
            name = entry["recipe"] if entry and entry["recipe"] else "-"
            row += f"{name:<{col_width}}"
        print(row)


def save_meal_plan(meal_plan, filepath="meal_history.csv"):
    """Appends the finalized plan to meal_history.csv so reports.py can
    later analyze 'most cooked recipes' over time. Entries with no
    recipe assigned are skipped."""
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["day", "slot", "recipe"])
        for entry in meal_plan:
            if entry["recipe"] is None:
                continue
            writer.writerow([entry["day"], entry["slot"], entry["recipe"]])


if __name__ == "__main__":
    # Standalone demo/test of this module using the sample CSVs
    import recipe_database as rdb
    import pantry_manager as pm

    recipes = rdb.load_recipes("recipes.csv")
    pantry = pm.load_pantry("pantry.csv")
    pantry_names = pm.get_ingredient_names(pantry)

    plan = generate_meal_plan(recipes, pantry_names)
    print_meal_plan(plan)

    shopping_list = build_shopping_list(plan)
    print("\nShopping list (ingredient, number of planned recipes needing it):")
    for ingredient, count in shopping_list:
        print(f"  {ingredient} (x{count})")
