"""
pantry_manager.py
Owner: Person B

Responsibility: manage the user's pantry - load/save from CSV, add,
update quantity, and remove ingredients, with input validation.

Data structure used:
    pantry = {
        "rice": {"quantity": 2.0, "unit": "kg"},
        "onion": {"quantity": 6.0, "unit": "pcs"},
        ...
    }
"""

import csv
import os


def load_pantry(filepath="pantry.csv"):
    """Read pantry.csv into the pantry dictionary described above."""
    pantry = {}
    if not os.path.exists(filepath):
        return pantry

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = row["ingredient"].strip().lower()
                pantry[name] = {
                    "quantity": float(row["quantity"]),
                    "unit": row["unit"].strip(),
                }
            except (KeyError, ValueError):
                print(f"  [Warning] Skipped a malformed row in {filepath}: {row}")
                continue
    return pantry


def save_pantry(pantry, filepath="pantry.csv"):
    """Write the pantry dictionary back out to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ingredient", "quantity", "unit"])
        for name, info in pantry.items():
            writer.writerow([name, info["quantity"], info["unit"]])


def _read_positive_number(prompt):
    """Helper: keep asking until the user gives a valid positive number,
    or types 'cancel' to back out. Returns None on cancel."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            return None
        try:
            value = float(raw)
            if value <= 0:
                print("  Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("  That's not a valid number. Try again (or type 'cancel').")


def _read_non_negative_number(prompt):
    """Like _read_positive_number but allows 0 (e.g. 'used it all up')."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            return None
        try:
            value = float(raw)
            if value < 0:
                print("  Quantity can't be negative.")
                continue
            return value
        except ValueError:
            print("  That's not a valid number. Try again (or type 'cancel').")


def add_ingredient(pantry):
    """
    Prompt the user for an ingredient name, quantity, and unit, validate
    everything, and add it to the pantry. If the ingredient already
    exists with the SAME unit, the new quantity is added to the existing
    amount rather than overwriting it. If it exists with a DIFFERENT
    unit, the user is warned and asked to confirm before overwriting.
    Type 'cancel' at any prompt to back out without changing anything.

    Returns:
        the same `pantry` dict, updated in place (also returned for convenience)
    """
    print("\n--- Add ingredient to pantry --- (type 'cancel' at any point to stop)")

    while True:
        name = input("Ingredient name: ").strip().lower()
        if name == "cancel":
            print("Cancelled.")
            return pantry
        if not name:
            print("  Name can't be empty.")
            continue
        break

    quantity = _read_positive_number("Quantity (positive number): ")
    if quantity is None:
        print("Cancelled.")
        return pantry

    unit = input("Unit (e.g. kg, g, pcs, litre): ").strip()
    if unit.lower() == "cancel":
        print("Cancelled.")
        return pantry
    if not unit:
        print("  Unit can't be empty. Defaulting to 'pcs'.")
        unit = "pcs"

    if name in pantry:
        existing = pantry[name]
        if existing["unit"].lower() == unit.lower():
            existing["quantity"] += quantity
            print(f"  Updated '{name}': now {existing['quantity']} {existing['unit']}.")
        else:
            confirm = input(
                f"  '{name}' already exists as {existing['quantity']} {existing['unit']}. "
                f"Overwrite with {quantity} {unit}? (y/n): "
            ).strip().lower()
            if confirm == "y":
                pantry[name] = {"quantity": quantity, "unit": unit}
                print(f"  '{name}' overwritten: now {quantity} {unit}.")
            else:
                print("Cancelled — pantry left unchanged.")
    else:
        pantry[name] = {"quantity": quantity, "unit": unit}
        print(f"  Added '{name}': {quantity} {unit}.")

    return pantry


def update_quantity(pantry, name):
    """
    Update the quantity of an existing pantry ingredient.
    Validates the ingredient exists and the new quantity is a
    non-negative number (0 is allowed, meaning "used it all up").

    Returns True if updated, False if not found or cancelled.
    """
    name = name.strip().lower()
    if name not in pantry:
        print(f"  No ingredient called '{name}' found in the pantry.")
        return False

    current = pantry[name]
    new_quantity = _read_non_negative_number(
        f"New quantity for '{name}' (currently {current['quantity']} {current['unit']}): "
    )
    if new_quantity is None:
        print("Cancelled.")
        return False

    current["quantity"] = new_quantity
    print(f"  '{name}' updated to {new_quantity} {current['unit']}.")
    return True


def remove_ingredient(pantry, name):
    """
    Remove an ingredient after confirmation.
    Returns True if deleted, False if not found or the user backed out.
    """
    name = name.strip().lower()
    if name not in pantry:
        print(f"  No ingredient called '{name}' found in the pantry.")
        return False

    confirm = input(f"Are you sure you want to remove '{name}' from the pantry? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return False

    del pantry[name]
    print(f"  '{name}' removed from the pantry.")
    return True


def view_pantry(pantry):
    """Print all pantry items in a readable table, sorted alphabetically."""
    if not pantry:
        print("Pantry is empty.")
        return

    print(f"\n{'Ingredient':<20}{'Quantity':<12}Unit")
    print("-" * 45)
    for name in sorted(pantry):
        info = pantry[name]
        print(f"{name:<20}{info['quantity']:<12}{info['unit']}")
    print(f"\n{len(pantry)} ingredient(s) in pantry.")


def get_ingredient_names(pantry):
    """Returns a set of ingredient names only (used by the matching engine)."""
    return set(pantry.keys())


def pantry_menu(pantry, filepath="pantry.csv"):
    """
    Standalone submenu for pantry management. Called from main.py's
    'View / manage pantry' option, or can be run directly for testing.
    Saves to `filepath` whenever the pantry changes.
    """
    while True:
        print("\n--- Pantry Menu ---")
        print("1. View pantry")
        print("2. Add ingredient")
        print("3. Update ingredient quantity")
        print("4. Remove ingredient")
        print("5. Back to main menu")
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            view_pantry(pantry)
        elif choice == "2":
            add_ingredient(pantry)
            save_pantry(pantry, filepath)
        elif choice == "3":
            name = input("Name of ingredient to update: ").strip()
            if update_quantity(pantry, name):
                save_pantry(pantry, filepath)
        elif choice == "4":
            name = input("Name of ingredient to remove: ").strip()
            if remove_ingredient(pantry, name):
                save_pantry(pantry, filepath)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    data = load_pantry("pantry.csv")
    print(f"Loaded {len(data)} pantry items.")
    pantry_menu(data, "pantry.csv")
