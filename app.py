
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load your datasets (same URLs from your notebook)
@st.cache_data
def load_data():
    cases_url = 'https://drive.google.com/uc?id=1f38FA3WzDO2gs5sPsF34ckmAeDgbbrOJ'
    hearings_url = 'https://drive.google.com/uc?id=12PgUYlxXEVHinwjdAkb7ISOndL2oVWPg'
    df_cases = pd.read_csv(cases_url)
    df_hearings = pd.read_csv(hearings_url)
    return df_cases, df_hearings

df_cases, df_hearings = load_data()

# Dashboard Title
st.title("🏛️ NJDG Dashboard - Karnataka High Court")
st.markdown("**Case Management System for Judges & Lawyers**")

# Sidebar - User Role Selection
st.sidebar.header("User Profile")
user_type = st.sidebar.selectbox('Select Your Role', ['Judge', 'Lawyer', 'Administrator'])

# JUDGE VIEW
if user_type == 'Judge':
    st.header("⚖️ Judge Workload Dashboard")
    
    # Judge selection
    judges = df_cases['NJDG_JUDGE_NAME'].dropna().unique()
    selected_judge = st.sidebar.selectbox('Select Judge', judges)
    
    # Filter cases for selected judge
    judge_cases = df_cases[df_cases['NJDG_JUDGE_NAME'] == selected_judge]
    
    # Workload Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", len(judge_cases))
    col2.metric("Pending Cases", len(judge_cases[judge_cases['CURRENT_STATUS'] == 'Pending']))
    col3.metric("Disposed Cases", len(judge_cases[judge_cases['CURRENT_STATUS'] == 'Disposed']))
    
    # Case distribution by type
    st.subheader("📊 Case Type Distribution")
    case_type_dist = judge_cases['CASE_TYPE'].value_counts().head(10)
    fig1 = px.bar(x=case_type_dist.index, y=case_type_dist.values, 
                  labels={'x': 'Case Type', 'y': 'Count'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Recent cases table
    st.subheader("📋 Recent Cases")
    st.dataframe(judge_cases[['COMBINED_CASE_NUMBER', 'CASE_TYPE', 'CURRENT_STATUS', 
                               'DATE_FILED', 'DECISION_DATE']].head(20))

# LAWYER VIEW
elif user_type == 'Lawyer':
    st.header("👨‍⚖️ Lawyer Case Management")
    
    # Lawyer selection
    lawyers = df_hearings['PetitionerAdvocate'].dropna().unique()
    selected_lawyer = st.sidebar.selectbox('Select Lawyer', lawyers[:100])
    
    # Filter cases
    lawyer_cases = df_hearings[df_hearings['PetitionerAdvocate'] == selected_lawyer]
    
    # Metrics
    col1, col2 = st.columns(2)
    col1.metric("Active Cases", len(lawyer_cases['CNR_NUMBER'].unique()))
    col2.metric("Total Hearings", len(lawyer_cases))
    
    # Personal Notes Feature
    st.subheader("📝 Personal Notes")
    case_id = st.selectbox("Select Case for Notes", lawyer_cases['CNR_NUMBER'].unique())
    note_text = st.text_area("Add/Edit Notes for this case", height=150)
    if st.button("Save Note"):
        st.success(f"✅ Note saved for {case_id}")
    
    # Case list
    st.subheader("📂 Your Cases")
    st.dataframe(lawyer_cases[['CNR_NUMBER', 'HearingDate', 'CurrentStage', 
                                'Remappedstages']].head(20))

# ADMINISTRATOR VIEW
else:
    st.header("📈 System-Wide Analytics")
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cases", len(df_cases))
    col2.metric("Pending", len(df_cases[df_cases['CURRENT_STATUS'] == 'Pending']))
    col3.metric("Disposed", len(df_cases[df_cases['CURRENT_STATUS'] == 'Disposed']))
    col4.metric("Avg Disposal Time", f"{df_cases['DISPOSALTIME_ADJ'].mean():.0f} days")
    
    # Bottleneck Analysis
    st.subheader("🚦 Bottleneck Analysis - Case Stages")
    stage_counts = df_hearings['Remappedstages'].value_counts().head(10)
    fig2 = px.bar(x=stage_counts.values, y=stage_counts.index, orientation='h',
                  labels={'x': 'Number of Cases', 'y': 'Stage'},
                  title="Cases by Stage (Identify Bottlenecks)")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Progression Timeline
    st.subheader("📅 Case Filing Trend (Progression)")
    df_cases['DATE_FILED'] = pd.to_datetime(df_cases['DATE_FILED'], errors='coerce')
    filing_trend = df_cases.groupby(df_cases['DATE_FILED'].dt.to_period('M')).size()
    filing_trend.index = filing_trend.index.to_timestamp()
    fig3 = px.line(x=filing_trend.index, y=filing_trend.values,
                   labels={'x': 'Month', 'y': 'Cases Filed'})
    st.plotly_chart(fig3, use_container_width=True)
    
    # Priority Areas - Long Pending Cases
    st.subheader("⚠️ Priority Areas - Long Pending Cases")
    long_pending = df_cases[df_cases['DISPOSALTIME_ADJ'] > 1000].sort_values('DISPOSALTIME_ADJ', ascending=False)
    st.dataframe(long_pending[['COMBINED_CASE_NUMBER', 'CASE_TYPE', 'DATE_FILED', 
                                'DISPOSALTIME_ADJ', 'NJDG_JUDGE_NAME']].head(20))

