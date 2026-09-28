"""
matching_engine.py
Owner: Person C

Responsibility: THE CORE COMPUTATIONAL FEATURE of the project.
Given the pantry and the recipe database, work out which recipes the
user can cook right now, which are "almost there", and which need a
proper shopping trip - then rank them.

This module is fully implemented already since it is the feature we
demo for Milestone 1. Person C should still read through it carefully,
be ready to explain every line in the viva, and can extend it later
(e.g. weighting rare/expensive ingredients differently, considering
quantity and not just presence).

Core idea (set operations):
    match_score = |pantry_ingredients ∩ recipe_ingredients| / |recipe_ingredients|
    missing     = recipe_ingredients - pantry_ingredients
"""


def compute_match(recipe_ingredients, pantry_ingredients):
    """
    Compare one recipe's ingredient set against the pantry.

    Args:
        recipe_ingredients (set[str]): ingredients required by the recipe
        pantry_ingredients (set[str]): ingredients currently in the pantry

    Returns:
        dict with:
            match_score (float): fraction of required ingredients available (0.0 - 1.0)
            have (set[str]): ingredients the user already has
            missing (set[str]): ingredients the user still needs to buy
    """
    if not recipe_ingredients:
        return {"match_score": 0.0, "have": set(), "missing": set()}

    have = recipe_ingredients & pantry_ingredients
    missing = recipe_ingredients - pantry_ingredients
    match_score = len(have) / len(recipe_ingredients)

    return {"match_score": match_score, "have": have, "missing": missing}


def classify(match_score):
    """Bucket a match score into a human-readable readiness label."""
    if match_score == 1.0:
        return "Ready now"
    if match_score >= 0.7:
        return "Almost there"
    return "Needs shopping"


def rank_recipes(recipes, pantry_ingredients, category=None):
    """
    Rank every recipe by how ready the user is to cook it.

    Args:
        recipes (dict): as produced by recipe_database.load_recipes()
        pantry_ingredients (set[str]): as produced by
            pantry_manager.get_ingredient_names()
        category (str, optional): filter to only this meal category
            (e.g. "breakfast", "lunch", "dinner")

    Returns:
        list[dict]: one entry per recipe, sorted best-match first, each with:
            name, category, calories, cook_time, match_score, status, missing
    """
    ranked = []

    for name, info in recipes.items():
        if category and info["category"] != category.lower():
            continue

        result = compute_match(info["ingredients"], pantry_ingredients)
        ranked.append({
            "name": name,
            "category": info["category"],
            "calories": info["calories"],
            "cook_time": info["cook_time"],
            "match_score": result["match_score"],
            "status": classify(result["match_score"]),
            "missing": result["missing"],
        })

    # Sort by: highest match score first, then fewest missing ingredients,
    # then shortest cook time (nice tie-breaker for a hungry student)
    ranked.sort(key=lambda r: (-r["match_score"], len(r["missing"]), r["cook_time"]))
    return ranked


def print_ranked_recipes(ranked, limit=10):
    """Pretty-print the ranked recipe list to the console."""
    print(f"\n{'Recipe':<25}{'Category':<12}{'Match':<10}{'Status':<16}Missing")
    print("-" * 90)
    for r in ranked[:limit]:
        missing_str = ", ".join(sorted(r["missing"])) if r["missing"] else "-"
        print(f"{r['name']:<25}{r['category']:<12}{r['match_score']*100:>5.0f}%    "
              f"{r['status']:<16}{missing_str}")


if __name__ == "__main__":
    # Standalone demo of the core feature using the sample CSVs.
    # This is the Milestone 1 prototype: run `python matching_engine.py`
    from recipe_database import load_recipes
    from pantry_manager import load_pantry, get_ingredient_names

    recipes = load_recipes("recipes.csv")
    pantry = load_pantry("pantry.csv")
    pantry_names = get_ingredient_names(pantry)

    print(f"Pantry has {len(pantry_names)} ingredients: {sorted(pantry_names)}")

    ranked = rank_recipes(recipes, pantry_names)
    print_ranked_recipes(ranked)
