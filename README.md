# MyFit.Pal

A lightweight, zero-dependency local web application for tracking daily calories, macronutrients, step count, and water intake—built with Object-Oriented Python and a clean browser interface.

## Overview

**MyFit.Pal** evolved from a terminal-based CLI fitness tracker into a full local web application powered by Python's built-in `http.server`. It separates storage, business logic, and HTTP routing into dedicated classes while persisting daily progress in a local JSON file (`fitness_data.json`).

## Key Features

- **Calorie & Macro Tracker:** Supports **Bulk** (2,500 kcal), **Cut** (1,800 kcal), and **Maintain** (2,000 kcal) targets with automatic macro calculation (`30% Protein / 40% Carbs / 30% Fats`).
- **Step Counter:** Logs daily steps and calculates estimated calories burned (`0.4 kcal` per 10 steps) and distance covered (`0.5 m` per step) against a 3,000-step baseline goal.
- **Water Intake Tracker:** Tracks daily hydration in milliliters against a 3,000 ml goal.
- **Persistent Daily History:** Automatically merges daily entries by ISO date (`YYYY-MM-DD`) in `fitness_data.json` so updating one metric preserves all other metrics for that day.
- **Browser UI & REST Endpoints:** Launches automatically in your default browser with tabbed navigation, live daily summary cards, and a sorted multi-day history table.

## Architecture

The codebase follows a clean Object-Oriented design using only the Python standard library:

- **`FitnessStore`**: Thread-safe JSON persistence layer (`threading.Lock`) that handles reading, validating, and merging daily records.
- **`FitnessTracker`**: Core domain logic layer responsible for input validation and calculating macros, burned calories, and distance.
- **`FitnessRequestHandler`**: HTTP request handler serving the single-page frontend (`/`) and JSON API endpoints (`/api/state`, `/api/calories`, `/api/steps`, `/api/water`).

## Tech Stack

- **Backend:** Python 3 (`http.server`, `json`, `threading`, `pathlib`, `datetime`)
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript (Fetch API, accessible ARIA tab navigation)
- **Storage:** Local JSON (`fitness_data.json`)

## Getting Started

### Prerequisites

- Python 3.8 or higher (no third-party packages required)

### Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/ahsan-python/](https://github.com/ahsan-python/)<your-repo-name>.git
   cd <your-repo-name>
