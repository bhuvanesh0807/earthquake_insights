import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Earthquake Analysis Dashboard", layout="wide", page_icon="🌍")

# Database connection
conn = st.connection('mysql', type='sql')

# Title
st.title("🌍 Global Earthquake Analysis Dashboard")
st.markdown("### Comprehensive insights from 26+ earthquake features")

# Sidebar for navigation
st.sidebar.title("📊 Analysis Categories")
analysis_category = st.sidebar.radio(
    "Select Analysis:",
    ["Overview", "Magnitude & Depth", "Time Analysis", "Event Type & Quality", 
     "Tsunamis & Alerts", "Seismic Patterns & Trends", "Depth & Location Analysis"]
)

# Helper function to run queries
def run_query(query):
    try:
        return conn.query(query, ttl=600)
    except Exception as e:
        st.error(f"Query Error: {e}")
        return None

# ==================== OVERVIEW ====================
if analysis_category == "Overview":
    st.header("📈 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total earthquakes
    total_eq = run_query("SELECT COUNT(*) as total FROM earthquake_db.earthquakes")
    if total_eq is not None:
        col1.metric("Total Earthquakes", f"{total_eq['total'][0]:,}")
    
    # Average magnitude
    avg_mag = run_query("SELECT ROUND(AVG(mag), 2) as avg_mag FROM earthquake_db.earthquakes")
    if avg_mag is not None:
        col2.metric("Average Magnitude", avg_mag['avg_mag'][0])
    
    # Max magnitude
    max_mag = run_query("SELECT MAX(mag) as max_mag FROM earthquake_db.earthquakes")
    if max_mag is not None:
        col3.metric("Strongest Earthquake", max_mag['max_mag'][0])
    
    # Countries affected
    countries = run_query("SELECT COUNT(DISTINCT country) as cnt FROM earthquake_db.earthquakes")
    if countries is not None:
        col4.metric("Countries Affected", countries['cnt'][0])
    
    st.markdown("---")
    
    # Recent earthquakes
    st.subheader("🕐 Recent Earthquakes (Last 20)")
    recent = run_query("""
        SELECT time, place, mag, depth_km, country, tsunami
        FROM earthquake_db.earthquakes
        ORDER BY time DESC
        LIMIT 20
    """)
    if recent is not None:
        st.dataframe(recent, use_container_width=True)

# ==================== MAGNITUDE & DEPTH ====================
elif analysis_category == "Magnitude & Depth":
    st.header("💪 Magnitude & Depth Analysis")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Top 10 Strongest", "Top 10 Deepest", "Shallow & Strong", 
        "Avg Depth by Country", "Avg Mag by Type"
    ])
    
    with tab1:
        st.subheader("1️⃣ Top 10 Strongest Earthquakes")
        query = """
            SELECT time, place, mag, depth_km, country, tsunami
            FROM earthquake_db.earthquakes
            ORDER BY mag DESC
            LIMIT 10
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='place', y='mag', color='mag', 
                        title="Top 10 Strongest Earthquakes",
                        labels={'mag': 'Magnitude', 'place': 'Location'})
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("2️⃣ Top 10 Deepest Earthquakes")
        query = """
            SELECT time, place, mag, depth_km, country
            FROM earthquake_db.earthquakes
            ORDER BY depth_km DESC
            LIMIT 10
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='place', y='depth_km', color='depth_km',
                        title="Top 10 Deepest Earthquakes",
                        labels={'depth_km': 'Depth (km)', 'place': 'Location'})
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("3️⃣ Shallow Earthquakes (< 50 km) with Magnitude > 7.5")
        query = """
            SELECT time, place, mag, depth_km, country, tsunami
            FROM earthquake_db.earthquakes
            WHERE depth_km < 50 AND mag > 7.5
            ORDER BY mag DESC
        """
        df = run_query(query)
        if df is not None:
            st.metric("Count", len(df))
            st.dataframe(df, use_container_width=True)
            if len(df) > 0:
                fig = px.scatter(df, x='depth_km', y='mag', size='mag', color='country',
                               hover_data=['place', 'time'],
                               title="Shallow & Strong Earthquakes")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("4️⃣ Average Depth per Country (Top 20)")
        query = """
            SELECT country, 
                   ROUND(AVG(depth_km), 2) as avg_depth,
                   COUNT(*) as count
            FROM earthquake_db.earthquakes
            GROUP BY country
            HAVING count > 10
            ORDER BY avg_depth DESC
            LIMIT 20
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='country', y='avg_depth', color='avg_depth',
                        title="Average Depth by Country",
                        labels={'avg_depth': 'Avg Depth (km)', 'country': 'Country'})
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("5️⃣ Average Magnitude by Magnitude Type")
        query = """
            SELECT magType, 
                   ROUND(AVG(mag), 2) as avg_mag,
                   COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE magType IS NOT NULL AND magType != ''
            GROUP BY magType
            ORDER BY avg_mag DESC
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='magType', y='avg_mag', color='avg_mag',
                        title="Average Magnitude by Type",
                        labels={'avg_mag': 'Avg Magnitude', 'magType': 'Magnitude Type'})
            st.plotly_chart(fig, use_container_width=True)

