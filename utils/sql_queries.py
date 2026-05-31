import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("data/fleet.db")

def fleet_summary():
    conn = get_connection()
    query = """
        SELECT 
            machine_id,
            location,
            COUNT(*) as total_days,
            ROUND(AVG(operating_hours), 2) as avg_daily_hours,
            ROUND(SUM(fuel_consumed_liters), 2) as total_fuel,
            ROUND(AVG(fuel_efficiency), 2) as avg_fuel_efficiency,
            ROUND(AVG(idle_percentage), 2) as avg_idle_pct,
            MAX(engine_hours_total) as max_engine_hours,
            SUM(CASE WHEN has_fault = 1 THEN 1 ELSE 0 END) as fault_days
        FROM fleet_clean
        GROUP BY machine_id, location
        ORDER BY total_fuel DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def daily_fleet_trend():
    conn = get_connection()
    query = """
        SELECT
            date,
            COUNT(DISTINCT machine_id) as active_machines,
            ROUND(AVG(operating_hours), 2) as avg_hours,
            ROUND(SUM(fuel_consumed_liters), 2) as total_fuel,
            ROUND(AVG(idle_percentage), 2) as avg_idle_pct
        FROM fleet_clean
        GROUP BY date
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def maintenance_alerts():
    conn = get_connection()
    query = """
        SELECT
            machine_id,
            location,
            MAX(engine_hours_total) as current_engine_hours,
            CASE
                WHEN MAX(engine_hours_total) >= 1800 THEN 'CRITICAL'
                WHEN MAX(engine_hours_total) >= 1500 THEN 'WARNING'
                ELSE 'OK'
            END as status
        FROM fleet_clean
        GROUP BY machine_id, location
        ORDER BY current_engine_hours DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def anomaly_machines():
    conn = get_connection()
    query = """
        SELECT
            machine_id,
            location,
            ROUND(AVG(fuel_efficiency), 2) as avg_fuel_eff,
            ROUND(AVG(idle_percentage), 2) as avg_idle_pct,
            SUM(CASE WHEN has_fault = 1 THEN 1 ELSE 0 END) as total_faults
        FROM fleet_clean
        GROUP BY machine_id, location
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["fuel_zscore"] = (
        (df["avg_fuel_eff"] - df["avg_fuel_eff"].mean()) / df["avg_fuel_eff"].std()
    ).round(2)

    df["idle_zscore"] = (
        (df["avg_idle_pct"] - df["avg_idle_pct"].mean()) / df["avg_idle_pct"].std()
    ).round(2)

    df["is_anomaly"] = (df["fuel_zscore"].abs() > 1.5) | (df["idle_zscore"].abs() > 1.5)

    return df

if __name__ == "__main__":
    print("=== FLEET SUMMARY ===")
    print(fleet_summary().head())

    print("\n=== DAILY TREND ===")
    print(daily_fleet_trend().head())

    print("\n=== MAINTENANCE ALERTS ===")
    print(maintenance_alerts())

    print("\n=== ANOMALY DETECTION ===")
    anomalies = anomaly_machines()
    print(anomalies[anomalies["is_anomaly"] == True])