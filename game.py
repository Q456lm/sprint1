#!/usr/bin/env python3
# *Used AI to help generate the code for the starting point*
"""
Echo of Terminal 7 — Text adventure.

Setting: Abandoned deep-space research station near a black hole.
Goal: Repair the Slip-Drive and escape; find out why the crew vanished.
"""


# ---------------------------------------------------------------------------
# Game state: tracks progress up to the hub choice
# ---------------------------------------------------------------------------

class State:
    """Holds persistent player progress for intro and power grid puzzle."""

    def __init__(self):
        self.time_units = 100           # Decreases on mistakes; used for tension and override
        self.override_used = False       # Did the player use the door override?


def lose_time(state, amount, message=None):
    """Subtract time units from state (never below 0). Optionally print a reason, then show remaining time."""
    state.time_units = max(0, state.time_units - amount)
    if message:
        print(message)
    print(f"Time units remaining: {state.time_units}\n")


def prompt_choice(choices, prompt_text="Choose"):
    """Print numbered options and loop until the player enters a valid number. Returns 1-based index."""
    print(f"\n{prompt_text}")
    for i, c in enumerate(choices, 1):
        print(f"  {i}. {c}")
    while True:
        try:
            n = int(input(f"Enter number (1-{len(choices)}): ").strip())
            if 1 <= n <= len(choices):
                return n
        except ValueError:
            pass
        print(f"Invalid. Enter 1 to {len(choices)}.")


def prompt_text(prompt_str, default=None):
    """Ask for a line of input. Returns stripped string, or default if empty."""
    s = input(f"{prompt_str} ").strip()
    return s if s else default


# ---------------------------------------------------------------------------
# Scenes: intro, power grid puzzle, central hub (room choice only)
# ---------------------------------------------------------------------------

def intro():
    """Opening: wake in cryo-pod, see hologram message, set the goal."""
    print("\n--- ECHO OF TERMINAL 7 ---\n")
    print("You wake in a flickering cryo-pod. The glass is cracked.")
    print("The air smells of ozone and old recycled oxygen.")
    print("Machinery hums on emergency power.\n")
    print('A holographic interface flickers to life:')
    print('  "REBOOT SUCCESSFUL. MEMORY FILES: CORRUPTED."')
    print('  "CORE TEMPERATURE: DROPPING."')
    print('  "STATION STATUS: CRITICAL. SLIP-DRIVE: OFFLINE."\n')
    print("You have to get out of this room—and find a way off the station.")
    input("\nPress Enter to continue...")


def power_grid_puzzle(state):
    """
    Puzzle 1: Fuse order from the riddle.
    Riddle: sky before sun, grass never touch blood, sun not last.
    Maps to: Blue (sky), Yellow (sun), Green (grass), Red (blood) -> order: blue, yellow, green, red.
    Wrong answers cost time; if time is low, offer a one-time override. Returns True if player escapes.
    """
    print("\n--- THE POWER GRID ---\n")
    print("The door is magnetically sealed. A maintenance panel has four fuses: Red, Blue, Green, Yellow.")
    print('A note on the wall reads: "The sky comes before the sun, but the grass must never')
    print('touch the blood. The sun is not last."\n')
    print("Enter the fuse order (e.g. blue yellow green red).")

    correct_order = ["blue", "yellow", "green", "red"]
    max_attempts = 3

    for attempt in range(max_attempts):
        raw = prompt_text("Order (comma or space separated):").lower().replace(",", " ")
        order = [w.strip() for w in raw.split() if w.strip()]

        if order == correct_order:
            print("\nThe fuses click into place. The door slides open.\n")
            input("Press Enter to continue...")
            return True

        lose_time(state, 15, "Wrong order. Oxygen levels drop. Alarms wail.")
        # Offer override only once, and only when time is already low
        if attempt < max_attempts - 1 and not state.override_used and state.time_units < 50:
            print("You find a manual override panel. Using it costs 10 time units.")
            if prompt_choice(["Use override", "Try again"], "Override?") == 1:
                state.time_units = max(0, state.time_units - 10)
                state.override_used = True
                print("\nOverride accepted. The door opens.\n")
                input("Press Enter to continue...")
                return True

    print("\nThe room runs out of power. You do not make it out.\n")
    return False


def central_hub(state):
    """First major choice: pick one of three wings. Game ends after the choice."""
    print("\n--- CENTRAL HUB ---\n")
    print("Emergency lights cast long shadows. The AI crackles: \"One elevator trip remaining.\"")
    print("Three corridors: 1) Botany Wing (oxygen, biology). 2) Server Room (A.R.I.A., logs). 3) Engineering (radiation, Slip-Drive parts).\n")

    room_names = ["Botany Wing", "Server Room", "Engineering Deck"]
    choice = prompt_choice(room_names, "Which way?")
    chosen = room_names[choice - 1]
    print(f"\nYou head toward the {chosen}.\n")
    print("Thanks for playing Echo of Terminal 7.\n")


def main():
    """Entry point: intro, power grid puzzle, then hub room choice. Game ends after choice."""
    state = State()
    intro()
    if not power_grid_puzzle(state):
        return
    central_hub(state)


if __name__ == "__main__":
    main()
