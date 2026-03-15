import streamlit as st
import pandas as pd
import time
import re

VERSION = "1.5"

LOG_FILE = "../logs/netcheck_log.csv"
TRACE_FILE = "../logs/traceroute_log.txt"

st.set_page_config(page_title="NetCheck Dashboard", layout="wide")

st.title("SendgikoskiLabs NetCheck Dashboard")

# =========================
# Latency Chart
# =========================

st.header("Live Latency Monitor")

df = pd.read_csv(LOG_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

hosts = df["host"].unique()

for host in hosts:

    host_data = df[df["host"] == host]

    st.subheader(host)

    st.line_chart(
        host_data.set_index("timestamp")["latency"]
    )

# =========================
# Traceroute Path Map
# =========================

st.header("Latest Network Path")

try:

    with open(TRACE_FILE) as f:
        lines = f.readlines()

except:
    st.warning("No traceroute data available yet.")
    st.stop()

# Extract last traceroute
sections = []
current = []

for line in lines:

    if line.startswith("====="):

        if current:
            sections.append(current)
            current = []

    else:
        current.append(line)

if current:
    sections.append(current)

latest_trace = sections[-1]

nodes = []

for line in latest_trace:

    if "* * *" in line:
        nodes.append("⚠️ Filtered hop")
        continue

    match = re.findall(r"(\d+\.\d+)\s*ms", line)

    if match:
        latency = max([float(x) for x in match])
        nodes.append(f"{latency} ms")

if nodes:

    for i, node in enumerate(nodes):

        st.write(f"Hop {i+1}")

        if "⚠️" in node:
            st.error(node)
        elif float(node.split()[0]) > 120:
            st.warning(node)
        else:
            st.success(node)

else:

    st.info("Traceroute contained no responding hops")