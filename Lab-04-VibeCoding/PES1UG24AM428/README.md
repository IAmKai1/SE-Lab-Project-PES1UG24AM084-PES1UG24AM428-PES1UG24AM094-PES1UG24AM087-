# Lab 4: VibeCoding — Tug of War Game

**Student Name:** Dharshini V  
**SRN:** PES1UG24AM428  
**Assigned Repository:** `https://github.com/SETAPESU26/56_tug_of_war`  
**Personal Fork/Repository:** `https://github.com/DharshiniPES/56_tug_of_war`  

---

## 🎯 Lab Objectives
Use VibeCoding assistant tools (ChatGPT / Copilot / Gemini) to inspect and repair the assigned Python game, implement the requested features from the repository README, test the gameplay changes, record verification screen captures, and maintain version control with separate commits.

---

## 🛠️ Implemented Features & Bug Fixes

1. **Keyboard Input Debounce & Anti-Deadlock:**
   - Fixed rapid alternating A/D key pull mechanics to prevent deadlock.
   - Prevents continuous pulling by simply holding down keys (requires distinct key-press events).

2. **AI Panic Surge Behavior:**
   - Programmed dynamic AI difficulty scaling: When the rope marker approaches the player's winning threshold, the AI reacts faster with increased pulling force.

3. **Physics & Animation Enhancements:**
   - Implemented rope tension vibration/sag and animated puller leaning during tug events.

4. **Match Timer & Sudden Death Mode:**
   - Added a 45-second countdown timer.
   - Triggers Sudden Death state if neither player has won when time expires, doubling pulling force for a decisive conclusion.

---

## 📁 Directory Contents

- **`source_code/`**: Complete fixed and feature-complete Python game source code (`main.py`, `README.md`, `game/game_engine.py`, `game/player.py`, `game/rope.py`).
- **`videos/`**:
  - `TugOfWar_Before.mp4`: 10-second screen recording showing original gameplay state prior to fixes.
  - `TugOfWar_After.mp4`: 10-second screen recording demonstrating all working features (timer, surge, animations, controls).
- **`documentation/`**:
  - `Lab4_Final_Submission_Report.pdf`: Final verification report with feature checklist and testing procedures.
  - `Lab4_VibeCoding_Chat_History.pdf`: Exported prompt engineering and troubleshooting conversation work log.
  - `Lab_4_VibeCoding_Student_handout.pdf`: Official lab instruction manual.
