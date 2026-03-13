import subprocess
import socket
import requests

VERSION = "1.1"

HOSTS = [
    "google.com",
    "cloudflare.com",
    "github.com"
]

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

    return None


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


def main():

    import time

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
