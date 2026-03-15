import subprocess
import socket
import requests
import time
import sys
import csv
import re
from datetime import datetime

VERSION = "1.5"

HOSTS = [
    "google.com",
    "cloudflare.com",
    "github.com"
]

LOG_FILE = "logs/netcheck_log.csv"
TRACEROUTE_LOG = "logs/traceroute_log.txt"

LATENCY_SPIKE_THRESHOLD = 100  # milliseconds
#LATENCY_SPIKE_THRESHOLD = 20  # milliseconds -- for testing
SPIKE_COOLDOWN = 300  # seconds
last_spike_time = {}

SLOW_HOP_THRESHOLD = 120  # milliseconds
#SLOW_HOP_THRESHOLD = 15  # milliseconds -- for testing


def init_log():

    import os
    import csv

    if not os.path.exists(LOG_FILE):

        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "host", "latency"])


def ping_test(host):

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        for line in result.stdout.split("\n"):
            if "time=" in line:
                latency = line.split("time=")[1].split()[0]
                return latency

    return float(latency)


def dns_test(host):

    try:
        ip = socket.gethostbyname(host)
        return ip
    except Exception:
        return None


def http_test(url):

    try:
        response = requests.get(url, timeout=5)
        return response.status_code
    except Exception:
        return None


def watch_mode():

    print("Monitoring network every 30 seconds...\n")

    while True:

        timestamp = datetime.now().strftime("%H:%M:%S")

        for host in HOSTS:

            latency = ping_test(host)

            if latency:
                
                latency = float(latency)
                
                log_latency(host, latency)
                
                if latency > LATENCY_SPIKE_THRESHOLD:
                    
                    now = time.time()
                    last = last_spike_time.get(host, 0)
                    
                    if now - last > SPIKE_COOLDOWN:

                        print(f"\n⚠️  LATENCY SPIKE: {host} = {latency} ms")
                        print("Running traceroute...\n")
                        
                        trace_output = run_traceroute(host)
                        log_traceroute(host, trace_output)
                        analyze_traceroute(trace_output)
                        
                        last_spike_time[host] = now
                    
                    else:
                        print(f"Spike suppressed for {host} (cooldown active)")
                
                print(f"[{timestamp}] {host:<15} {latency} ms")
            else:
                print(f"[{timestamp}] {host:<15} FAILED")

        print()

        time.sleep(30)


def log_latency(host, latency):

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([timestamp, host, latency])


def run_traceroute(host):

    try:
        result = subprocess.run(
            ["traceroute", "-m", "10", host],   # limit to 10 hops
            capture_output=True,
            text=True,
            timeout=15
        )

        return result.stdout

    except Exception as e:
        return f"Traceroute failed: {e}"


def log_traceroute(host, output):

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(TRACEROUTE_LOG, "a") as f:

        f.write(f"\n===== {timestamp} | {host} =====\n")
        f.write(output)
        f.write("\n")


def analyze_traceroute(trace_output):

    slowest_hop = None
    slowest_latency = 0
    filtered_hops = 0

    for line in trace_output.splitlines():

        latencies = re.findall(r"(\d+\.\d+)\s*ms", line)

        if latencies:

            values = [float(x) for x in latencies]
            latency = max(values)

            if latency > slowest_latency:
                slowest_latency = latency
                slowest_hop = line.strip()

        if "* * *" in line:
            filtered_hops += 1
        
    if filtered_hops:
        print(f"⚠️ {filtered_hops} hops did not respond (likely filtered by ISP)")
    
    if slowest_hop and slowest_latency > SLOW_HOP_THRESHOLD:

        print("\n⚠️ Possible network bottleneck detected:")
        print(slowest_hop)
        print(f"Latency: {slowest_latency} ms\n")


def main():
    
    init_log()

    if "--watch" in sys.argv:
        watch_mode()
        return

    print(f"SendgikoskiLabs NetCheck v{VERSION}\n")

    print("==============================")
    print(" SendgikoskiLabs NetCheck ")
    print("==============================\n")

    start = time.time()

    for host in HOSTS:

        print(f"Target Host : {host}")

        ip = dns_test(host)
        latency = ping_test(host)
        http_status = http_test(f"https://{host}")

        print(f"Resolved IP : {ip}")

        if latency:
            print(f"Ping Latency: {latency} ms  [OK]")
        else:
            print("Ping Latency: FAILED")

        if http_status == 200:
            print(f"HTTP Status : {http_status}  [OK]")
        else:
            print(f"HTTP Status : {http_status}  [ERROR]")

        print("----------------------------------")

    elapsed = round(time.time() - start, 2)

    print("\nDiagnostics completed in", elapsed, "seconds")
    print("\n==============================\n")


if __name__ == "__main__":
    main()
