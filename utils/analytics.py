import pandas as pd
import numpy as np
from utils.sql_queries import fleet_summary, daily_fleet_trend, maintenance_alerts, anomaly_machines

def get_kpis(df=None):
    summary = fleet_summary()

    total_machines = summary["machine_id"].nunique()
    total_fuel = summary["total_fuel"].sum()
    avg_utilisation = summary["avg_daily_hours"].mean() / 12 * 100
    avg_fuel_efficiency = summary["avg_fuel_efficiency"].mean()
    avg_idle = summary["avg_idle_pct"].mean()
    total_fault_days = summary["fault_days"].sum()

    return {
        "total_machines": int(total_machines),
        "total_fuel_liters": round(total_fuel, 2),
        "fleet_utilisation_pct": round(avg_utilisation, 1),
        "avg_fuel_efficiency": round(avg_fuel_efficiency, 2),
        "avg_idle_pct": round(avg_idle, 1),
        "total_fault_days": int(total_fault_days)
    }

def get_maintenance_summary():
    alerts = maintenance_alerts()
    critical = alerts[alerts["status"] == "CRITICAL"]
    warning = alerts[alerts["status"] == "WARNING"]
    ok = alerts[alerts["status"] == "OK"]

    return {
        "critical_count": len(critical),
        "warning_count": len(warning),
        "ok_count": len(ok),
        "critical_machines": critical,
        "warning_machines": warning
    }

def get_anomaly_summary():
    anomalies = anomaly_machines()
    flagged = anomalies[anomalies["is_anomaly"] == True]
    return {
        "total_anomalies": len(flagged),
        "anomaly_machines": flagged
    }

def get_location_breakdown():
    summary = fleet_summary()
    location_df = summary.groupby("location").agg(
        machines=("machine_id", "count"),
        total_fuel=("total_fuel", "sum"),
        avg_efficiency=("avg_fuel_efficiency", "mean"),
        avg_idle=("avg_idle_pct", "mean"),
        total_faults=("fault_days", "sum")
    ).reset_index()
    location_df = location_df.round(2)
    return location_df

if __name__ == "__main__":
    print("=== KPIs ===")
    kpis = get_kpis()
    for k, v in kpis.items():
        print(f"{k}: {v}")

    print("\n=== MAINTENANCE SUMMARY ===")
    maint = get_maintenance_summary()
    print(f"Critical: {maint['critical_count']} machines")
    print(f"Warning: {maint['warning_count']} machines")
    print(f"OK: {maint['ok_count']} machines")

    print("\n=== ANOMALY SUMMARY ===")
    anom = get_anomaly_summary()
    print(f"Flagged anomalies: {anom['total_anomalies']} machines")
    print(anom["anomaly_machines"][["machine_id","location","avg_fuel_eff","fuel_zscore","idle_zscore"]])

    print("\n=== LOCATION BREAKDOWN ===")
    print(get_location_breakdown())