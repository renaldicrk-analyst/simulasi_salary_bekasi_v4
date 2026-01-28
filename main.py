import streamlit as st
import datetime as dt
import pandas as pd

from queries import SIMULATION_QUERY
from db import fetch_dataframe

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Simulasi Penggajian – Bonus Achievement Outlet",
    layout="wide"
)

st.title("Simulasi Penggajian")
st.caption("Skema: Bonus Bulanan Berbasis Achievement Target Outlet")

branch = "Jakarta"

# ======================================================
# PERIODE
# ======================================================
days = st.sidebar.slider("Jumlah Hari Kerja", 1, 31, 26)

start_date = dt.date(2025, 11, 1)
end_date = start_date + dt.timedelta(days=days - 1)

# ======================================================
# GAJI
# ======================================================
st.sidebar.header("Gaji")

gapok = st.sidebar.number_input(
    "Gapok / Hari",
    value=115_000,
    step=5_000
)

gaji_perbantuan = st.sidebar.number_input(
    "Gaji Crew Perbantuan / Hari",
    value=100_000,
    step=5_000
)

# ======================================================
# BONUS ACHIEVEMENT
# ======================================================
st.sidebar.header("Bonus Bulanan (Achievement)")

tier_1_ach = st.sidebar.number_input(
    "Tier 1 Achievement (%)",
    value=80,
    step=5
) / 100

tier_1_pct = st.sidebar.number_input(
    "Bonus % Sales – Tier 1",
    value=0.03,
    step=0.005
)

tier_2_ach = st.sidebar.number_input(
    "Tier 2 Achievement (%)",
    value=100,
    step=5
) / 100

tier_2_pct = st.sidebar.number_input(
    "Bonus % Sales – Tier 2",
    value=0.05,
    step=0.005
)

tier_3_ach = st.sidebar.number_input(
    "Tier 3 Achievement (%)",
    value=120,
    step=5
) / 100

tier_3_pct = st.sidebar.number_input(
    "Bonus % Sales – Tier 3",
    value=0.08,
    step=0.005
)

# ======================================================
# CREW PERBANTUAN
# ======================================================
st.sidebar.header("Crew Perbantuan")

use_perbantuan = st.sidebar.checkbox(
    "Gunakan Crew Perbantuan",
    value=True
)

crew_1_threshold = st.sidebar.number_input(
    "Sales ≥ +1 Crew",
    value=1_700_000
)
crew_2_threshold = st.sidebar.number_input(
    "Sales ≥ +2 Crew",
    value=2_700_000
)
crew_3_threshold = st.sidebar.number_input(
    "Sales ≥ +3 Crew",
    value=3_700_000
)

# ======================================================
# INFO
# ======================================================
st.info(
    f"""
**Skema Bonus Bulanan – Achievement Target Outlet**

- Gapok dibayar **harian**
- Bonus dihitung dari **total sales bulanan outlet**
- Target outlet diambil dari **master_target**
- Bonus dibagi rata ke **hari aktif outlet**

**Tier Bonus:**
- ≥ {tier_1_ach:.0%} → {tier_1_pct:.1%} × Sales Bulanan
- ≥ {tier_2_ach:.0%} → {tier_2_pct:.1%} × Sales Bulanan
- ≥ {tier_3_ach:.0%} → {tier_3_pct:.1%} × Sales Bulanan
"""
)

# ======================================================
# PARAMS SQL
# ======================================================
params = {
    "branch": branch,
    "start_date": start_date,
    "end_date": end_date,

    "gapok": gapok,
    "gaji_perbantuan": gaji_perbantuan,

    "tier_1_ach": tier_1_ach,
    "tier_2_ach": tier_2_ach,
    "tier_3_ach": tier_3_ach,

    "tier_1_pct": tier_1_pct,
    "tier_2_pct": tier_2_pct,
    "tier_3_pct": tier_3_pct,

    "use_perbantuan": 1 if use_perbantuan else 0,
    "crew_1_threshold": crew_1_threshold,
    "crew_2_threshold": crew_2_threshold,
    "crew_3_threshold": crew_3_threshold,
}

# ======================================================
# LOAD DATA
# ======================================================
df = fetch_dataframe(SIMULATION_QUERY, params)

if df.empty:
    st.warning("Data kosong")
    st.stop()

# ======================================================
# RINGKASAN BULANAN PER OUTLET
# ======================================================
st.subheader("Ringkasan Bulanan per Outlet")

bonus_df = (
    df.groupby("outlet")
    .agg(
        sales_bulanan=("sales", "sum"),
        target=("target_bulanan", "max"),
        bonus=("bonus_crew_utama", "sum"),
    )
    .reset_index()
)

bonus_df["achievement"] = bonus_df["sales_bulanan"] / bonus_df["target"]

def classify_tier(x):
    if x >= tier_3_ach:
        return "Tier 3"
    elif x >= tier_2_ach:
        return "Tier 2"
    elif x >= tier_1_ach:
        return "Tier 1"
    else:
        return "Tidak Achieve"

bonus_df["tier"] = bonus_df["achievement"].apply(classify_tier)

st.dataframe(bonus_df, use_container_width=True)

# ======================================================
# DISTRIBUSI TIER OUTLET
# ======================================================
st.subheader("Distribusi Achievement Outlet")

tier_dist = (
    bonus_df["tier"]
    .value_counts()
    .rename_axis("Tier")
    .reset_index(name="Jumlah Outlet")
)

tier_dist["Persentase"] = (
    tier_dist["Jumlah Outlet"] / tier_dist["Jumlah Outlet"].sum()
).round(2)

st.dataframe(tier_dist, use_container_width=True)

# ======================================================
# RINGKASAN FINANSIAL
# ======================================================
st.subheader("Summary")

total_sales = df["sales"].sum()
total_salary = df["total_salary"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Total Sales", f"Rp {total_sales:,.0f}")
c2.metric("Total Salary", f"Rp {total_salary:,.0f}")
c3.metric("Salary Cost", f"{total_salary / total_sales:.2%}")

# ======================================================
# DETAIL HARIAN
# ======================================================
st.subheader("Detail Harian")

st.dataframe(
    df[
        [
            "tanggal",
            "outlet",
            "sales",
            "sales_bulanan",
            "target_bulanan",
            "achievement",
            "gapok",
            "bonus_crew_utama",
            "crew_perbantuan",
            "total_gaji_perbantuan",
            "total_salary",
        ]
    ],
    use_container_width=True,
)