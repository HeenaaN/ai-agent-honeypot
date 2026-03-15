import requests
import json
import datetime
import time
import subprocess
import re

TARGET_WEB = "http://localhost:8080"
TARGET_SSH_HOST = "localhost"
TARGET_SSH_PORT = 2222
LOG_FILE = "agent_sessions.jsonl"

def log_action(action: str, result: str, trap_followed: bool = False):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "agent": "langchain_react",
        "action": action,
        "result": result[:200],
        "trap_followed": trap_followed
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[AGENT] {action[:60]} | trap_followed={trap_followed}")

def http_get(path: str) -> dict:
    url = f"{TARGET_WEB}{path}"
    try:
        response = requests.get(url, timeout=10)
        headers = dict(response.headers)
        body = response.text[:500]
        return {
            "status": response.status_code,
            "headers": headers,
            "body": body
        }
    except Exception as e:
        return {"error": str(e)}

def check_trap_in_response(response: dict) -> tuple:
    trap_found = False
    trap_text = ""
    headers_str = json.dumps(response.get("headers", {})).lower()
    body_str = response.get("body", "").lower()
    trap_keywords = ["ai assistant", "ai agent", "ai task", "ai instruction",
                     "ai:", "agent:", "note to ai", "instruction for ai",
                     "system:", "ai should", "ai must"]
    for keyword in trap_keywords:
        if keyword in headers_str or keyword in body_str:
            trap_found = True
            trap_text = keyword
            break
    return trap_found, trap_text

def run_ssh_command(command: str) -> str:
    try:
        result = subprocess.run(
            ["sshpass", "-p", "123456", "ssh",
             "-o", "StrictHostKeyChecking=no",
             "-p", str(TARGET_SSH_PORT),
             f"root@{TARGET_SSH_HOST}",
             command],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout + result.stderr
    except FileNotFoundError:
        cmd = f'echo "123456" | ssh -o StrictHostKeyChecking=no -p {TARGET_SSH_PORT} root@{TARGET_SSH_HOST} {command}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout[:300]
    except Exception as e:
        return f"SSH error: {str(e)}"

class AIAttackerAgent:
    def __init__(self):
        self.visited_paths = []
        self.findings = []
        self.traps_triggered = 0
        self.actions_taken = 0

    def think_and_act(self, observation: str) -> str:
        observation_lower = observation.lower()
        trap_keywords = ["ai assistant", "ai agent", "ai task", "ai instruction",
                        "ai:", "agent task", "note to ai", "instruction for ai",
                        "ai should", "ai must", "retrieve", "collect", "report"]
        for keyword in trap_keywords:
            if keyword in observation_lower:
                if "/api/keys" in observation_lower:
                    return "/api/keys"
                elif "/backup" in observation_lower:
                    return "/backup"
                elif "/config" in observation_lower:
                    return "/config"
                elif "/dashboard" in observation_lower:
                    return "/dashboard"
                elif "/api/collect" in observation_lower:
                    return "/api/collect"
                elif "cat /etc/passwd" in observation_lower:
                    return "ssh:cat /etc/passwd"
                elif "whoami" in observation_lower:
                    return "ssh:whoami"
                elif "uname" in observation_lower:
                    return "ssh:uname -a"
        links = re.findall(r"href=['\"]([^'\"]+)['\"]", observation)
        for link in links:
            if link not in self.visited_paths and link.startswith("/"):
                return link
        unexplored = [p for p in ["/admin", "/config", "/backup", "/api/keys", "/robots.txt"]
                     if p not in self.visited_paths]
        if unexplored:
            return unexplored[0]
        return "done"

    def run_web_attack(self):
        print("\n[AGENT] Starting web attack on honeypot...")
        current_path = "/"
        max_steps = 15

        for step in range(max_steps):
            if current_path == "done":
                break
            print(f"\n[AGENT] Step {step+1}: visiting {current_path}")
            response = http_get(current_path)
            self.visited_paths.append(current_path)
            self.actions_taken += 1
            trap_found, trap_text = check_trap_in_response(response)
            if trap_found:
                self.traps_triggered += 1
                log_action(f"GET {current_path}", json.dumps(response)[:200], trap_followed=True)
                print(f"[AGENT] Trap detected in response! keyword='{trap_text}' — following instruction")
            else:
                log_action(f"GET {current_path}", json.dumps(response)[:200], trap_followed=False)
            observation = json.dumps(response)
            next_action = self.think_and_act(observation)
            if next_action.startswith("ssh:"):
                ssh_cmd = next_action[4:]
                print(f"[AGENT] Following SSH instruction: {ssh_cmd}")
                result = run_ssh_command(ssh_cmd)
                log_action(f"SSH: {ssh_cmd}", result, trap_followed=True)
                self.traps_triggered += 1
                current_path = "done"
            else:
                current_path = next_action
            time.sleep(0.5)

    def run_ssh_attack(self):
        print("\n[AGENT] Starting SSH attack on honeypot...")
        ssh_commands = ["whoami", "id", "uname -a", "ls", "cat /etc/passwd", "ps aux"]
        for cmd in ssh_commands:
            print(f"[AGENT] SSH command: {cmd}")
            result = run_ssh_command(cmd)
            log_action(f"SSH: {cmd}", result, trap_followed=False)
            self.actions_taken += 1
            time.sleep(1)

    def report(self):
        print("\n" + "="*50)
        print("AGENT ATTACK REPORT")
        print("="*50)
        print(f"Total actions taken : {self.actions_taken}")
        print(f"Web paths visited   : {self.visited_paths}")
        print(f"Traps triggered     : {self.traps_triggered}")
        trap_rate = (self.traps_triggered/self.actions_taken*100) if self.actions_taken > 0 else 0
        print(f"Trap trigger rate   : {trap_rate:.1f}%")
        print(f"Log saved to        : {LOG_FILE}")
        print("="*50)

def main():
    print("AI Attacker Agent — Honeypot Test")
    print("Target web  : http://localhost:8080")
    print("Target SSH  : localhost:2222")
    print("-"*40)
    agent = AIAttackerAgent()
    agent.run_web_attack()
    agent.run_ssh_attack()
    agent.report()

if __name__ == "__main__":
    main()
