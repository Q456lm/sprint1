## Echo of Terminal 7

### Team Members
- Nayan Patel — Developer  
- Khani Lyan — Developer 
- Gauhar Veeravalli — Developer 
- Quint Bunting — Developer 

### Game Overview
Echo of Terminal 7 is a top‑down sci‑fi puzzle adventure built with Pygame.  
You control a stranded scientist exploring a dying research station, moving between rooms in a central hub and solving environmental puzzles to restore power, uncover “The Herd” experiment, and stabilize the Slip‑Drive.  
The game focuses on light exploration, simple movement, and room‑based mini‑games rather than combat.

### Game Type
Top‑Down Puzzle Adventure (Pygame)

### Core Mechanics
- **Room exploration** — Move a scientist around a 2D hub and enter themed rooms (Botany, Server Room, Engineering) via doors.
- **Environmental interaction** — Stand near doors or consoles and press `E` to trigger puzzles or change rooms.
- **Mini‑game puzzles** — Each room presents a focused puzzle:
  - **Power Grid**: click fuses in the right color order.
  - **Server Room**: decrypt a Caesar‑cipher log by typing the correct phrase.
  - **Botany**: choose which specimen tank is “The Herd”.
  - **Engineering**: toggle couplers into a stable Up/Down pattern.

### How to Run
Steps

- Clone or download this repository to your computer.

- Open a terminal or command prompt.

- Navigate to the folder containing the project files (the folder with game.py).

- Be sure to have Python Installed, visit prerequisites for Python version. 

- You must have pygame installed .
- Install Pygame (once):

```bash
 python -m pip install pygame-ce
```

- Run the game by typing: python game.py
(On macOS/Linux, use: python3 game.py)
- A window titled “Echo of Terminal 7 — Pygame Prototype” should open.
#### Prerequisites
- Python 3.8+  
- `pygame` 2.x  


### Example Play Session

```bash
$ python game.py
```

A window opens titled **“Echo of Terminal 7 — Pygame Prototype”**.  
You see the **Central Hub** with three labeled doors and a power console.

- You move using **WASD / Arrow keys** toward the **Power Grid** console.  
- You press **E** to interact and enter the **Power Grid Puzzle** screen.  
- You click the fuses in the order **Blue → Yellow → Green → Red** to restore power.  
- You press **ESC** to return to the hub, then walk to the **Server** door and press **E** to attempt the cipher puzzle.

### Win & Lose Conditions

> Note: The current prototype focuses on movement and room puzzles more than a final “you win” cutscene.

#### Win
- Conceptually, the player “wins” when:
  - **Power is restored** via the Power Grid puzzle.  
  - **The Herd secret is understood** via the Server/Botany puzzles.  
  - **The Slip‑Drive couplers are stabilized** in Engineering.  
- These states are tracked in `GameState` (e.g. `power_restored`, `herd_secret_known`, `slip_repaired`) and can be extended into a final escape sequence.

#### Lose
- There is **no hard fail state** yet (no health system or game‑over screen).  
- The player can always:
  - Back out of a puzzle with **ESC**.
  - Close the game from the hub with **ESC**.  
- Future extensions could add timers, radiation damage, or limited attempts to create explicit loss conditions.

### Controls / Input

- **Movement**
  - `W` / `A` / `S` / `D` — Move up / left / down / right  
  - Arrow keys — Alternative movement controls  

- **Interaction**
  - `E` — Interact / use (doors and consoles in the hub)  
  - Mouse left‑click — Click puzzle elements (fuses in Power Grid, tanks in Botany, couplers in Engineering)  

- **System**
  - `ESC` (in hub) — Quit the game  
  - `ESC` (in a room/puzzle) — Return to the hub  

### Design Decisions

#### Why We Chose This Game Type
- We started from a **text narrative** but wanted something more visual and tactile.  
- Pygame makes it straightforward to prototype **2D movement and room‑based puzzles** without heavy engine overhead.  
- A top‑down puzzle adventure fits the story well: exploring a station, interacting with consoles, and solving localized challenges in each wing.

#### Scope Decisions
- **Focused on:**
  - Core movement and room transitions from the **Central Hub**.  
  - Implementing **three main room puzzles** (Power Grid, Cipher, Botany/Engineering mini‑games).  
  - Clean, readable Python structure (separate classes for hub, puzzles, rooms, and player).  

- **Deferred (future work):**
  - Final cinematic **escape sequence** once all puzzles are solved.  
  - Audio, ambient music, and sound effects.  
  - Save/load system and a proper main menu.  
  - More complex AI / hazards (e.g., moving entities, oxygen/radiation timers).

### Known Issues & Limitations

#### Bugs
- **[Bug 1]: Pygame import error if not installed**  
  - *What happens*: Running `python game.py` without Pygame installed raises an `ImportError`.  
  - *Severity*: High for first‑time setup, but fixed by installing Pygame (`pip install pygame`).  


#### Incomplete Features
- **Final Escape Sequence** — Planned: when `power_restored`, `herd_secret_known`, and `slip_repaired` are all true, trigger a Slip‑Drive escape scene and credits.  
- **Additional Room Details** — Environmental art, more props, and non‑interactive flavor are minimal; focus so far is on logic, not visuals.  

### Recommendations for Week 6 QA

- **Input robustness**
  - Try holding multiple movement keys; confirm movement feels correct and bounded by the screen.  
  - Test pressing `E` when not near a door/console (nothing should break).  

- **Puzzle edge cases**
  - Power Grid:
    - Click fuses in random orders; ensure the puzzle always resets cleanly.  
  - Server Room:
    - Try uppercase, extra spaces, slightly wrong strings; verify only the exact decrypted phrase passes.  
  - Botany:
    - Click wrong tanks first, then correct one; verify message updates appropriately.  
  - Engineering:
    - Toggle couplers quickly and in different sequences; verify only **Up–Down–Up** is accepted.  

- **State consistency**
  - Solve a puzzle, return to hub with `ESC`, and re‑enter the room: does the puzzle show as solved / consistent?  
  - Confirm `ESC` always returns to hub from rooms and quits from the hub.

### File Structure

```text
.
├── game.py              # Main Pygame game loop, hub, player, and room/puzzle classes
├── README.md            # This file (game overview and documentation)
├── STANDUP_NOTES.md     # Daily standup notes
├── BLOCKERS.md          # Issues encountered & resolutions
├── CODE_STYLE.md        # Coding guidelines
└── KNOWN_ISSUES.md      # Detailed bug list and future fixes
```

> Optional: A `test_game.py` file can be added later for unit tests around puzzle logic.

### Development Notes

#### Technologies Used
- Python 3.8+  
- `pygame` 2.x  

#### Development Timeline (Week 5)
- **Day 1**: Story + mechanic spec (hub + three rooms + puzzles).  
- **Day 2–4**: Implemented movement, hub, and all room puzzles in Pygame.  
- **Day 5**: Refactoring, commenting, and README / documentation polish.  

#### Lessons Learned
- Managing **game modes** (`hub`, `power_puzzle`, `server`, `botany`, `engineering`) with a single loop keeps logic simple but requires careful input routing.  
- Building puzzles as **separate classes** (each with `handle_event` and `draw`) makes it much easier to expand or swap mechanics later.  
- Starting from a text adventure helped clarify story beats before committing to visuals and interactions.

### Contact

Questions about this game?  
Ask **Nayan Patel** or check `STANDUP_NOTES.md` for ongoing context and decisions.


