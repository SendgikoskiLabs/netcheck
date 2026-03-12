import subprocess
import socket
import requests


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

    host = "google.com"

    print("\nSendgikoskiLabs Network Check\n")

    latency = ping_test(host)
    ip = dns_test(host)
    http_status = http_test("https://google.com")

    print(f"Host: {host}")
    print(f"DNS: {ip}")
    print(f"Ping latency: {latency} ms")
    print(f"HTTP status: {http_status}")


if __name__ == "__main__":
    main()
