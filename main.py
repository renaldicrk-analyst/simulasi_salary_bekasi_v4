import streamlit as st
import datetime as dt
import pandas as pd

from queries import SIMULATION_QUERY
from db import fetch_dataframe


# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Simulasi Penggajian",
    layout="wide"
)

st.title("Simulasi Penggajian")

branch = "Jakarta"


# ======================================================
# SIDEBAR – PILIH SKEMA
# ======================================================
st.sidebar.header("Skema Penggajian")

mode_label = st.sidebar.radio(
    "Pilih Skema",
    [
        "Custom 1 – Bonus Flat Harian",
        "Custom 2 – Bonus Berjenjang Harian",
        "Custom 3 – Bonus Fixed Bulanan",
        "Custom 4 – Bonus Berjenjang Bulanan",
        "Custom 5 – Bonus Target Bulanan Outlet",
    ]
)

mode_key = {
    "Custom 1 – Bonus Flat Harian": "custom_1",
    "Custom 2 – Bonus Berjenjang Harian": "custom_2",
    "Custom 3 – Bonus Fixed Bulanan": "custom_3",
    "Custom 4 – Bonus Berjenjang Bulanan": "custom_4",
    "Custom 5 – Bonus Target Bulanan Outlet": "custom_5",
}[mode_label]

st.sidebar.divider()


# ======================================================
# JUMLAH HARI
# ======================================================
days = st.sidebar.slider("Jumlah Hari Kerja", 1, 31, 26)

start_date = dt.date(2025, 11, 1)
end_date = start_date + dt.timedelta(days=days - 1)


# ======================================================
# GAPOK & PERBANTUAN
# ======================================================
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
# DEFAULT PARAM (ANTI SQL ERROR)
# ======================================================
bonus_trigger = 0
flat_bonus = 0

tier_1_sales = tier_2_sales = tier_3_sales = 0
tier_1_pct = tier_2_pct = tier_3_pct = 0.0

monthly_sales_trigger = 0
monthly_fixed_bonus = 0

monthly_tier_1_sales = monthly_tier_2_sales = monthly_tier_3_sales = 0
monthly_tier_1_pct = monthly_tier_2_pct = monthly_tier_3_pct = 0.0

custom_5_bonus = 0


# ======================================================
# SETTING BONUS
# ======================================================
if mode_key == "custom_1":
    bonus_trigger = st.sidebar.number_input(
        "Target Sales Bonus",
        value=1_000_000
    )
    flat_bonus = st.sidebar.number_input(
        "Bonus / Hari",
        value=60_000
    )

elif mode_key == "custom_2":
    tier_1_sales = st.sidebar.number_input("Tier 1 ≥", value=1_200_000)
    tier_1_pct = st.sidebar.number_input("Bonus % Tier 1", value=0.05, step=0.01)

    tier_2_sales = st.sidebar.number_input("Tier 2 ≥", value=1_700_000)
    tier_2_pct = st.sidebar.number_input("Bonus % Tier 2", value=0.08, step=0.01)

    tier_3_sales = st.sidebar.number_input("Tier 3 ≥", value=2_200_000)
    tier_3_pct = st.sidebar.number_input("Bonus % Tier 3", value=0.10, step=0.01)

elif mode_key == "custom_3":
    monthly_sales_trigger = st.sidebar.number_input(
        "Target Sales Bulanan",
        value=30_000_000
    )
    monthly_fixed_bonus = st.sidebar.number_input(
        "Bonus Bulanan",
        value=1_500_000
    )

elif mode_key == "custom_4":
    monthly_tier_1_sales = st.sidebar.number_input("Tier 1 ≥", value=30_000_000)
    monthly_tier_1_pct = st.sidebar.number_input(
        "Bonus % Tier 1", value=0.05, step=0.005
    )

    monthly_tier_2_sales = st.sidebar.number_input("Tier 2 ≥", value=40_000_000)
    monthly_tier_2_pct = st.sidebar.number_input(
        "Bonus % Tier 2", value=0.08, step=0.005
    )

    monthly_tier_3_sales = st.sidebar.number_input("Tier 3 ≥", value=60_000_000)
    monthly_tier_3_pct = st.sidebar.number_input(
        "Bonus % Tier 3", value=0.10, step=0.005
    )

elif mode_key == "custom_5":

    st.sidebar.markdown("### Tier Achievement")

    achv_1 = st.sidebar.number_input(
        "Tier 1 Achievement ≥ (%)", value=100, step=5
    )
    achv_1_pct = st.sidebar.number_input(
        "Bonus % Tier 1", value=0.02, step=0.005
    )

    achv_2 = st.sidebar.number_input(
        "Tier 2 Achievement ≥ (%)", value=110, step=5
    )
    achv_2_pct = st.sidebar.number_input(
        "Bonus % Tier 2", value=0.03, step=0.005
    )

    achv_3 = st.sidebar.number_input(
        "Tier 3 Achievement ≥ (%)", value=120, step=5
    )
    achv_3_pct = st.sidebar.number_input(
        "Bonus % Tier 3", value=0.04, step=0.005
    )


