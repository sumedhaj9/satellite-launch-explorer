# (paste your full Streamlit code here)
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Satellite Launch Explorer", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("satellite launches.csv")
    df['launch_date'] = pd.to_datetime(df['launch_date'], errors='coerce')
    df['launch_year'] = df['launch_date'].dt.year
    df['status'] = df['status'].fillna("Unknown")
    df['owner'] = df['owner'].fillna("Unknown")
    return df

df = load_data()

st.title("🛰️ Global Satellite Launch Explorer")

# Step 1: World Map
st.subheader("1️⃣ Satellite Launches by Country")
country_counts = df['owner'].value_counts().reset_index()
country_counts.columns = ['country', 'count']

fig_map = px.choropleth(
    country_counts,
    locations='country',
    locationmode='country names',
    color='count',
    color_continuous_scale='YlOrRd',
    title="Number of Satellites Launched"
)
st.plotly_chart(fig_map, use_container_width=True)

# Step 2: Select Country
country = st.selectbox("Select a country to view details", country_counts['country'].unique())

if country:
    country_df = df[df['owner'] == country]
    yearly = country_df.groupby('launch_year').size().reset_index(name='count')

    st.subheader(f"2️⃣ Year-wise Satellite Launches: {country}")
    fig_year = px.line(yearly, x='launch_year', y='count', markers=True)
    st.plotly_chart(fig_year, use_container_width=True)

    # Step 3: Select Year
    year = st.selectbox("Select a year", yearly['launch_year'])
    if year:
        year_df = country_df[country_df['launch_year'] == year]
        status_counts = year_df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']

        st.subheader(f"3️⃣ Satellite Status in {year} ({country})")
        fig_status = px.bar(status_counts, x='status', y='count', color='status', text='count')
        st.plotly_chart(fig_status, use_container_width=True)

        selected_status = st.selectbox("Select Status", status_counts['status'])
        if selected_status:
          final_list = (
              year_df[year_df['status'] == selected_status][['name', 'launch_date', 'flight_ended', 'norad_id']]
              .rename(columns={
                  'name': 'Satellite Name',
                  'launch_date': 'Launch Date',
                  'flight_ended': 'Flight Ended',
                  'norad_id': 'NORAD ID'
              })
          )

          # Step 4: select status
          final_list['Launch Date'] = pd.to_datetime(final_list['Launch Date'], errors='coerce').dt.strftime('%b %d, %Y')
          final_list['Flight Ended'] = pd.to_datetime(final_list['Flight Ended'], errors='coerce').dt.strftime('%b %d, %Y')

          st.subheader(f"🛰️ Satellites from {country} ({year}, {selected_status})")

          # Display as info cards
          for _, row in final_list.iterrows():
              st.markdown(f"""
              <div style="
                  background-color:#f5f7fa;
                  padding:15px;
                  border-radius:12px;
                  margin-bottom:10px;
                  box-shadow:0 2px 4px rgba(0,0,0,0.08);
                  ">
                  <b style="font-size:16px;">{row['Satellite Name']}</b><br>
                  🚀 <b>Launch Date:</b> {row['Launch Date']}<br>
                  ⏳ <b>Flight Ended:</b> {row['Flight Ended'] if row['Flight Ended'] != 'NaT' else '—'}<br>
                  🆔 <b>NORAD ID:</b> {row['NORAD ID']}
              </div>
              """, unsafe_allow_html=True)
