# MyFit.Pal

> **Small steps. Strong habits.** — A zero-dependency Object-Oriented Python web application for daily calorie, macro, step, and water tracking.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-OOP%20%7C%20REST%20JSON-73e0bd?style=flat-square)](#architecture)
[![Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-19273b?style=flat-square)](#getting-started)
[![Status](https://img.shields.io/badge/Status-Active%20Build-73e0bd?style=flat-square)](#overview)

## Overview

**MyFit.Pal** started as a command-line fitness script and was refactored with an agentic workflow into a structured, full-stack local web application. It serves a responsive browser interface and JSON REST endpoints from a lightweight Python backend while storing daily progress in a local `fitness_data.json` file.

## Features

- **Calorie & Macro Tracker:** Supports **Bulk** (`2,500 kcal`), **Cut** (`1,800 kcal`), and **Maintain** (`2,000 kcal`) goals with automatic macro distribution (`30% Protein / 40% Carbs / 30% Fats`).
- **Step Counter:** Tracks daily steps against a `3,000`-step goal and estimates calories burned (`0.4 kcal` per 10 steps) and distance covered (`0.5 m` per step).
- **Water Intake Tracker:** Monitors daily hydration in milliliters toward a `3,000 ml` target.
- **Daily History & Overview:** Displays live daily metrics on the **Home** tab, maintains a chronological history table on the **History** tab, and merges updates per date (`YYYY-MM-DD`) so existing daily metrics stay intact.

## Architecture

Built with clean separation of concerns using Python's standard library:

| Layer | Class | Responsibility |
| :--- | :--- | :--- |
| **Persistence** | `FitnessStore` | Thread-safe (`threading.Lock`) JSON read/write, schema validation, and per-day record merging |
| **Domain Logic** | `FitnessTracker` | Input validation and macro, calorie-burn, and distance calculations |
| **Transport / UI** | `FitnessRequestHandler` | Serves the single-page web UI (`/`) and handles JSON API routes |

## Tech Stack

- **Backend:** Python (`http.server`, `ThreadingHTTPServer`, `json`, `threading`, `pathlib`, `datetime`)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API, ARIA tab navigation)
- **Storage:** Local JSON (`fitness_data.json`)

## Getting Started

### 1. Clone & Run

```bash
git clone [https://github.com/ahsan-python/myfit-pal.git](https://github.com/ahsan-python/myfit-pal.git)
cd myfit-pal
python main.py
