import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# Helper functions
# -------------------------

def generate_fake_db(name, total_xids, frozen, age):
    return {
        "name": name,
        "total_xids": total_xids,
        "frozen": frozen,
        "age": age,
    }

def visualize_wraparound(db):
    MAX_XID = 2**31  # 2,147,483,648
    FREEZE_LIMIT = 200_000_000  # typical autovacuum_freeze_max_age

    age = db["age"]

    # Risk thresholds
    if age < FREEZE_LIMIT:
        risk = "🟢 Safe"
    elif age < (MAX_XID - 1_000_000_000):
        risk = "🟡 Warning (Vacuum soon)"
    else:
        risk = "🔴 Critical (Close to wraparound!)"

    # Plot
    fig, ax = plt.subplots(figsize=(6, 3))
    x = np.linspace(0, MAX_XID, 500000)
    y = np.zeros_like(x)

    ax.plot(x, y, alpha=0)  # invisible baseline
    ax.axvline(FREEZE_LIMIT, color="orange", linestyle="--", label="Freeze Age Limit")
    ax.axvline(MAX_XID, color="red", linestyle="--", label="Wraparound (2^31)")

    # Age pointer
    ax.axvline(age, color="blue", linewidth=2, label=f"Current Age: {age:,}")

    ax.set_xlim(0, MAX_XID)
    ax.set_yticks([])
    ax.set_xlabel("Transaction ID Age")
    ax.set_title(f"DB: {db['name']} — Risk: {risk}")
    ax.legend()

    st.pyplot(fig)

    st.info(
        f"**Database:** {db['name']}  \n"
        f"**Age:** {age:,}  \n"
        f"**Frozen Tuples:** {db['frozen']:,}  \n"
        f"**Total Tuples:** {db['total_xids']:,}  \n"
        f"**Status:** {risk}"
    )

# -------------------------
# Streamlit UI
# -------------------------

st.title("🌀 PostgreSQL Transaction ID Wraparound Visualizer")
st.write(
    "Simulate how PostgreSQL tracks transaction ID age and visualize the risk of **wraparound**.\n"
    "This demo uses fake datasets. Later, we can connect to a real PostgreSQL database."
)

# Demo datasets
fake_dbs = [
    generate_fake_db("Tiny DB", 1_000_000, 900_000, 10_000),
    generate_fake_db("Busy OLTP", 500_000_000, 400_000_000, 150_000_000),
    generate_fake_db("Neglected Warehouse", 2_000_000_000, 100_000_000, 1_900_000_000),
]

db_names = [db["name"] for db in fake_dbs]
choice = st.selectbox("Choose a database to visualize:", db_names)

# Render visualization
selected_db = next(db for db in fake_dbs if db["name"] == choice)
visualize_wraparound(selected_db)

st.caption("💡 Later we can extend this to run `SELECT age(datfrozenxid) FROM pg_database;` on a live PostgreSQL instance.")