# ======================================================
# CREW PERBANTUAN
# ======================================================
st.sidebar.divider()

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
# DESKRIPSI SKEMA
# ======================================================
if mode_key == "custom_1":
    st.info(
        f"""
**Skema Custom 1 – Bonus Flat Harian**
- Gapok harian: **Rp {gapok:,.0f}**
- Bonus tetap **Rp {flat_bonus:,.0f} / hari**
- Bonus diberikan jika **sales ≥ Rp {bonus_trigger:,.0f}**

**Rumus:**
> Gaji Harian = Gapok + Bonus Flat  
> Total Gaji = Gaji Harian × Jumlah Hari Kerja

**Crew Perbantuan:** {"Aktif (berdasarkan threshold sales)" if use_perbantuan else "Tidak digunakan"}
"""
    )

elif mode_key == "custom_2":
    st.info(
        f"""
**Skema Custom 2 – Bonus Berjenjang Harian**
- Gapok harian: **Rp {gapok:,.0f}**
- Bonus dihitung dari **persentase sales harian**

**Jenjang Bonus:**
- ≥ Rp {tier_1_sales:,.0f} → **{tier_1_pct:.0%}**
- ≥ Rp {tier_2_sales:,.0f} → **{tier_2_pct:.0%}**
- ≥ Rp {tier_3_sales:,.0f} → **{tier_3_pct:.0%}**

**Rumus:**
> Gaji Harian = Gapok + (Sales × Persentase Bonus)

**Crew Perbantuan:** {"Aktif (berdasarkan threshold sales)" if use_perbantuan else "Tidak digunakan"}
"""
    )

elif mode_key == "custom_3":
    st.info(
        f"""
**Skema Custom 3 – Bonus Fixed Bulanan**
- Gapok dibayar **harian**
- Bonus **bulanan tetap** jika outlet mencapai target
- Bonus **tidak masuk gaji harian**

**Target Bulanan:**
≥ Rp {monthly_sales_trigger:,.0f} → Bonus **Rp {monthly_fixed_bonus:,.0f}**

**Crew Perbantuan:** {"Aktif (berdasarkan threshold sales harian)" if use_perbantuan else "Tidak digunakan"}
"""
    )

elif mode_key == "custom_4":
    st.info(
        f"""
**Skema Custom 4 – Bonus Berjenjang Bulanan**
- Gapok dibayar **harian**
- Bonus dihitung dari **total sales bulanan**
- Bonus **tidak masuk gaji harian**

**Jenjang Bonus Bulanan:**
- ≥ Rp {monthly_tier_1_sales:,.0f} → **{monthly_tier_1_pct:.0%}**
- ≥ Rp {monthly_tier_2_sales:,.0f} → **{monthly_tier_2_pct:.0%}**
- ≥ Rp {monthly_tier_3_sales:,.0f} → **{monthly_tier_3_pct:.0%}**

**Crew Perbantuan:** {"Aktif (berdasarkan threshold sales harian)" if use_perbantuan else "Tidak digunakan"}
"""
    )