# ==================== TIME ANALYSIS ====================
elif analysis_category == "Time Analysis":
    st.header("⏰ Time-Based Analysis")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "By Year", "By Month", "By Day of Week", "By Hour", "Network Activity"
    ])
    
    with tab1:
        st.subheader("6️⃣ Earthquakes per Year")
        query = """
            SELECT year, COUNT(*) as count
            FROM earthquake_db.earthquakes
            GROUP BY year
            ORDER BY year
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.line(df, x='year', y='count', markers=True,
                         title="Earthquake Frequency by Year")
            st.plotly_chart(fig, use_container_width=True)
            max_year = df.loc[df['count'].idxmax()]
            st.success(f"🏆 Most Active Year: {int(max_year['year'])} with {max_year['count']:,} earthquakes")
    
    with tab2:
        st.subheader("7️⃣ Earthquakes per Month")
        query = """
            SELECT month, COUNT(*) as count
            FROM earthquake_db.earthquakes
            GROUP BY month
            ORDER BY month
        """
        df = run_query(query)
        if df is not None:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            df['month_name'] = df['month'].apply(lambda x: months[int(x)-1] if 1 <= x <= 12 else str(x))
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='month_name', y='count', color='count',
                        title="Earthquake Frequency by Month")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("8️⃣ Earthquakes by Day of Week")
        query = """
            SELECT day_of_week, COUNT(*) as count
            FROM earthquake_db.earthquakes
            GROUP BY day_of_week
            ORDER BY FIELD(day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='day_of_week', y='count', color='count',
                        title="Earthquake Frequency by Day of Week")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("9️⃣ Earthquakes by Hour of Day")
        query = """
            SELECT HOUR(time) as hour, COUNT(*) as count
            FROM earthquake_db.earthquakes
            GROUP BY hour
            ORDER BY hour
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.line(df, x='hour', y='count', markers=True,
                         title="Earthquake Frequency by Hour of Day")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("🔟 Most Active Reporting Networks")
        query = """
            SELECT net, COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE net IS NOT NULL AND net != ''
            GROUP BY net
            ORDER BY count DESC
            LIMIT 15
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='net', y='count', color='count',
                        title="Top Reporting Networks")
            st.plotly_chart(fig, use_container_width=True)

