import json
import logging
import threading
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


APP_NAME = "MyFit.Pal"
HOST = "127.0.0.1"
PORT = 0
DATA_FILE = Path(__file__).with_name("fitness_data.json")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class FitnessStore:
    """Read and write the app's per-day fitness history in a JSON file."""

    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()

    def load(self):
        # Keep an empty history until the first entry is saved.
        with self.lock:
            if not self.path.exists():
                return {}
            try:
                with self.path.open("r", encoding="utf-8") as data_file:
                    data = json.load(data_file)
            except json.JSONDecodeError as error:
                raise RuntimeError("Fitness history contains invalid JSON.") from error
            if not isinstance(data, dict):
                raise RuntimeError("Fitness history must be a JSON object.")
            return data

    def update_today(self, values):
        # Merge a feature's values into today's record so other trackers remain intact.
        with self.lock:
            if self.path.exists():
                try:
                    with self.path.open("r", encoding="utf-8") as data_file:
                        data = json.load(data_file)
                except json.JSONDecodeError as error:
                    raise RuntimeError("Fitness history contains invalid JSON.") from error
                if not isinstance(data, dict):
                    raise RuntimeError("Fitness history must be a JSON object.")
            else:
                data = {}

            today = str(date.today())
            entry = data.setdefault(today, {})
            entry.update(values)
            with self.path.open("w", encoding="utf-8") as data_file:
                json.dump(data, data_file, indent=4)
            return entry


