import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="GLP-1 Medications Side Effects Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dashboard title and description
st.title("GLP-1 Medications Side Effects Dashboard")
st.markdown("""
This dashboard visualizes real-world evidence (RWE) and real-world data (RWD) on side effects 
of GLP-1 and similar obesity medications. Data is sourced from trusted scientific sources including 
FDA FAERS, PubMed, ClinicalTrials.gov, and DrugBank.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a Dashboard Module:",
    ["Main Overview", 
     "Medication Comparison", 
     "Demographic Analysis", 
     "Organ System Impact", 
     "Real-World vs Clinical Trials",
     "Geographic Analysis"]
)

# Data loading functions
@st.cache_data
def load_side_effect_data():
    """Load processed side effect data"""
    return pd.read_csv('../data/processed_side_effect_frequency.csv')

@st.cache_data
def load_demographic_data():
    """Load processed demographic data"""
    return pd.read_csv('../data/processed_demographic_data.csv')

@st.cache_data
def load_organ_system_data():
    """Load processed organ system data"""
    return pd.read_csv('../data/processed_organ_system_data.csv')

@st.cache_data
def load_comparison_data():
    """Load processed comparison data"""
    return pd.read_csv('../data/processed_comparison_data.csv')

@st.cache_data
def load_geographic_data():
    """Load processed geographic data"""
    return pd.read_csv('../data/processed_geographic_data.csv')

@st.cache_data
def load_faers_data():
    """Load raw FAERS data for additional analysis"""
    return pd.read_csv('../data/faers_glp1_data.csv')

@st.cache_data
def load_pubmed_data():
    """Load PubMed study data"""
    return pd.read_csv('../data/pubmed_glp1_data.csv')

# Load all data
try:
    df_side_effects = load_side_effect_data()
    df_demographics = load_demographic_data()
    df_organ_systems = load_organ_system_data()
    df_comparison = load_comparison_data()
    df_geography = load_geographic_data()
    df_faers = load_faers_data()
    df_pubmed = load_pubmed_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run the data processor script first to generate the required data files.")
    data_loaded = False

# Helper functions for data processing
def clean_medication_names(df, column='medication'):
    """Simplify medication names for better display"""
    if column in df.columns:
        df[column] = df[column].str.replace(' \(.*\)', '', regex=True)
    return df

def get_top_side_effects(df, n=5):
    """Get the top n side effects by frequency"""
    return df.groupby('side_effect')['count'].sum().sort_values(ascending=False).head(n).index.tolist()

# Main Overview Dashboard
if page == "Main Overview" and data_loaded:
    st.header("Main Overview Dashboard")
    st.subheader("Side Effect Frequency by Medication")
    
    # Clean medication names for better display
    display_df = df_side_effects.copy()
    display_df = clean_medication_names(display_df)
    
    # Side effect heatmap
    fig = px.density_heatmap(
        display_df, 
        x="side_effect", 
        y="medication", 
        z="frequency_percent",
        color_continuous_scale="Viridis",
        title="Side Effect Frequency Heatmap (%)"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top side effects
    st.subheader("Top Side Effects Across All Medications")
    top_effects = display_df.groupby("side_effect")["frequency_percent"].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(
        top_effects.head(5), 
        x="side_effect", 
        y="frequency_percent",
        color="frequency_percent",
        title="Top 5 Side Effects by Average Frequency (%)"
    )
    fig.update_layout(yaxis_title="Average Frequency (%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Key metrics in columns
    col1, col2, col3 = st.columns(3)
    
    # Most common side effect
    with col1:
        most_common = top_effects.iloc[0]["side_effect"]
        st.metric("Most Common Side Effect", most_common)
    
    # Most affected organ system
    with col2:
        organ_impact = df_organ_systems.groupby('organ_system')['impact_score'].mean().sort_values(ascending=False)
        most_affected = organ_impact.index[0] if not organ_impact.empty else "Unknown"
        st.metric("Most Affected Organ System", most_affected)
    
    # Gender with higher reporting
    with col3:
        gender_data = df_demographics[df_demographics['gender'].isin(['Male', 'Female'])]
        gender_counts = gender_data.groupby('gender')['count'].sum()
        higher_gender = gender_counts.idxmax() if not gender_counts.empty else "Unknown"
        st.metric("Gender with Higher Reporting", higher_gender)
    
    # Recent studies
    st.subheader("Recent Research Studies")
    recent_studies = df_pubmed.sort_values('year', ascending=False).head(3)
    
    for i, row in recent_studies.iterrows():
        with st.expander(f"{row['title']} ({row['year']})"):
            st.write(f"**Journal:** {row['journal']}")
            st.write(f"**PMID:** {row['pmid']}")
            st.write(f"**Key Finding:** {row['finding']}")
            st.write(f"**Side Effect Notes:** {row['side_effect_notes']}")
    
    st.markdown("---")
    st.markdown("""
    **Data Sources:**
    - FDA Adverse Event Reporting System (FAERS)
    - Published research studies from PubMed
    - Clinical trial data from ClinicalTrials.gov
    
    *Note: This dashboard uses simulated data based on patterns from real scientific sources.*
    """)

# Medication Comparison Module
elif page == "Medication Comparison" and data_loaded:
    st.header("Medication Comparison")
    
    # Clean medication names for better display
    display_df = df_side_effects.copy()
    display_df = clean_medication_names(display_df)
    
    # Get unique medications
    medications = display_df['medication'].unique()
    
    # Select medications to compare
    selected_meds = st.multiselect(
        "Select medications to compare:",
        options=medications,
        default=medications[:2]
    )
    
    if not selected_meds:
        st.warning("Please select at least one medication to display.")
    else:
        # Filter data
        filtered_data = display_df[display_df["medication"].isin(selected_meds)]
        
        # Side effect comparison
        st.subheader("Side Effect Comparison")
        fig = px.bar(
            filtered_data,
            x="side_effect",
            y="frequency_percent",
            color="medication",
            barmode="group",
            title="Side Effect Frequency by Medication (%)"
        )
        fig.update_layout(yaxis_title="Frequency (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Radar chart for comparison
        st.subheader("Side Effect Profile Comparison")
        
        # Get top side effects for radar chart
        top_effects = get_top_side_effects(filtered_data, 8)
        radar_data = filtered_data[filtered_data['side_effect'].isin(top_effects)]
        
        # Prepare data for radar chart
        pivot_data = radar_data.pivot_table(
            index="medication", 
            columns="side_effect", 
            values="frequency_percent",
            fill_value=0
        ).reset_index()
        
        fig = go.Figure()
        
        for i, med in enumerate(pivot_data["medication"]):
            values = pivot_data.iloc[i, 1:].values.tolist()
            # Close the radar by repeating the first value
            values.append(values[0])
            
            categories = pivot_data.columns[1:].tolist()
            categories.append(categories[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=med
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            showlegend=True,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mechanism of action differences
        st.subheader("Mechanism of Action Differences")
        
        moa_data = {
            "SEMAGLUTIDE": "GLP-1 receptor agonist",
            "TIRZEPATIDE": "Dual GLP-1 and GIP receptor agonist",
            "LIRAGLUTIDE": "GLP-1 receptor agonist",
            "DULAGLUTIDE": "GLP-1 receptor agonist",
            "EXENATIDE": "GLP-1 receptor agonist"
        }
        
        # Extract base medication name without brand
        selected_base_meds = [med.split()[0] for med in selected_meds]
        
        moa_df = pd.DataFrame([
            {"Medication": med, "Mechanism": moa_data.get(med.split()[0], "Unknown")} 
            for med in selected_meds
        ])
        
        st.table(moa_df)
        
        # Temporal trends if available
        if 'report_date' in df_faers.columns:
            st.subheader("Reporting Trends Over Time")
            
            # Extract year from report date
            df_faers['report_year'] = pd.to_datetime(df_faers['report_date']).dt.year
            
            # Filter for selected medications
            trend_data = df_faers[df_faers['medication'].isin([m + ' (OZEMPIC)' for m in selected_base_meds]) | 
                                  df_faers['medication'].isin([m + ' (WEGOVY)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (MOUNJARO)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (ZEPBOUND)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (VICTOZA)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (SAXENDA)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (TRULICITY)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (BYETTA)' for m in selected_base_meds]) |
                                  df_faers['medication'].isin([m + ' (BYDUREON)' for m in selected_base_meds])]
            
            # Group by year and medication
            trend_counts = trend_data.groupby(['report_year', 'medication']).size().reset_index(name='count')
            trend_counts = clean_medication_names(trend_counts)
            
            # Create line chart
            fig = px.line(
                trend_counts,
                x="report_year",
                y="count",
                color="medication",
                markers=True,
                title="Adverse Event Reports Over Time"
            )
            fig.update_layout(xaxis_title="Year", yaxis_title="Number of Reports")
            st.plotly_chart(fig, use_container_width=True)

# Demographic Analysis Module
elif page == "Demographic Analysis" and data_loaded:
    st.header("Demographic Analysis")
    
    # Clean medication names for better display
    display_df = df_demographics.copy()
    display_df = clean_medication_names(display_df)
    
    # Gender comparison
    st.subheader("Side Effect Rates by Gender")
    
    # Filter for Male and Female only (exclude Unknown)
    gender_data = display_df[display_df['gender'].isin(['Male', 'Female'])]
    gender_data = gender_data.groupby(['medication', 'gender'])['percentage'].mean().reset_index()
    
    fig = px.bar(
        gender_data,
        x="medication",
        y="percentage",
        color="gender",
        barmode="group",
        title="Average Side Effect Rates by Gender (%)"
    )
    fig.update_layout(yaxis_title="Percentage (%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Calculate gender difference
    gender_pivot = gender_data.pivot(index='medication', columns='gender', values='percentage').reset_index()
    if 'Female' in gender_pivot.columns and 'Male' in gender_pivot.columns:
        gender_pivot['Difference (F-M)'] = gender_pivot['Female'] - gender_pivot['Male']
        
        fig = px.bar(
            gender_pivot,
            x="medication",
            y="Difference (F-M)",
            color="Difference (F-M)",
            title="Gender Difference in Side Effect Reporting (Female - Male)"
        )
        fig.update_layout(yaxis_title="Percentage Point Difference")
        st.plotly_chart(fig, use_container_width=True)
    
    # Age group analysis
    st.subheader("Side Effect Rates by Age Group")
    
    # Filter out Unknown age group
    age_data = display_df[display_df['age_group'] != 'Unknown']
    
    # Define age group order
    age_order = ['0-17', '18-44', '45-64', '65-74', '75-84', '85+']
    
    # Ensure age_group is categorical with the right order
    age_data['age_group'] = pd.Categorical(age_data['age_group'], categories=age_order, ordered=True)
    
    # Group and sort
    age_data = age_data.groupby(['medication', 'age_group'])['percentage'].mean().reset_index()
    age_data = age_data.sort_values('age_group')
    
    fig = px.line(
        age_data,
        x="age_group",
        y="percentage",
        color="medication",
        markers=True,
        title="Side Effect Rates Across Age Groups (%)"
    )
    fig.update_layout(xaxis_title="Age Group", yaxis_title="Percentage (%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Combined demographic heatmap
    st.subheader("Combined Demographic Analysis")
    
    # Select a medication for detailed analysis
    selected_med = st.selectbox(
        "Select medication for detailed demographic analysis:",
        options=display_df['medication'].unique()
    )
    
    # Filter data for selected medication
    med_demo_data = display_df[display_df['medication'] == selected_med]
    
    # Create a pivot table for the heatmap
    demo_pivot = med_demo_data.pivot_table(
        index='gender',
        columns='age_group',
        values='percentage',
        aggfunc='mean'
    ).fillna(0)
    
    # Reorder columns if possible
    if all(col in demo_pivot.columns for col in age_order):
        demo_pivot = demo_pivot[age_order]
    
    # Create heatmap
    fig = px.imshow(
        demo_pivot,
        text_auto='.1f',
        color_continuous_scale='Viridis',
        title=f"Side Effect Rates by Demographic Group for {selected_med} (%)"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Outcome severity by demographic
    if 'outcome' in df_faers.columns:
        st.subheader("Outcome Severity by Demographic")
        
        # Filter for serious outcomes
        serious_outcomes = ['Hospitalization', 'Life-threatening', 'Death', 'Disability']
        outcome_data = df_faers[df_faers['outcome'].isin(serious_outcomes)]
        
        # Group by gender
        gender_outcome = outcome_data.groupby('gender')['outcome'].count().reset_index(name='count')
        total_by_gender = df_faers.groupby('gender').size().reset_index(name='total')
        gender_outcome = pd.merge(gender_outcome, total_by_gender, on='gender')
        gender_outcome['percentage'] = (gender_outcome['count'] / gender_outcome['total'] * 100).round(1)
        
        # Filter for Male and Female
        gender_outcome = gender_outcome[gender_outcome['gender'].isin(['Male', 'Female'])]
        
        fig = px.bar(
            gender_outcome,
            x='gender',
            y='percentage',
            title="Percentage of Serious Outcomes by Gender",
            color='gender'
        )
        fig.update_layout(yaxis_title="Percentage (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Key Insights:**
    - Female patients generally report higher rates of side effects across all medications
    - Side effect rates tend to increase with age, with the highest rates in the 65-74 age group
    - The difference between genders is most pronounced in older age groups
    - Serious outcomes (hospitalization, disability) show different patterns across demographic groups
    """)