# ==================== EVENT TYPE & QUALITY ====================
elif analysis_category == "Event Type & Quality":
    st.header("📋 Event Type & Quality Metrics")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Status", "Event Type", "Data Types", "RMS & Gap", "Station Coverage"
    ])
    
    with tab1:
        st.subheader("1️⃣4️⃣ Reviewed vs Automatic Earthquakes")
        query = """
            SELECT status, COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE status IS NOT NULL AND status != ''
            GROUP BY status
            ORDER BY count DESC
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.pie(df, values='count', names='status',
                        title="Earthquake Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("1️⃣5️⃣ Count by Earthquake Type")
        query = """
            SELECT type, COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE type IS NOT NULL AND type != ''
            GROUP BY type
            ORDER BY count DESC
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='type', y='count', color='count',
                        title="Earthquake Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("1️⃣6️⃣ Earthquakes by Data Types Available")
        query = """
            SELECT types, COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE types IS NOT NULL AND types != ''
            GROUP BY types
            ORDER BY count DESC
            LIMIT 20
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
    
    with tab4:
        st.subheader("1️⃣7️⃣ Average RMS and Gap by Country (Top 20)")
        query = """
            SELECT country,
                   ROUND(AVG(rms), 3) as avg_rms,
                   ROUND(AVG(gap), 2) as avg_gap,
                   COUNT(*) as count
            FROM earthquake_db.earthquakes
            GROUP BY country
            HAVING count > 20
            ORDER BY count DESC
            LIMIT 20
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.bar(df, x='country', y='avg_rms', 
                             title="Average RMS by Country")
                fig1.update_xaxes(tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                fig2 = px.bar(df, x='country', y='avg_gap',
                             title="Average Gap by Country")
                fig2.update_xaxes(tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
    
    with tab5:
        st.subheader("1️⃣8️⃣ Events with High Station Coverage")
        threshold = st.slider("Select NST Threshold", 0, 500, 100)
        query = f"""
            SELECT time, place, mag, nst, country
            FROM earthquake_db.earthquakes
            WHERE nst > {threshold}
            ORDER BY nst DESC
            LIMIT 50
        """
        df = run_query(query)
        if df is not None:
            st.metric("Events with NST > " + str(threshold), len(df))
            st.dataframe(df, use_container_width=True)

# ==================== TSUNAMIS & ALERTS ====================
elif analysis_category == "Tsunamis & Alerts":
    st.header("🌊 Tsunami & Alert Analysis")
    
    tab1, tab2 = st.tabs(["Tsunami by Year", "Significance Analysis"])
    
    with tab1:
        st.subheader("1️⃣9️⃣ Tsunamis Triggered per Year")
        query = """
            SELECT year, COUNT(*) as tsunami_count
            FROM earthquake_db.earthquakes
            WHERE tsunami = 1
            GROUP BY year
            ORDER BY year
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.line(df, x='year', y='tsunami_count', markers=True,
                         title="Tsunami Events by Year",
                         labels={'tsunami_count': 'Number of Tsunamis'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Total tsunamis
            total = run_query("SELECT COUNT(*) as total FROM earthquake_db.earthquakes WHERE tsunami = 1")
            if total is not None:
                st.success(f"📊 Total Tsunami Events: {total['total'][0]:,}")
    
    with tab2:
        st.subheader("2️⃣0️⃣ High Significance Events (Top 50)")
        query = """
            SELECT time, place, mag, depth_km, sig, tsunami, country
            FROM earthquake_db.earthquakes
            ORDER BY sig DESC
            LIMIT 50
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.scatter(df, x='mag', y='sig', size='sig', color='tsunami',
                           hover_data=['place', 'time'],
                           title="Magnitude vs Significance (Tsunami Highlighted)")
            st.plotly_chart(fig, use_container_width=True)

# ==================== SEISMIC PATTERNS & TRENDS ====================
elif analysis_category == "Seismic Patterns & Trends":
    st.header("📊 Seismic Patterns & Trends Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Top Countries", "Shallow & Deep", "YoY Growth", "Active Regions"
    ])
    
    with tab1:
        st.subheader("2️⃣1️⃣ Top 5 Countries by Average Magnitude (Last 10 Years)")
        query = """
            SELECT country,
                   ROUND(AVG(mag), 2) as avg_mag,
                   COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE year >= YEAR(CURDATE()) - 10
            GROUP BY country
            HAVING count > 100
            ORDER BY avg_mag DESC
            LIMIT 5
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='country', y='avg_mag', color='avg_mag',
                        title="Top 5 Countries by Average Magnitude",
                        labels={'avg_mag': 'Average Magnitude'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("2️⃣2️⃣ Countries with Both Shallow & Deep Earthquakes in Same Month")
        query = """
            SELECT country, year, month, 
                   SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) as shallow_count,
                   SUM(CASE WHEN depth_km >= 70 THEN 1 ELSE 0 END) as deep_count
            FROM earthquake_db.earthquakes
            GROUP BY country, year, month
            HAVING shallow_count > 0 AND deep_count > 0
            ORDER BY year DESC, month DESC
            LIMIT 100
        """
        df = run_query(query)
        if df is not None:
            st.metric("Countries with Mixed Depth Patterns", len(df['country'].unique()))
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("2️⃣3️⃣ Year-over-Year Growth Rate")
        query = """
            SELECT year, 
                   COUNT(*) as count,
                   LAG(COUNT(*)) OVER (ORDER BY year) as prev_count
            FROM earthquake_db.earthquakes
            GROUP BY year
            ORDER BY year
        """
        df = run_query(query)
        if df is not None:
            df['growth_rate'] = ((df['count'] - df['prev_count']) / df['prev_count'] * 100).round(2)
            df = df.dropna()
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='year', y='growth_rate',
                        title="Year-over-Year Growth Rate (%)",
                        labels={'growth_rate': 'Growth Rate (%)'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("2️⃣4️⃣ Top 3 Most Seismically Active Regions")
        query = """
            SELECT country,
                   COUNT(*) as frequency,
                   ROUND(AVG(mag), 2) as avg_mag,
                   ROUND((COUNT(*) * AVG(mag)), 2) as activity_score
            FROM earthquake_db.earthquakes
            GROUP BY country
            ORDER BY activity_score DESC
            LIMIT 3
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='country', y='activity_score', color='activity_score',
                        title="Most Seismically Active Regions (Frequency × Avg Magnitude)",
                        labels={'activity_score': 'Activity Score'})
            st.plotly_chart(fig, use_container_width=True)

