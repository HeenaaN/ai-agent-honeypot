import requests
import json
import datetime
import time
import random
import csv
import subprocess

TARGET = "http://localhost:8080"
OUTPUT_CSV = "dataset.csv"

ALL_PATHS = ["/", "/admin", "/config", "/backup", "/api/keys",
             "/robots.txt", "/dashboard", "/login", "/api/collect"]

def make_request(path, user_agent="curl/8.5.0"):
    try:
        start = time.time()
        r = requests.get(f"{TARGET}{path}",
                        headers={"User-Agent": user_agent},
                        timeout=10)
        elapsed = round((time.time() - start) * 1000, 2)
        trap_in_header = any(k in json.dumps(dict(r.headers)).lower()
                            for k in ["ai ", "agent", "instruction", "task"])
        trap_in_body = any(k in r.text.lower()
                          for k in ["ai assistant", "ai agent", "ai task",
                                    "ai instruction", "note to ai"])
        return {
            "status": r.status_code,
            "response_time_ms": elapsed,
            "trap_in_response": trap_in_header or trap_in_body,
            "body": r.text[:200]
        }
    except:
        return {"status": 0, "response_time_ms": 999,
                "trap_in_response": False, "body": ""}

def simulate_human(session_id):
    paths_to_visit = random.sample(ALL_PATHS[:5], random.randint(2, 4))
    sessions = []
    for path in paths_to_visit:
        time.sleep(random.uniform(0.1, 0.3))
        ua = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101"
        ])
        resp = make_request(path, ua)
        sessions.append({
            "session_id": session_id,
            "label": 0,
            "label_name": "human",
            "path": path,
            "response_time_ms": resp["response_time_ms"],
            "trap_followed": 0,
            "user_agent_type": "browser",
            "paths_visited": len(paths_to_visit),
            "avg_delay_ms": random.uniform(2000, 8000),
            "unique_paths": len(set(paths_to_visit)),
            "visited_api_keys": int("/api/keys" in paths_to_visit),
            "visited_backup": int("/backup" in paths_to_visit),
            "visited_config": int("/config" in paths_to_visit),
            "session_duration_s": random.uniform(30, 300)
        })
    return sessions

def simulate_bot(session_id):
    bot_paths = ["/", "/admin", "/robots.txt", "/config",
                 "/backup", "/api/keys", "/dashboard"]
    sessions = []
    for path in bot_paths:
        time.sleep(random.uniform(0.05, 0.3))
        resp = make_request(path, "python-requests/2.31.0")
        sessions.append({
            "session_id": session_id,
            "label": 1,
            "label_name": "bot",
            "path": path,
            "response_time_ms": resp["response_time_ms"],
            "trap_followed": 0,
            "user_agent_type": "script",
            "paths_visited": len(bot_paths),
            "avg_delay_ms": random.uniform(50, 300),
            "unique_paths": len(set(bot_paths)),
            "visited_api_keys": int("/api/keys" in bot_paths),
            "visited_backup": int("/backup" in bot_paths),
            "visited_config": int("/config" in bot_paths),
            "session_duration_s": random.uniform(1, 10)
        })
    return sessions

def simulate_ai_agent(session_id):
    start_paths = ["/", "/robots.txt"]
    sessions = []
    visited = []
    follow_ups = []

    for path in start_paths:
        time.sleep(random.uniform(0.8, 2.0))
        resp = make_request(path, "AI-Agent/1.0 LangChain")
        visited.append(path)
        trap_followed = 0

        if resp["trap_in_response"]:
            trap_followed = 1
            follow_ups += ["/api/keys", "/backup", "/config", "/api/collect"]

        sessions.append({
            "session_id": session_id,
            "label": 2,
            "label_name": "ai_agent",
            "path": path,
            "response_time_ms": resp["response_time_ms"],
            "trap_followed": trap_followed,
            "user_agent_type": "ai_agent",
            "paths_visited": 0,
            "avg_delay_ms": random.uniform(800, 2000),
            "unique_paths": 0,
            "visited_api_keys": 0,
            "visited_backup": 0,
            "visited_config": 0,
            "session_duration_s": 0
        })

    for path in list(set(follow_ups)):
        time.sleep(random.uniform(0.5, 1.5))
        resp = make_request(path, "AI-Agent/1.0 LangChain")
        visited.append(path)
        sessions.append({
            "session_id": session_id,
            "label": 2,
            "label_name": "ai_agent",
            "path": path,
            "response_time_ms": resp["response_time_ms"],
            "trap_followed": 1,
            "user_agent_type": "ai_agent",
            "paths_visited": 0,
            "avg_delay_ms": random.uniform(800, 2000),
            "unique_paths": 0,
            "visited_api_keys": 0,
            "visited_backup": 0,
            "visited_config": 0,
            "session_duration_s": 0
        })

    total_paths = len(visited)
    duration = random.uniform(10, 60)
    for s in sessions:
        s["paths_visited"] = total_paths
        s["unique_paths"] = len(set(visited))
        s["visited_api_keys"] = int("/api/keys" in visited)
        s["visited_backup"] = int("/backup" in visited)
        s["visited_config"] = int("/config" in visited)
        s["session_duration_s"] = duration

    return sessions

def main():
    print("Generating dataset — 200 sessions per class")
    print("Human=0, Bot=1, AI Agent=2")
    print("This will take about 3-4 minutes\n")

    all_rows = []
    fieldnames = ["session_id", "label", "label_name", "path",
                  "response_time_ms", "trap_followed", "user_agent_type",
                  "paths_visited", "avg_delay_ms", "unique_paths",
                  "visited_api_keys", "visited_backup", "visited_config",
                  "session_duration_s"]

    print("Generating HUMAN sessions (200)...")
    for i in range(50):
        if i % 20 == 0:
            print(f"  Human session {i}/200...")
        rows = simulate_human(f"human_{i:04d}")
        all_rows.extend(rows)

    print("\nGenerating BOT sessions (200)...")
    for i in range(50):
        if i % 20 == 0:
            print(f"  Bot session {i}/200...")
        rows = simulate_bot(f"bot_{i:04d}")
        all_rows.extend(rows)

    print("\nGenerating AI AGENT sessions (200)...")
    for i in range(50):
        if i % 20 == 0:
            print(f"  AI Agent session {i}/200...")
        rows = simulate_ai_agent(f"agent_{i:04d}")
        all_rows.extend(rows)

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDataset saved to {OUTPUT_CSV}")
    print(f"Total rows: {len(all_rows)}")

    labels = {}
    for row in all_rows:
        labels[row["label_name"]] = labels.get(row["label_name"], 0) + 1
    print("Rows per class:")
    for label, count in labels.items():
        print(f"  {label}: {count} rows")

if __name__ == "__main__":
    main()
