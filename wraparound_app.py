import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Transaction ID Wraparound Visualizer", layout="wide")

st.title("🔄 PostgreSQL Transaction ID Wraparound Visualizer")

st.markdown("""
This tool helps you understand **Transaction ID (XID) wraparound** in PostgreSQL.
Every transaction consumes an XID, and since XIDs are 32-bit (~4 billion), they eventually wrap around.
To prevent data loss, PostgreSQL uses **autovacuum freeze** to mark old tuples as frozen.
""")

# Parameters
max_xid = 2**32  # 4 billion
autovacuum_freeze_max_age = st.slider("Autovacuum Freeze Max Age", min_value=100_000, max_value=1_000_000_000, value=200_000_000, step=100_000)
xid_age_warning = st.slider("XID Age Warning Threshold", min_value=10_000, max_value=1_000_000_000, value=150_000_000, step=100_000)

# Simulation range
transactions = st.slider("Number of Transactions to Simulate", 1_000, 1_000_000_000, 10_000_000, step=1_000_000)

# Generate fake XIDs
xids = np.arange(transactions)
ages = (xids % max_xid)

# Freeze logic
frozen = ages > autovacuum_freeze_max_age

# Create DataFrame
df = pd.DataFrame({
    "XID": xids,
    "Age": ages,
    "Frozen": frozen
})

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["XID"], df["Age"], label="Transaction Age", color="blue")
ax.axhline(autovacuum_freeze_max_age, color="red", linestyle="--", label="Autovacuum Freeze Max Age")
ax.axhline(xid_age_warning, color="orange", linestyle="--", label="Warning Threshold")
ax.set_xlabel("Transaction ID progression")
ax.set_ylabel("Age")
ax.set_title("Transaction ID Wraparound Simulation")
ax.legend()
st.pyplot(fig)

st.markdown("""
### How to Read:
- **Blue line** = Transaction ages.
- **Orange line** = Warning threshold (monitoring alert zone).
- **Red line** = Autovacuum freeze point (tuples older than this are frozen).
- When XIDs reach **2^31**, PostgreSQL must prevent wraparound failure.
""")

st.info("✅ Try adjusting the sliders above to see how different autovacuum thresholds affect wraparound risk.")
