import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.analytics import get_kpis, get_maintenance_summary, get_anomaly_summary, get_location_breakdown
from utils.sql_queries import fleet_summary, daily_fleet_trend, maintenance_alerts

st.set_page_config(
    page_title="Fleet Operations Dashboard",
    page_icon="🚜",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e2e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
    .critical { border-left-color: #f44336; }
    .warning { border-left-color: #ff9800; }
    .ok { border-left-color: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/John_Deere_logo.svg/320px-John_Deere_logo.svg.png", width=160)
st.sidebar.title("Fleet Analytics")
st.sidebar.markdown("---")

summary_df = fleet_summary()
locations = ["All"] + sorted(summary_df["location"].unique().tolist())
selected_location = st.sidebar.selectbox("Filter by Location", locations)

trend_df = daily_fleet_trend()
trend_df["date"] = pd.to_datetime(trend_df["date"])
min_date = trend_df["date"].min().date()
max_date = trend_df["date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

st.sidebar.markdown("---")


# ── Filter data ──────────────────────────────────────────────────────────────
if selected_location != "All":
    filtered_summary = summary_df[summary_df["location"] == selected_location]
else:
    filtered_summary = summary_df

if len(date_range) == 2:
    filtered_trend = trend_df[
        (trend_df["date"].dt.date >= date_range[0]) &
        (trend_df["date"].dt.date <= date_range[1])
    ]
else:
    filtered_trend = trend_df

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🚜 Fleet Operations Dashboard")
st.markdown("Real-time equipment utilisation, fuel analytics, and maintenance intelligence")
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
kpis = get_kpis()
maint = get_maintenance_summary()
anom = get_anomaly_summary()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Machines", kpis["total_machines"])
col2.metric("Fleet Utilisation", f"{kpis['fleet_utilisation_pct']}%")
col3.metric("Avg Fuel Efficiency", f"{kpis['avg_fuel_efficiency']} L/hr")
col4.metric("Avg Idle Time", f"{kpis['avg_idle_pct']}%")
col5.metric("⚠️ Warnings", maint["warning_count"])
col6.metric("🔴 Anomalies", anom["total_anomalies"])

st.markdown("---")

# ── Row 1: Fuel trend + Location breakdown ───────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Daily Fuel Consumption Trend")
    fig_trend = px.line(
        filtered_trend, x="date", y="total_fuel",
        labels={"total_fuel": "Total Fuel (L)", "date": "Date"},
        color_discrete_sequence=["#4CAF50"]
    )
    fig_trend.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", height=300
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.subheader("📍 Fuel by Location")
    loc_df = get_location_breakdown()
    fig_loc = px.bar(
        loc_df, x="location", y="total_fuel",
        color="total_fuel", color_continuous_scale="Greens",
        labels={"total_fuel": "Total Fuel (L)"}
    )
    fig_loc.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", height=300, showlegend=False
    )
    st.plotly_chart(fig_loc, use_container_width=True)

# ── Row 2: Machine efficiency + Idle time ────────────────────────────────────
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("⛽ Fuel Efficiency by Machine")
    fig_eff = px.bar(
        filtered_summary.sort_values("avg_fuel_efficiency", ascending=True),
        x="avg_fuel_efficiency", y="machine_id",
        orientation="h", color="avg_fuel_efficiency",
        color_continuous_scale="RdYlGn",
        labels={"avg_fuel_efficiency": "L/hr", "machine_id": "Machine"}
    )
    fig_eff.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", height=400
    )
    st.plotly_chart(fig_eff, use_container_width=True)

with col_right2:
    st.subheader("💤 Idle Time by Machine")
    fig_idle = px.bar(
        filtered_summary.sort_values("avg_idle_pct", ascending=False),
        x="machine_id", y="avg_idle_pct",
        color="avg_idle_pct", color_continuous_scale="Reds",
        labels={"avg_idle_pct": "Idle %", "machine_id": "Machine"}
    )
    fig_idle.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", height=400
    )
    st.plotly_chart(fig_idle, use_container_width=True)

# ── Row 3: Maintenance alerts ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("🔧 Maintenance Alerts")

alerts_df = maintenance_alerts()
col_c, col_w, col_o = st.columns(3)

with col_c:
    critical_df = alerts_df[alerts_df["status"] == "CRITICAL"]
    st.error(f"🔴 CRITICAL — {len(critical_df)} machines")
    if len(critical_df) > 0:
        st.dataframe(critical_df[["machine_id", "location", "current_engine_hours"]], use_container_width=True)
    else:
        st.success("No critical machines")

with col_w:
    warning_df = alerts_df[alerts_df["status"] == "WARNING"]
    st.warning(f"⚠️ WARNING — {len(warning_df)} machines")
    st.dataframe(warning_df[["machine_id", "location", "current_engine_hours"]], use_container_width=True)

with col_o:
    ok_df = alerts_df[alerts_df["status"] == "OK"]
    st.success(f"✅ OK — {len(ok_df)} machines")
    st.dataframe(ok_df[["machine_id", "location", "current_engine_hours"]], use_container_width=True)

# ── Row 4: Anomaly detection ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("🚨 Anomaly Detection")

from utils.analytics import get_anomaly_summary
from utils.sql_queries import anomaly_machines

anom_df = anomaly_machines()
fig_scatter = px.scatter(
    anom_df, x="avg_fuel_eff", y="avg_idle_pct",
    color="is_anomaly", symbol="is_anomaly",
    hover_data=["machine_id", "location"],
    color_discrete_map={True: "#f44336", False: "#4CAF50"},
    labels={"avg_fuel_eff": "Avg Fuel Efficiency (L/hr)", "avg_idle_pct": "Avg Idle %"},
    title="Fleet Anomaly Map — Red points are flagged machines"
)
fig_scatter.update_layout(
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    font_color="white", height=400
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("Built with Python · Streamlit · Plotly · SQLite | John Deere Fleet Analytics Demo")

