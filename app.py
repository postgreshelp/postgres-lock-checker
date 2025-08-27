import streamlit as st

# Title
st.title("PostgreSQL Lock Conflict Checker")
st.write(
    "Select an operation in Session 1 and Session 2 to see if Session 2 has to wait."
)

# Lock rules (from your diagram/blog)
lock_rules = {
    1: [7],
    2: [6, 7],
    3: [5, 6, 7],
    4: [4, 5, 6, 7],
    5: [3, 4, 6, 7],
    6: [2, 3, 4, 5, 6, 7],
    7: [1, 2, 3, 4, 5, 6, 7],
}

# Operation names for dropdown
op_names = {
    1: "1. SELECT",
    2: "2. SELECT FOR UPDATE / SELECT FOR SHARE",
    3: "3. UPDATE, DELETE, INSERT",
    4: "4. VACUUM (without FULL), ANALYZE, CREATE INDEX CONCURRENTLY, ALTER TABLE VALIDATE",
    5: "5. CREATE INDEX (without CONCURRENTLY)",
    6: "6. REFRESH MATERIALIZED VIEW CONCURRENTLY",
    7: "7. DROP/TRUNCATE/REINDEX/CLUSTER/VACUUM FULL/REFRESH MV (no CONCURRENTLY)/ALTER TABLE ADD or DROP COLUMN",
}


# Function to check conflict
def check_conflict(op1, op2):
    if op2 in lock_rules.get(op1, []):
        return f"❌ Conflict: Session 2 (op{op2}) must wait for Session 1 (op{op1})."
    else:
        return f"✅ No conflict: Session 2 (op{op2}) can run in parallel with Session 1 (op{op1})."


# UI
col1, col2 = st.columns(2)

with col1:
    session1 = st.selectbox("Select operation for Session 1", options=list(op_names.keys()), format_func=lambda x: op_names[x])

with col2:
    session2 = st.selectbox("Select operation for Session 2", options=list(op_names.keys()), format_func=lambda x: op_names[x])

# Show result
if st.button("Check Conflict"):
    result = check_conflict(session1, session2)
    st.subheader("Result")
    st.success(result if "✅" in result else result)

# Optional: show full matrix
st.write("---")
st.write("### Lock Conflict Matrix")
st.write("This table shows which operations must wait on others:")

import pandas as pd

# Build matrix DataFrame
matrix = []
for i in range(1, 8):
    row = []
    for j in range(1, 8):
        if j in lock_rules[i]:
            row.append("⏳ Wait")
        else:
            row.append("✔️ No wait")
    matrix.append(row)

df = pd.DataFrame(matrix, index=[op_names[i] for i in range(1, 8)], columns=[op_names[j] for j in range(1, 8)])
st.dataframe(df, use_container_width=True)
