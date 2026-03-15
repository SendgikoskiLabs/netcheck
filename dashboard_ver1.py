import streamlit as st
import pandas as pd
import time

LOG_FILE = "../logs/netcheck_log.csv"

#st.title("SendgikoskiLabs NetCheck Dashboard")

st.sidebar.title("SendgikoskiLabs")
st.sidebar.write("NetCheck Monitoring Dashboard")

refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 5, 60, 10)

# Load data
df = pd.read_csv(LOG_FILE)

# Convert timestamp column
df["timestamp"] = pd.to_datetime(df["timestamp"])

hosts = df["host"].unique()

selected_host = st.selectbox("Select Host", hosts)

host_data = df[df["host"] == selected_host]

st.subheader("Raw Data")
st.dataframe(host_data.tail(20))

st.subheader(f"Latency History for {selected_host}")
st.line_chart(
    host_data.set_index("timestamp")["latency"],
    height=300
)

st.subheader("Latency Statistics")

st.write("Average latency:", round(host_data["latency"].mean(), 2), "ms")
st.write("Minimum latency:", round(host_data["latency"].min(), 2), "ms")
st.write("Maximum latency:", round(host_data["latency"].max(), 2), "ms")

# ---- Auto refresh AFTER rendering ----
time.sleep(refresh_rate)
st.rerun()