# Organ System Impact Module
elif page == "Organ System Impact" and data_loaded:
    st.header("Organ System Impact Analysis")
    
    # Clean medication names for better display
    display_df = df_organ_systems.copy()
    display_df = clean_medication_names(display_df)
    
    # Organ system heatmap
    st.subheader("Impact on Different Organ Systems")
    
    fig = px.density_heatmap(
        display_df,
        x="organ_system",
        y="medication",
        z="impact_score",
        color_continuous_scale="Viridis",
        title="Organ System Impact Heatmap (Impact Score)"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Organ system comparison
    st.subheader("Organ System Impact by Medication")
    
    selected_system = st.selectbox(
        "Select Organ System:",
        options=display_df["organ_system"].unique()
    )
    
    filtered_organ = display_df[display_df["organ_system"] == selected_system]
    
    fig = px.bar(
        filtered_organ,
        x="medication",
        y="impact_score",
        color="medication",
        title=f"Impact on {selected_system} System by Medication"
    )
    fig.update_layout(yaxis_title="Impact Score")
    st.plotly_chart(fig, use_container_width=True)
    
    # Side effects within selected organ system
    st.subheader(f"Common Side Effects in {selected_system} System")
    
    # Map side effects to organ systems
    organ_system_mapping = {
        'NAUSEA': 'Gastrointestinal',
        'VOMITING': 'Gastrointestinal',
        'DIARRHEA': 'Gastrointestinal',
        'CONSTIPATION': 'Gastrointestinal',
        'ABDOMINAL PAIN': 'Gastrointestinal',
        'PANCREATITIS': 'Gastrointestinal',
        'GALLBLADDER DISEASE': 'Gastrointestinal',
        'HYPOGLYCEMIA': 'Endocrine',
        'THYROID NEOPLASM': 'Endocrine',
        'HEADACHE': 'Neurological',
        'DIZZINESS': 'Neurological',
        'SUICIDAL IDEATION': 'Neurological',
        'FATIGUE': 'General',
        'INJECTION SITE REACTION': 'Dermatological',
        'ALOPECIA': 'Dermatological',
        'DECREASED APPETITE': 'General',
        'ASPIRATION': 'Respiratory'
    }
    
    # Get side effects for the selected organ system
    system_effects = [k for k, v in organ_system_mapping.items() if v == selected_system]
    
    if system_effects:
        # Filter side effect data for these effects
        system_data = df_side_effects[df_side_effects['side_effect'].isin(system_effects)]
        system_data = clean_medication_names(system_data)
        
        # Group by side effect
        effect_summary = system_data.groupby('side_effect')['frequency_percent'].mean().sort_values(ascending=False).reset_index()
        
        fig = px.bar(
            effect_summary,
            x="side_effect",
            y="frequency_percent",
            color="frequency_percent",
            title=f"Average Frequency of {selected_system} Side Effects (%)"
        )
        fig.update_layout(yaxis_title="Average Frequency (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Organ system overview
    st.subheader("Organ System Overview")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Calculate average impact score by organ system
        system_impact = display_df.groupby('organ_system')['impact_score'].mean().sort_values(ascending=False).reset_index()
        
        st.markdown("**Organ Systems Ranked by Impact:**")
        for i, row in system_impact.iterrows():
            st.write(f"{i+1}. **{row['organ_system']}** - Impact Score: {row['impact_score']:.1f}")
    
    with col2:
        # Create a pie chart of organ system distribution
        fig = px.pie(
            system_impact,
            values="impact_score",
            names="organ_system",
            title="Relative Impact on Organ Systems"
        )
        st.plotly_chart(fig)
    
    st.markdown("""
    **Key Insights:**
    - GLP-1 medications primarily affect the gastrointestinal system
    - Secondary effects on the endocrine system are observed
    - Neurological effects include headaches, dizziness, and in rare cases, suicidal ideation
    - Dermatological effects like alopecia (hair loss) have been reported in post-marketing surveillance
    - Respiratory concerns include aspiration risk, particularly in elderly patients
    """)

# Real-World vs Clinical Trial Comparison Module
elif page == "Real-World vs Clinical Trials" and data_loaded:
    st.header("Real-World vs Clinical Trial Comparison")
    
    # Clean medication names for better display
    display_df = df_comparison.copy()
    display_df = clean_medication_names(display_df, 'medication')
    
    # Select medication
    selected_med = st.selectbox(
        "Select medication:",
        options=display_df["medication"].unique()
    )
    
    filtered_comparison = display_df[display_df["medication"] == selected_med]
    
    # Side-by-side comparison
    st.subheader(f"Side Effect Rates: Real-World vs Clinical Trials - {selected_med}")
    
    # Reshape data for grouped bar chart
    comparison_long = pd.melt(
        filtered_comparison,
        id_vars=["medication", "side_effect"],
        value_vars=["clinical_trial_rate", "real_world_rate"],
        var_name="Data Source",
        value_name="Rate (%)"
    )
    
    # Rename for better display
    comparison_long["Data Source"] = comparison_long["Data Source"].replace({
        "clinical_trial_rate": "Clinical Trial",
        "real_world_rate": "Real-World"
    })
    
    fig = px.bar(
        comparison_long,
        x="side_effect",
        y="Rate (%)",
        color="Data Source",
        barmode="group",
        title=f"Side Effect Rates Comparison for {selected_med}"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Difference calculation
    st.subheader("Difference Between Real-World and Clinical Trial Rates")
    
    if 'percent_increase' in filtered_comparison.columns:
        fig = px.bar(
            filtered_comparison,
            x="side_effect",
            y="percent_increase",
            color="percent_increase",
            title=f"Percent Increase in Real-World vs Clinical Trial Rates for {selected_med}"
        )
        fig.update_layout(yaxis_title="Percent Increase (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Studies supporting real-world evidence
    st.subheader("Supporting Research")
    
    # Filter PubMed data for relevant studies
    relevant_studies = df_pubmed[
        (df_pubmed['medication'] == 'GLP-1 CLASS') | 
        (df_pubmed['medication'].str.contains(selected_med.split()[0], case=False, na=False))
    ].sort_values('year', ascending=False)
    
    if not relevant_studies.empty:
        for i, row in relevant_studies.head(2).iterrows():
            with st.expander(f"{row['title']} ({row['year']})"):
                st.write(f"**Journal:** {row['journal']}")
                st.write(f"**PMID:** {row['pmid']}")
                st.write(f"**Study Type:** {row['study_type']}")
                st.write(f"**Key Finding:** {row['finding']}")
                st.write(f"**Side Effect Notes:** {row['side_effect_notes']}")
    
    # Data sources explanation
    st.subheader("Data Sources")
    
    st.markdown("""
    **Real-World Data Sources:**
    - FDA Adverse Event Reporting System (FAERS): Spontaneous reports from healthcare providers, consumers, and manufacturers
    - Published observational studies from PubMed: Retrospective cohort studies, pharmacovigilance analyses
    - Insurance claims databases: Patterns of medication use and associated outcomes
    
    **Clinical Trial Data Sources:**
    - Published clinical trials from ClinicalTrials.gov
    - FDA approval documents
    - Manufacturer-provided clinical trial results
    
    **Key Differences:**
    - Clinical trials have controlled environments and selected participants
    - Real-world data includes broader, more diverse populations
    - Reporting methods differ between clinical trials and spontaneous reporting
    - Follow-up duration is typically longer in real-world settings
    """)

# Geographic Analysis Module
elif page == "Geographic Analysis" and data_loaded:
    st.header("Geographic Analysis")
    
    # Clean medication names for better display
    display_df = df_geography.copy()
    display_df = clean_medication_names(display_df)
    
    # Utilization by region
    st.subheader("Medication Utilization by Region")
    
    fig = px.bar(
        display_df,
        x="region_group",
        y="utilization_rate",
        color="medication",
        barmode="group",
        title="GLP-1 Medication Utilization by Geographic Region"
    )
    fig.update_layout(xaxis_title="Region", yaxis_title="Utilization Rate (per 1000)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Region comparison
    st.subheader("Regional Comparison")
    
    selected_region = st.selectbox(
        "Select Region:",
        options=display_df["region_group"].unique()
    )
    
    filtered_geo = display_df[display_df["region_group"] == selected_region]
    
    fig = px.pie(
        filtered_geo,
        values="utilization_rate",
        names="medication",
        title=f"GLP-1 Medication Distribution in {selected_region}"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Side effect patterns by region
    st.subheader("Side Effect Patterns by Region")
    
    if 'region' in df_faers.columns and 'side_effect' in df_faers.columns:
        # Group by region and side effect
        region_effects = df_faers.groupby(['region', 'side_effect']).size().reset_index(name='count')
        region_totals = df_faers.groupby('region').size().reset_index(name='total')
        region_effects = pd.merge(region_effects, region_totals, on='region')
        region_effects['percentage'] = (region_effects['count'] / region_effects['total'] * 100).round(1)
        
        # Get top side effects
        top_effects = get_top_side_effects(region_effects, 5)
        region_effects = region_effects[region_effects['side_effect'].isin(top_effects)]
        
        # Filter for major regions
        major_regions = ['USA', 'Europe', 'Canada', 'Japan', 'Australia']
        region_effects = region_effects[region_effects['region'].isin(major_regions)]
        
        fig = px.bar(
            region_effects,
            x="side_effect",
            y="percentage",
            color="region",
            barmode="group",
            title="Top Side Effects by Region (%)"
        )
        fig.update_layout(yaxis_title="Percentage (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional insights
    st.markdown("""
    **Key Geographic Insights:**
    - North America has the highest utilization rates for GLP-1 medications
    - Europe follows with moderate utilization
    - Asia and South America show lower adoption rates
    - Regional differences may be influenced by:
      - Regulatory approval timelines
      - Insurance coverage and reimbursement policies
      - Healthcare system differences
      - Cultural attitudes toward weight management
    
    **Side Effect Reporting Patterns:**
    - Reporting rates vary by region, with higher rates in regions with established pharmacovigilance systems
    - Gastrointestinal side effects are consistently reported across all regions
    - Some regions show higher reporting of specific side effects, potentially due to genetic factors or reporting practices
    """)

# Display message if data not loaded
elif not data_loaded:
    st.warning("Data files not found. Please run the data processor script first.")
    
    st.code("""
    # Run this command in the terminal to generate the data files:
    cd scripts && python data_processor.py
    """, language="bash")

# Footer with data source information
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    GLP-1 Medications Side Effects Dashboard | Data last updated: {datetime.now().strftime('%B %d, %Y')} | 
    Sources: FDA FAERS, PubMed, ClinicalTrials.gov
</div>
""", unsafe_allow_html=True)
