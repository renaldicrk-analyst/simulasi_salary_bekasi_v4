# queries.py

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
-- AGGREGATE BULANAN PER OUTLET
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
-- TARGET BULANAN PER OUTLET (CUSTOM 5)
-- ======================================================
target_bulanan AS (
    SELECT
        outlet_tag_clean AS outlet,
        target
    FROM master_target
    WHERE tanggal_penjualan = '2025-11-01'
),

-- ======================================================
-- LOGIKA GAJI & BONUS
-- ======================================================
salary_logic AS (
    SELECT
        b.tanggal,
        b.outlet,
        b.sales,
        m.sales_bulanan,
        m.hari_aktif,
        t.target AS target_bulanan,

        %(gapok)s AS gapok,

        -- ----------------------------------------------
        -- KETERANGAN BONUS
        -- ----------------------------------------------
        CASE
            WHEN %(use_flat_bonus)s = 1
                 AND b.sales >= %(bonus_trigger)s
                THEN 'BONUS FLAT (HARIAN)'

            WHEN %(use_tier_bonus)s = 1
                 AND b.sales >= %(tier_1_sales)s
                THEN 'BONUS JENJANG (HARIAN)'

            WHEN %(use_monthly_fixed)s = 1
                 AND m.sales_bulanan >= %(monthly_sales_trigger)s
                THEN 'BONUS FIXED (BULANAN)'

            WHEN %(use_monthly_tier)s = 1
                 AND m.sales_bulanan >= %(monthly_tier_1_sales)s
                THEN 'BONUS JENJANG (BULANAN)'

            WHEN %(use_custom_5)s = 1
                 AND m.sales_bulanan >= t.target
                THEN 'BONUS TARGET BULANAN (OUTLET)'

            ELSE 'TIDAK DAPAT BONUS'
        END AS keterangan_bonus,

        -- ----------------------------------------------
        -- BONUS CREW UTAMA
        -- ----------------------------------------------
        CASE
            -- CUSTOM 1 – FLAT HARIAN
            WHEN %(use_flat_bonus)s = 1
                 AND b.sales >= %(bonus_trigger)s
                THEN %(flat_bonus)s

            -- CUSTOM 2 – JENJANG HARIAN
            WHEN %(use_tier_bonus)s = 1
                 AND b.sales >= %(tier_3_sales)s
                THEN b.sales * %(tier_3_pct)s

            WHEN %(use_tier_bonus)s = 1
                 AND b.sales >= %(tier_2_sales)s
                THEN b.sales * %(tier_2_pct)s

            WHEN %(use_tier_bonus)s = 1
                 AND b.sales >= %(tier_1_sales)s
                THEN b.sales * %(tier_1_pct)s

            -- CUSTOM 3 – FIXED BULANAN (DIALOKASI HARIAN)
            WHEN %(use_monthly_fixed)s = 1
                 AND m.sales_bulanan >= %(monthly_sales_trigger)s
                THEN %(monthly_fixed_bonus)s / m.hari_aktif

            -- CUSTOM 4 – JENJANG BULANAN (DIALOKASI HARIAN)
            WHEN %(use_monthly_tier)s = 1
                 AND m.sales_bulanan >= %(monthly_tier_3_sales)s
                THEN (m.sales_bulanan * %(monthly_tier_3_pct)s) / m.hari_aktif

            WHEN %(use_monthly_tier)s = 1
                 AND m.sales_bulanan >= %(monthly_tier_2_sales)s
                THEN (m.sales_bulanan * %(monthly_tier_2_pct)s) / m.hari_aktif

            WHEN %(use_monthly_tier)s = 1
                 AND m.sales_bulanan >= %(monthly_tier_1_sales)s
                THEN (m.sales_bulanan * %(monthly_tier_1_pct)s) / m.hari_aktif

            -- CUSTOM 5 – TARGET BULANAN OUTLET (DIALOKASI HARIAN)
            WHEN %(use_custom_5)s = 1
                 AND m.sales_bulanan >= t.target
                THEN %(custom_5_bonus)s / m.hari_aktif

            ELSE 0
        END AS bonus_crew_utama

    FROM base b
    LEFT JOIN monthly_sales m
        ON b.outlet = m.outlet
    LEFT JOIN target_bulanan t
        ON b.outlet = t.outlet
),

-- ======================================================
-- LOGIKA CREW PERBANTUAN
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

-- ======================================================
-- FINAL OUTPUT
-- ======================================================
SELECT
    tanggal,
    outlet,
    sales,
    sales_bulanan,
    target_bulanan,

    keterangan_bonus,
    gapok,
    gaji_perbantuan,
    bonus_crew_utama,

    gapok + bonus_crew_utama AS gaji_crew_utama,

    crew_perbantuan,
    crew_perbantuan * gaji_perbantuan AS total_gaji_perbantuan,

    (gapok + bonus_crew_utama)
    + (crew_perbantuan * gaji_perbantuan) AS total_salary

FROM crew_logic
ORDER BY tanggal, outlet;
"""
