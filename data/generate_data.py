import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

MACHINES = [f"JD-{i:03d}" for i in range(1, 21)]
LOCATIONS = ["Pune", "Nashik", "Aurangabad", "Kolhapur", "Nagpur"]
START_DATE = datetime(2024, 1, 1)
DAYS = 180

records = []

for machine in MACHINES:
    base_fuel = np.random.uniform(8, 15)
    base_idle = np.random.uniform(10, 40)
    engine_hours = np.random.uniform(50, 200)
    location = random.choice(LOCATIONS)

    for day in range(DAYS):
        date = START_DATE + timedelta(days=day)
        operating_hours = np.random.uniform(4, 12)
        fuel_consumed = base_fuel * operating_hours * np.random.uniform(0.85, 1.15)
        idle_minutes = base_idle * np.random.uniform(0.5, 1.5)
        speed_avg = np.random.uniform(5, 25)
        engine_hours += operating_hours
        fault_code = random.choices(
            [None, "E001", "E002", "E003"],
            weights=[0.92, 0.04, 0.02, 0.02]
        )[0]

        records.append({
            "machine_id": machine,
            "date": date.strftime("%Y-%m-%d"),
            "location": location,
            "operating_hours": round(operating_hours, 2),
            "fuel_consumed_liters": round(fuel_consumed, 2),
            "idle_time_minutes": round(idle_minutes, 2),
            "avg_speed_kmh": round(speed_avg, 2),
            "engine_hours_total": round(engine_hours, 2),
            "fault_code": fault_code if fault_code else "NONE"
        })

df = pd.DataFrame(records)

os.makedirs("data", exist_ok=True)
df.to_csv("data/fleet_data.csv", index=False)

conn = sqlite3.connect("data/fleet.db")
df.to_sql("fleet_operations", conn, if_exists="replace", index=False)
conn.close()

print(f"Generated {len(df)} records for {len(MACHINES)} machines")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"CSV saved to data/fleet_data.csv")
print(f"SQLite database saved to data/fleet.db")
print(df.head())