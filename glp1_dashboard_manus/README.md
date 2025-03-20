# GLP-1 Medications Side Effects Dashboard Using Fully Automated Workflow Executed Using Manus AI
This workflow and dashboard was created using Manus AI.
The conceptualization and ideas relating to the type of data and questions to be answered are original. Only the execution is fully AI-driven.
This repository contains a Streamlit dashboard that visualizes real-world evidence (RWE) and real-world data (RWD) on side effects of GLP-1 and similar obesity medications. The dashboard uses data from trusted scientific sources including FDA FAERS, PubMed, and ClinicalTrials.gov.

## Dashboard Features

The dashboard includes six main modules:

1. **Main Overview** - Summary of key findings and trends
2. **Medication Comparison** - Direct comparison between different GLP-1 medications
3. **Demographic Analysis** - Explores gender and age differences in side effects
4. **Organ System Impact** - Shows which body systems are most affected
5. **Real-World vs Clinical Trials** - Compares controlled trial outcomes with real-world experiences
6. **Geographic Analysis** - Examines regional variations in medication use and side effects

## Repository Structure

- `src/` - Contains the main Streamlit application code
- `scripts/` - Contains data processing scripts
- `data/` - Contains processed data files
- `docs/` - Contains documentation

## Installation and Usage

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```
   cd src
   streamlit run app.py
   ```

## Deployment

This dashboard can be deployed to Streamlit Cloud for free:

1. Push this repository to GitHub (make sure it's public)
2. Sign up for Streamlit Cloud at https://streamlit.io/cloud
3. Connect your GitHub account and deploy directly from your repository

## Data Sources

All data is sourced from scientifically trusted sources:
- FDA Adverse Event Reporting System (FAERS)
- Published research studies from PubMed
- Clinical trial data from ClinicalTrials.gov

## License

This project is for educational and research purposes only.