else:  # 🔹 CUSTOM 5
    st.info(
    f"""
**Skema Custom 5 – Bonus Achievement Bulanan Outlet**
- Gapok dibayar **harian**
- Bonus dihitung dari **achievement terhadap target outlet**
- Bonus dibayarkan **bulanan (tidak dialokasikan harian)**

**Tier Bonus:**
- ≥ {achv_1}% → **{achv_1_pct:.1%} × Sales Bulanan**
- ≥ {achv_2}% → **{achv_2_pct:.1%} × Sales Bulanan**
- ≥ {achv_3}% → **{achv_3_pct:.1%} × Sales Bulanan**

**Crew Perbantuan:** {"Aktif" if use_perbantuan else "Tidak digunakan"}
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

    "use_flat_bonus": 1 if mode_key == "custom_1" else 0,
    "use_tier_bonus": 1 if mode_key == "custom_2" else 0,
    "use_monthly_fixed": 1 if mode_key == "custom_3" else 0,
    "use_monthly_tier": 1 if mode_key == "custom_4" else 0,
    "use_custom_5": 1 if mode_key == "custom_5" else 0,

    "bonus_trigger": bonus_trigger,
    "flat_bonus": flat_bonus,

    "tier_1_sales": tier_1_sales,
    "tier_2_sales": tier_2_sales,
    "tier_3_sales": tier_3_sales,
    "tier_1_pct": tier_1_pct,
    "tier_2_pct": tier_2_pct,
    "tier_3_pct": tier_3_pct,

    "monthly_sales_trigger": monthly_sales_trigger,
    "monthly_fixed_bonus": monthly_fixed_bonus,

    "monthly_tier_1_sales": monthly_tier_1_sales,
    "monthly_tier_2_sales": monthly_tier_2_sales,
    "monthly_tier_3_sales": monthly_tier_3_sales,
    "monthly_tier_1_pct": monthly_tier_1_pct,
    "monthly_tier_2_pct": monthly_tier_2_pct,
    "monthly_tier_3_pct": monthly_tier_3_pct,

    "custom_5_bonus": custom_5_bonus,
    "achv_1": achv_1,
    "achv_2": achv_2,
    "achv_3": achv_3,

    "achv_1_pct": achv_1_pct,
    "achv_2_pct": achv_2_pct,
    "achv_3_pct": achv_3_pct,

    "use_perbantuan": 1 if use_perbantuan else 0,
    "crew_1_threshold": crew_1_threshold,
    "crew_2_threshold": crew_2_threshold,
    "crew_3_threshold": crew_3_threshold,
}


# LOAD DATA
df = fetch_dataframe(SIMULATION_QUERY, params)

if df.empty:
    st.warning("Data kosong")
    st.stop()

# ================= CUSTOM 1 & 2 ========================
if mode_key in ["custom_1", "custom_2"]:

    st.subheader("Range Total Salary")
    min_salary = gapok * days
    max_salary = (gapok + df["bonus_crew_utama"].max()) * days

    c1, c2 = st.columns(2)
    c1.metric("Minimum", f"Rp {min_salary:,.0f}")
    c2.metric("Maksimum", f"Rp {max_salary:,.0f}")

    st.subheader("Distribusi Bonus")
    dist = df["keterangan_bonus"].value_counts().reset_index()
    dist.columns = ["Status Bonus", "Jumlah Hari"]
    dist["Persentase"] = (
        dist["Jumlah Hari"] / dist["Jumlah Hari"].sum()
    ).round(2)

    st.dataframe(dist, use_container_width=True)

    st.subheader("Ringkasan Total")
    total_sales = df["sales"].sum()
    total_salary = df["total_salary"].sum()
    total_bonus = df["bonus_crew_utama"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales", f"Rp {total_sales:,.0f}")
    c2.metric("Total Salary", f"Rp {total_salary:,.0f}")
    c3.metric("Total Bonus", f"Rp {total_bonus:,.0f}")

    st.metric("Salary Cost", f"{total_salary / total_sales:.2%}")

    st.subheader("Detail Harian")
    st.dataframe(
        df[
            [
                "tanggal",
                "outlet",
                "sales",
                "keterangan_bonus",
                "gapok",
                "total_gaji_perbantuan",
                "bonus_crew_utama",
                "crew_perbantuan",
                "total_salary",
            ]
        ],
        use_container_width=True,
    )

# ================= CUSTOM 3, 4 & 5 ========================
else:

    st.subheader("Ringkasan Bonus Bulanan")
    bonus_df = (
        df.groupby("outlet")
        .agg(
            sales_bulanan=("sales", "sum"),
            bonus=("bonus_crew_utama", "sum"),
        )
        .reset_index()
    )

    achieved = bonus_df[bonus_df["bonus"] > 0]

    total_outlet = df["outlet"].nunique()
    achieved_outlet = achieved["outlet"].nunique()
    achievement_pct = (
        achieved_outlet / total_outlet if total_outlet > 0 else 0
    )

    total_sales = df["sales"].sum()
    total_salary_without_bonus = df["total_salary"].sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Outlet", total_outlet)
    c2.metric("Outlet Achieve Target", achieved_outlet)
    c3.metric("% Achieve Target", f"{achievement_pct:.1%}")
    c4.metric(
        "Total Bonus Bulanan",
        f"Rp {achieved['bonus'].sum():,.0f}",
    )
    c5.metric("Total Sales", f"Rp {total_sales:,.0f}")
    c6.metric(
        "Total Salary (Tanpa Bonus)",
        f"Rp {total_salary_without_bonus:,.0f}",
    )

    total_salary = total_salary_without_bonus + achieved["bonus"].sum()
    st.metric("Salary Cost", f"{total_salary / total_sales:.2%}")

    st.subheader("Detail Harian (Tanpa Bonus)")
    df["total_salary_harian"] = (
        df["gapok"] + df["total_gaji_perbantuan"]
    )

    st.dataframe(
        df[
            [
                "tanggal",
                "outlet",
                "sales",
                "gapok",
                "crew_perbantuan",
                "total_gaji_perbantuan",
                "total_salary_harian",
            ]
        ],
        use_container_width=True,
    )
