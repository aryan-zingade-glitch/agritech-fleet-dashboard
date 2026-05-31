import pandas as pd
import sqlite3

def load_and_clean():
    df = pd.read_csv("data/fleet_data.csv")

    print("=== BEFORE CLEANING ===")
    print(f"Shape: {df.shape}")
    print(f"Null values:\n{df.isnull().sum()}")
    print(f"Data types:\n{df.dtypes}")

    df["date"] = pd.to_datetime(df["date"])
    df["machine_id"] = df["machine_id"].str.strip().str.upper()
    df["location"] = df["location"].str.strip().str.title()
    df["fault_code"] = df["fault_code"].str.strip()

    df = df[df["operating_hours"] > 0]
    df = df[df["fuel_consumed_liters"] > 0]
    df = df[df["engine_hours_total"] > 0]

    df["fuel_efficiency"] = (
        df["fuel_consumed_liters"] / df["operating_hours"]
    ).round(2)

    df["idle_percentage"] = (
        (df["idle_time_minutes"] / (df["operating_hours"] * 60)) * 100
    ).round(2)

    df["has_fault"] = df["fault_code"] != "NONE"

    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.day_name()

    print("\n=== AFTER CLEANING ===")
    print(f"Shape: {df.shape}")
    print(f"New columns added: fuel_efficiency, idle_percentage, has_fault")
    print(f"\nSample:\n{df[['machine_id','date','fuel_efficiency','idle_percentage','has_fault']].head()}")

    df.to_csv("data/fleet_data_clean.csv", index=False)

    conn = sqlite3.connect("data/fleet.db")
    df.to_sql("fleet_clean", conn, if_exists="replace", index=False)
    conn.close()

    print("\nCleaned data saved to data/fleet_data_clean.csv and fleet.db")
    return df

if __name__ == "__main__":
    df = load_and_clean()