# ==================== DEPTH & LOCATION ANALYSIS ====================
elif analysis_category == "Depth & Location Analysis":
    st.header("🗺️ Depth, Location & Distance Analysis")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Equatorial Depth", "Shallow/Deep Ratio", "Tsunami Magnitude",
        "Data Reliability", "Consecutive Events", "Deep-Focus Regions"
    ])
    
    with tab1:
        st.subheader("2️⃣5️⃣ Average Depth within ±5° of Equator")
        query = """
            SELECT country,
                   ROUND(AVG(depth_km), 2) as avg_depth,
                   COUNT(*) as count
            FROM earthquake_db.earthquakes
            WHERE latitude BETWEEN -5 AND 5
            GROUP BY country
            HAVING count > 5
            ORDER BY avg_depth DESC
            LIMIT 20
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='country', y='avg_depth', color='avg_depth',
                        title="Average Depth Near Equator (±5° Latitude)")
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("2️⃣6️⃣ Shallow to Deep Earthquake Ratio by Country")
        query = """
            SELECT country,
                   SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) as shallow_count,
                   SUM(CASE WHEN depth_km >= 70 THEN 1 ELSE 0 END) as deep_count,
                   ROUND(
                       SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) / 
                       NULLIF(SUM(CASE WHEN depth_km >= 70 THEN 1 ELSE 0 END), 0), 
                   2) as shallow_to_deep_ratio
            FROM earthquake_db.earthquakes
            GROUP BY country
            HAVING shallow_count > 10 AND deep_count > 10
            ORDER BY shallow_to_deep_ratio DESC
            LIMIT 20
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='country', y='shallow_to_deep_ratio', 
                        color='shallow_to_deep_ratio',
                        title="Shallow to Deep Earthquake Ratio")
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("2️⃣7️⃣ Magnitude Difference: Tsunami vs Non-Tsunami")
        query = """
            SELECT 
                ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END), 2) as avg_mag_tsunami,
                ROUND(AVG(CASE WHEN tsunami = 0 THEN mag END), 2) as avg_mag_no_tsunami,
                ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END) - 
                      AVG(CASE WHEN tsunami = 0 THEN mag END), 2) as magnitude_difference
            FROM earthquake_db.earthquakes
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Mag (Tsunami)", df['avg_mag_tsunami'][0])
            col2.metric("Avg Mag (No Tsunami)", df['avg_mag_no_tsunami'][0])
            col3.metric("Difference", df['magnitude_difference'][0])
    
    with tab4:
        st.subheader("2️⃣8️⃣ Events with Lowest Data Reliability (Top 50)")
        query = """
            SELECT time, place, mag, depth_km,
                   ROUND(gap, 2) as gap,
                   ROUND(rms, 3) as rms,
                   ROUND((gap + rms * 100), 2) as error_score
            FROM earthquake_db.earthquakes
            WHERE gap > 0 AND rms > 0
            ORDER BY error_score DESC
            LIMIT 50
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.scatter(df, x='gap', y='rms', size='mag', color='error_score',
                           hover_data=['place', 'time'],
                           title="Data Reliability: Gap vs RMS")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("2️⃣9️⃣ Consecutive Earthquakes (Within 50km & 1 Hour)")
        st.info("This query finds pairs of earthquakes occurring close in space and time")
        query = """
            SELECT 
                e1.time as time1, e1.place as place1, e1.mag as mag1,
                e2.time as time2, e2.place as place2, e2.mag as mag2,
                ROUND(
                    6371 * ACOS(
                        COS(RADIANS(e1.latitude)) * COS(RADIANS(e2.latitude)) *
                        COS(RADIANS(e2.longitude) - RADIANS(e1.longitude)) +
                        SIN(RADIANS(e1.latitude)) * SIN(RADIANS(e2.latitude))
                    ), 2
                ) as distance_km,
                ROUND(TIMESTAMPDIFF(MINUTE, e1.time, e2.time) / 60.0, 2) as time_diff_hours
            FROM earthquake_db.earthquakes e1
            JOIN earthquake_db.earthquakes e2 
                ON e1.id < e2.id
                AND e2.time BETWEEN e1.time AND DATE_ADD(e1.time, INTERVAL 1 HOUR)
            HAVING distance_km <= 50
            ORDER BY time1 DESC
            LIMIT 100
        """
        df = run_query(query)
        if df is not None:
            st.metric("Consecutive Event Pairs Found", len(df))
            st.dataframe(df, use_container_width=True)
    
    with tab6:
        st.subheader("3️⃣0️⃣ Deep-Focus Earthquake Regions (Depth > 300km)")
        query = """
            SELECT country,
                   COUNT(*) as deep_focus_count,
                   ROUND(AVG(mag), 2) as avg_mag,
                   ROUND(AVG(depth_km), 2) as avg_depth
            FROM earthquake_db.earthquakes
            WHERE depth_km > 300
            GROUP BY country
            ORDER BY deep_focus_count DESC
            LIMIT 20
        """
        df = run_query(query)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x='country', y='deep_focus_count', 
                        color='avg_depth',
                        title="Regions with Deep-Focus Earthquakes (>300km)")
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🌍 **Data Source:** USGS Earthquake Catalog | **Database:** MySQL")
st.markdown("📊 **Features Analyzed:** 26+ earthquake attributes including magnitude, depth, location, time, quality metrics, and more")