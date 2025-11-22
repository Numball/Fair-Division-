# Fair Division — Rental Harmony (3-person implementation)

This repository contains a small Python implementation and front-end assets for exploring the Rental Harmony / fair-rent problem for three roommates and three rooms.

The core idea: split the total rent across rooms (a point in a 2-simplex). Each roommate has subjective preferences over rooms given a price vector; we seek a rent partition such that every roommate prefers a different room (an envy-free assignment). The implementation uses combinatorial triangulation (barycentric subdivision) and Sperner-style labelling to locate such a partition.

Contents
--------
- `rent.py` — main Python implementation for the 3-person problem (core algorithm & CLI runner).
- `index.html`, `js/`, `css/`, `partials/` — lightweight demo UI and assets (original demo was hosted at the project demo URL).

Why this project
-----------------
Rental Harmony is a classic fair division problem: how to divide a fixed total rent among rooms so that each roommate gets a room and a rent share they do not envy. This project implements an algorithmic approach for the three-person case and provides both a programmatic and visual exploration.

Key concepts and guarantees
---------------------------
- Subjective preferences: each roommate evaluates rooms using their own preference function over price splits.
- Envy-free goal: find a price vector where each roommate prefers a distinct room.
- Existence (informal): using Sperner's lemma / combinatorial triangulation techniques, we can show (and algorithmically find) a partition for which each person prefers a different room under reasonable continuity and monotonicity assumptions.

Algorithm overview (as implemented in `rent.py`)
-------------------------------------------------
This implementation focuses on the 3-person (3-room) case and uses the following ideas (documented and implemented in `rent.py`):

- Represent price splits as Points in the 2-simplex whose coordinates sum to `total_rent`.
- Each Point precomputes each housemate's choice by calling the configured strategy function for that housemate.
- Triangulate the simplex using a barycentric split: each triangle can be subdivided into six inner sub-triangles.
- Use a labelling scheme where the corner label specifies which housemate's choice to read at that corner. If a sub-triangle's corner choices contain all rooms, it's marked “good”. The algorithm follows a chain of good inner triangles, refining to the barycentre until convergence.

Implementation notes (from `rent.py` comments)
---------------------------------------------
- Numeric tolerance: a small EPS (0.01) is used for equality/sum checks and to zero-out tiny coordinates.
- Rounding: coordinates are rounded to 3 decimal places for cleaner output.
- Strategies: each housemate's preference is implemented as a function mapping a Point -> chosen room id. Example strategy types included:
	- `cheapskateStrategy` — picks the cheapest room (ties broken by lower index).
	- `randomStrategy` — picks a random room from available rooms.
	- `makeRoomNStrategy(n)` — always wants room `n` (with a small fallback rule implemented in the file).
	- `makeCapStrategy(prices)` — capped preference ordering: prefer rooms cheaper than a per-room cap, with a favorite and order.
- Triangle subdivision: `Triangle.initInnerTriangles()` builds the six sub-triangles and computes their labels/choices. `Triangle.getGoodInnerTriangle()` returns the first inner triangle marked good; the main loop follows this good triangle deeper until the barycentre stabilizes or a max iteration count is reached.

How to run the Python solver
----------------------------
Requirements: Python 3.x (tested with CPython). No external packages are required.

Run the script directly from a shell (PowerShell example on Windows):

```powershell
python .\rent.py
```

What you can configure in `rent.py`
----------------------------------
- `housemates` — list of housemate labels (default `['A','B','C']`).
- `rooms` — list of room ids (default `[1,2,3]`).
- `total_rent` — numeric total rent to split across rooms (default `1000`).
- `strategies` — mapping from housemate label to a strategy function. The file provides several ready-to-use examples and a `capA` example configuration. Change these to explore different preference profiles.
- `EPS`, `ROUNDING` — numeric tolerances and rounding used when constructing Points.

Interpreting the output
-----------------------
When you run `rent.py` as-is it will:
- build the outer simplex (three extreme splits where one room is free and the other rooms cover the rent),
- subdivide, find an inner sub-triangle marked "good" (its corner choices contain all rooms),
- follow that good triangle recursively, and
- print progress messages that show the barycentre of the current triangle, its corner labels and choices.

Custom experiments and tips
---------------------------
- Try different `strategies` configurations to model different roommate behavior (e.g., one roommate who strongly prefers a balcony, one who prefers cheapest room, etc.).
- Reduce `EPS` if you want stricter equality checks and finer numeric distinction (but be careful with floating point rounding).
- Add logging or small unit tests around `Point` and `Triangle` classes to verify strategy behavior and subdivision correctness if you modify the code.

Live Demo
---------------------------
-https://numball.github.io/Fair-Division-/

References
----------
- Su, Francis E., et al. "Rental Harmony: Sperner's lemma in fair division." (See literature on Rental Harmony and Sperner's Lemma for the theoretical background.)
- Sourced Idea from chunmun on github