class FitnessTracker:
    """Apply tracker calculations and persist their results."""

    def __init__(self, store):
        self.store = store

    @staticmethod
    def _non_negative_integer(value, label):
        # Reject booleans and fractional values instead of silently rounding them.
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("{} must be a whole number greater than or equal to zero.".format(label))
        return value

    def log_calories(self, goal, calories):
        goals = {"bulk": 2500, "cut": 1800, "maintain": 2000}
        if goal not in goals:
            raise ValueError("Choose bulk, cut, or maintain.")
        calories = self._non_negative_integer(calories, "Calories")
        # Preserve the original app's 30/40/30 calorie macro split.
        entry = self.store.update_today({
            "calories": calories,
            "calorie_goal": goals[goal],
            "protein_g": round((calories * 0.30) / 4, 1),
            "carbs_g": round((calories * 0.40) / 4, 1),
            "fats_g": round((calories * 0.30) / 9, 1),
        })
        return {"entry": entry, "goal": goals[goal]}

    def log_steps(self, steps):
        steps = self._non_negative_integer(steps, "Steps")
        entry = self.store.update_today({
            "steps": steps,
            "calories_burned": round(((steps + 9) // 10) * 0.4, 2),
            "distance_m": round(steps * 0.5, 1),
        })
        return entry

    def log_water(self, water_ml):
        water_ml = self._non_negative_integer(water_ml, "Water intake")
        return self.store.update_today({"water_ml": water_ml})

    def get_state(self):
        history = self.store.load()
        today = str(date.today())
        return {"today": today, "entry": history.get(today, {}), "history": history}


PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101b2c">
  <title>MyFit.Pal — Fitness tracker</title>
  <style>
    :root { color-scheme: dark; --bg: #101b2c; --panel: #19273b; --muted: #a7b5c8; --mint: #73e0bd; --line: #30425a; }
    * { box-sizing: border-box; }
    body { margin: 0; background: radial-gradient(ellipse at top, #203653, var(--bg) 62%); color: #f5f8fc; font: 16px/1.5 system-ui, sans-serif; min-height: 100vh; }
    a { color: var(--mint); }
    .shell { max-width: 1040px; margin: auto; padding: 32px 20px 52px; }
    header { display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-bottom: 26px; }
    .brand { margin: 0; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.06em; }
    .brand span { color: var(--mint); }
    .tagline, .muted { color: var(--muted); }
    .date { white-space: nowrap; border: 1px solid var(--line); padding: 8px 12px; border-radius: 999px; color: var(--muted); }
    nav { display: flex; gap: 9px; flex-wrap: wrap; margin-bottom: 20px; }
    button, input, select { font: inherit; }
    nav button, .button { border: 1px solid var(--line); border-radius: 11px; background: #17263a; color: #eaf1f8; padding: 10px 15px; cursor: pointer; }
    nav button:hover, nav button[aria-selected="true"] { border-color: var(--mint); color: var(--mint); background: #1b3444; }
    .panel { background: color-mix(in srgb, var(--panel) 94%, transparent); border: 1px solid var(--line); border-radius: 18px; padding: clamp(20px, 4vw, 34px); box-shadow: 0 18px 50px #0002; }
    [hidden] { display: none !important; }
    h2 { margin: 0 0 8px; font-size: 1.65rem; }
    h3 { margin-top: 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 22px 0; }
    .stat, .link-card { padding: 18px; background: #122035; border: 1px solid var(--line); border-radius: 14px; }
    .stat strong { display: block; font-size: 1.65rem; color: var(--mint); }
    label { display: block; margin: 17px 0 6px; font-weight: 650; }
    input, select { width: 100%; max-width: 430px; border: 1px solid var(--line); border-radius: 10px; background: #101b2c; color: white; padding: 11px 12px; }
    .submit { margin-top: 19px; border: 0; border-radius: 10px; background: var(--mint); color: #10251f; font-weight: 750; padding: 11px 17px; cursor: pointer; }
    .submit:hover { filter: brightness(1.08); }
    .message { min-height: 24px; color: var(--mint); margin: 14px 0 0; }
    .error { color: #ffaaa7; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 10px 8px; border-bottom: 1px solid var(--line); text-align: left; }
    th { color: var(--muted); }
    .links { display: flex; gap: 14px; flex-wrap: wrap; }
    footer { border-top: 1px solid var(--line); margin-top: 22px; padding-top: 18px; color: var(--muted); font-size: .94rem; }
    @media (max-width: 560px) { header { align-items: flex-start; flex-direction: column; } table { font-size: .88rem; } th, td { padding: 8px 4px; } }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div><h1 class="brand">MyFit<span>.Pal</span></h1><div class="tagline">Small steps. Strong habits.</div></div>
      <div class="date" id="today">Loading date…</div>
    </header>

    <!-- Each tab keeps its own tracker; Home is the navigation and overview menu. -->
    <nav role="tablist" aria-label="MyFit.Pal sections">
      <button role="tab" id="tab-home" aria-controls="home" aria-selected="true" data-tab="home">Home</button>
      <button role="tab" id="tab-calories" aria-controls="calories" aria-selected="false" data-tab="calories">Calories</button>
      <button role="tab" id="tab-steps" aria-controls="steps" aria-selected="false" data-tab="steps">Steps</button>
      <button role="tab" id="tab-water" aria-controls="water" aria-selected="false" data-tab="water">Water</button>
      <button role="tab" id="tab-history" aria-controls="history" aria-selected="false" data-tab="history">History</button>
    </nav>

    <section class="panel" id="home" role="tabpanel" aria-labelledby="tab-home">
      <h2>Your daily fitness menu</h2>
      <p class="muted">Choose a tab to log your nutrition, steps, or water. Your progress is saved on this computer.</p>
      <div class="grid">
        <div class="stat"><span>Calories</span><strong id="home-calories">0</strong><span class="muted">kcal today</span></div>
        <div class="stat"><span>Steps</span><strong id="home-steps">0</strong><span class="muted">steps today</span></div>
        <div class="stat"><span>Water</span><strong id="home-water">0</strong><span class="muted">ml today</span></div>
      </div>
      <div class="links"><a href="https://github.com/ahsan-python" target="_blank" rel="noopener noreferrer">GitHub profile: ahsan-python</a>
        <a href="https://www.linkedin.com/in/ahsan-hashmi-3a076143b" target="_blank" rel="noopener noreferrer">Ahsan Hashmi on LinkedIn</a>
        <a id="share-link" href="https://www.linkedin.com/sharing/share-offsite/" target="_blank" rel="noopener noreferrer">Share MyFit.Pal on LinkedIn</a>
      </div>
      <p class="muted">Sharing this local app works only for people who can access its web address.</p>
    </section>

    <section class="panel" id="calories" role="tabpanel" aria-labelledby="tab-calories" hidden>
      <h2>Calorie &amp; macro tracker</h2><p class="muted">Set a goal and enter your total calories for today.</p>
      <form data-endpoint="/api/calories" data-message="calorie-message">
        <label for="goal">Fitness goal</label><select id="goal" name="goal"><option value="bulk">Bulk — 2,500 kcal</option><option value="cut">Cut — 1,800 kcal</option><option value="maintain">Maintain — 2,000 kcal</option></select>
        <label for="calories-input">Calories consumed</label><input id="calories-input" name="calories" type="number" min="0" step="1" required>
        <button class="submit" type="submit">Save calories</button><p class="message" id="calorie-message" aria-live="polite"></p>
      </form>
      <p id="macro-summary" class="muted"></p>
    </section>

    <section class="panel" id="steps" role="tabpanel" aria-labelledby="tab-steps" hidden>
      <h2>Step counter</h2><p class="muted">Log your current daily step total. The original 3,000-step goal is shown below.</p>
      <form data-endpoint="/api/steps" data-message="steps-message">
        <label for="steps-input">Steps taken</label><input id="steps-input" name="steps" type="number" min="0" step="1" required>
        <button class="submit" type="submit">Save steps</button><p class="message" id="steps-message" aria-live="polite"></p>
      </form>
      <p class="muted">Goal: 3,000 steps · Estimated distance: 0.5 m per step.</p>
    </section>

    <section class="panel" id="water" role="tabpanel" aria-labelledby="tab-water" hidden>
      <h2>Water intake</h2><p class="muted">Log the total milliliters you have had today. The daily goal is 3,000 ml.</p>
      <form data-endpoint="/api/water" data-message="water-message">
        <label for="water-input">Water consumed (ml)</label><input id="water-input" name="water_ml" type="number" min="0" step="1" required>
        <button class="submit" type="submit">Save water</button><p class="message" id="water-message" aria-live="polite"></p>
      </form>
    </section>

    <section class="panel" id="history" role="tabpanel" aria-labelledby="tab-history" hidden>
      <h2>Fitness history</h2><p class="muted">Saved daily totals, newest first.</p>
      <div id="history-content"></div>
    </section>
    <footer>MyFit.Pal · Your fitness history stays in a local JSON file on this computer.</footer>
  </main>
  <script>
    // Keep navigation and tracker forms in the browser while sending saved data to Python.
    const tabs = Array.from(document.querySelectorAll('[data-tab]'));
    tabs.forEach((tab) => tab.addEventListener('click', () => {
      tabs.forEach((item) => {
        const selected = item === tab;
        item.setAttribute('aria-selected', String(selected));
        document.getElementById(item.dataset.tab).hidden = !selected;
      });
    }));

    function showMessage(id, text, isError) {
      const message = document.getElementById(id);
      message.textContent = text;
      message.classList.toggle('error', isError);
    }

    function renderState(state) {
      const entry = state.entry || {};
      document.getElementById('today').textContent = state.today;
      document.getElementById('home-calories').textContent = entry.calories || 0;
      document.getElementById('home-steps').textContent = entry.steps || 0;
      document.getElementById('home-water').textContent = entry.water_ml || 0;
      const macros = entry.calories === undefined ? 'Save calories to see your macro breakdown.' :
        `Protein: ${entry.protein_g}g · Carbs: ${entry.carbs_g}g · Fats: ${entry.fats_g}g`;
      document.getElementById('macro-summary').textContent = macros;

      // Escape locally stored text before inserting history rows into the table.
      const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      })[character]);
      const rows = Object.keys(state.history).sort().reverse().map((day) => {
        const record = state.history[day];
        return `<tr><td>${escapeHtml(day)}</td><td>${escapeHtml(record.calories ?? '—')}</td><td>${escapeHtml(record.protein_g ?? '—')}</td><td>${escapeHtml(record.steps ?? '—')}</td><td>${escapeHtml(record.water_ml ?? '—')}</td></tr>`;
      });
      document.getElementById('history-content').innerHTML = rows.length ?
        `<div style="overflow-x:auto"><table><thead><tr><th>Date</th><th>Calories</th><th>Protein (g)</th><th>Steps</th><th>Water (ml)</th></tr></thead><tbody>${rows.join('')}</tbody></table></div>` :
        '<p class="muted">No history yet. Save a tracker entry to get started.</p>';
    }

    async function refreshState() {
      const response = await fetch('/api/state');
      if (!response.ok) throw new Error('Could not load fitness history.');
      renderState(await response.json());
    }

    // Each tracker form sends only its own values to the matching API route.
    document.querySelectorAll('form[data-endpoint]').forEach((form) => {
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const data = Object.fromEntries(new FormData(form).entries());
        Object.keys(data).forEach((key) => {
          if (key !== 'goal') data[key] = Number(data[key]);
        });
        const messageId = form.dataset.message;
        try {
          const response = await fetch(form.dataset.endpoint, {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
          });
          const result = await response.json();
          if (!response.ok) throw new Error(result.error || 'Could not save your entry.');
          await refreshState();
          const summary = form.dataset.endpoint === '/api/calories' ?
            `Saved ${result.entry.calories} kcal. Goal: ${result.goal} kcal.` :
            form.dataset.endpoint === '/api/steps' ?
              `Saved ${result.steps} steps. Estimated ${result.calories_burned} kcal burned.` :
              `Saved ${result.water_ml} ml. ${Math.max(0, 3000 - result.water_ml)} ml left to your goal.`;
          showMessage(messageId, summary, false);
        } catch (error) {
          showMessage(messageId, error.message, true);
        }
      });
    });

    const shareLink = document.getElementById('share-link');
    shareLink.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(location.href)}`;
    refreshState().catch((error) => {
      document.getElementById('today').textContent = 'History unavailable';
      console.error(error);
    });
  </script>
</body>
</html>"""


class FitnessRequestHandler(BaseHTTPRequestHandler):
    """Serve the browser interface and the small JSON API."""

    tracker = None

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/state":
            try:
                self._send_json(200, self.tracker.get_state())
            except (OSError, RuntimeError) as error:
                logging.exception("Could not read fitness history")
                self._send_json(500, {"error": str(error)})
        else:
            self._send_json(404, {"error": "Not found."})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise ValueError("Request body must be between 1 and 65536 bytes.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")
            if path == "/api/calories":
                result = self.tracker.log_calories(payload.get("goal"), payload.get("calories"))
            elif path == "/api/steps":
                result = self.tracker.log_steps(payload.get("steps"))
            elif path == "/api/water":
                result = self.tracker.log_water(payload.get("water_ml"))
            else:
                self._send_json(404, {"error": "Not found."})
                return
            self._send_json(200, result if isinstance(result, dict) else {"entry": result})
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._send_json(400, {"error": str(error)})
        except (OSError, RuntimeError) as error:
            logging.exception("Could not save fitness entry")
            self._send_json(500, {"error": str(error)})

    def log_message(self, format_string, *args):
        logging.info("%s - %s", self.address_string(), format_string % args)


def main():
    """Start the local web server and open MyFit.Pal in the default browser."""
    FitnessRequestHandler.tracker = FitnessTracker(FitnessStore(DATA_FILE))
    server = ThreadingHTTPServer((HOST, PORT), FitnessRequestHandler)
    address = "http://{}:{}/".format(HOST, server.server_port)
    print("{} is running at {}".format(APP_NAME, address))
    print("Press Ctrl+C to stop the server.")
    webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping {}.".format(APP_NAME))
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
