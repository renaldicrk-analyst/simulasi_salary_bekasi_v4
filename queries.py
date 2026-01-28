SIMULATION_QUERY = """
WITH base AS (
    SELECT
        tanggal,
        outlet,
        branch,
        sales
    FROM mv_manpower_cost_v2
    WHERE branch = %(branch)s
      AND tanggal BETWEEN %(start_date)s AND %(end_date)s
),

-- ======================================================
-- SALES BULANAN
-- ======================================================
monthly_sales AS (
    SELECT
        outlet,
        SUM(sales) AS sales_bulanan,
        COUNT(DISTINCT tanggal) AS hari_aktif
    FROM base
    GROUP BY outlet
),

-- ======================================================
-- TARGET BULANAN
-- ======================================================
target_bulanan AS (
    SELECT
        outlet_tag_clean AS outlet,
        target
    FROM master_target
    WHERE tanggal_penjualan = '2025-11-01'
),

-- ======================================================
-- LOGIKA BONUS
-- ======================================================
salary_logic AS (
    SELECT
        b.tanggal,
        b.outlet,
        b.sales,

        m.sales_bulanan,
        m.hari_aktif,
        t.target AS target_bulanan,

        (m.sales_bulanan / NULLIF(t.target, 0)) AS achievement,

        %(gapok)s AS gapok,

        CASE
            WHEN (m.sales_bulanan / t.target) >= %(tier_3_ach)s
                THEN (m.sales_bulanan * %(tier_3_pct)s) / m.hari_aktif

            WHEN (m.sales_bulanan / t.target) >= %(tier_2_ach)s
                THEN (m.sales_bulanan * %(tier_2_pct)s) / m.hari_aktif

            WHEN (m.sales_bulanan / t.target) >= %(tier_1_ach)s
                THEN (m.sales_bulanan * %(tier_1_pct)s) / m.hari_aktif

            ELSE 0
        END AS bonus_crew_utama

    FROM base b
    LEFT JOIN monthly_sales m
        ON b.outlet = m.outlet
    LEFT JOIN target_bulanan t
        ON b.outlet = t.outlet
),

-- ======================================================
-- CREW PERBANTUAN
-- ======================================================
crew_logic AS (
    SELECT
        *,
        CASE
            WHEN %(use_perbantuan)s = 0 THEN 0
            WHEN sales >= %(crew_3_threshold)s THEN 3
            WHEN sales >= %(crew_2_threshold)s THEN 2
            WHEN sales >= %(crew_1_threshold)s THEN 1
            ELSE 0
        END AS crew_perbantuan,

        %(gaji_perbantuan)s AS gaji_perbantuan
    FROM salary_logic
)

SELECT
    tanggal,
    outlet,
    sales,
    sales_bulanan,
    target_bulanan,
    achievement,

    gapok,
    bonus_crew_utama,

    crew_perbantuan,
    crew_perbantuan * gaji_perbantuan AS total_gaji_perbantuan,

    gapok
    + bonus_crew_utama
    + (crew_perbantuan * gaji_perbantuan) AS total_salary

FROM crew_logic
ORDER BY tanggal, outlet;
"""