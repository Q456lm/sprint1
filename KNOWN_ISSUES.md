## Known Issues

### Bug 1: Boss Room End State UI Not Rendering
- **Severity:** Critical
- **Description:** Upon completing the Boss Room encounter (either by eliminating the swarm or dying), the game state transitions to `win` or `game_over`, but the text overlays ("ALL ENTITIES ELIMINATED" or "CONSUMED BY THE SWARM") defined in `BossRoom.draw` do not appear. The player is left on the fight screen with no feedback.
- **Repro Steps:** 1. Launch the game and navigate to the Boss Room.
  2. Defeat all 15 `HerdMember` enemies to trigger the win condition, OR allow player HP to drop to 0.
  3. Observe that the specific victory/defeat text and background dimming do not render.
- **Status:** Fixed

### Bug 2: Botany Room Simulation Diagrams Invisible
- **Severity:** Major
- **Description:** The moving particle simulations ("diagrams") inside tanks A, B, and C in the Botany Room are not visible. While the `sim_particles` logic appears to update positions for bouncing, swarming, and circling behaviors, the `pygame.draw.circle` calls are not producing visible output on the tank surfaces, making the puzzle unsolvable.
- **Repro Steps:**
  1. Enter the Botany Room from the Hub.
  2. Inspect the three containment tanks (A, B, C).
  3. Attempt to identify the "Organized Intelligence" pattern.
  4. Note that the tanks appear empty despite the simulation code running.
- **Status:** Fixed
