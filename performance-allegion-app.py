import streamlit as st
import pandas as pd
import altair as alt

# Required columns
REQUIRED_COLUMNS = ['OS', 'Build Number', 'Target Device', 'OS Version', 'Load', 'feature', 'KPI Name', 'KPI Value']

# Constant columns to check
CONSTANT_COLUMNS = ['OS', 'Build Number', 'Target Device', 'OS Version']

# Initial Page Configuration
st.set_page_config(
    page_title="Performance Data Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar for file upload part
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 400px;
        }
    </style>
""", unsafe_allow_html=True)
st.sidebar.title("Upload Performance Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Check if a file is uploaded or not uploaded
if uploaded_file is not None:
    # Store the upload CSV file in a dataframe
    data_set = pd.read_csv(uploaded_file)
    uploaded_csv_column = data_set.columns.to_list()

    # Check for required columns and constant values [CSV Validation]
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in uploaded_csv_column]
    if missing_columns:
        st.error(f"The uploaded CSV file is missing the following required columns: {', '.join(missing_columns)}")
        st.warning(f"Please ensure that the CSV file contains all required columns: {', '.join(REQUIRED_COLUMNS)}")
        st.stop()

    if not missing_columns:
        # Validate constant columns
        csv_status = all(data_set[col].nunique() == 1 for col in CONSTANT_COLUMNS)
        if not csv_status:
            st.error("The uploaded CSV file contains inconsistent data.")
            st.warning(f"Please ensure that all constant columns have the same value: {', '.join(CONSTANT_COLUMNS)}")
        
        # Valid CSV file processing
        else: 
            st.markdown(
                "<h1 style='text-align: center; font-weight: bold;'>Performance Data Analysis</h1>",
                unsafe_allow_html=True
            )

            # Extract constant values
            os = data_set['OS'].iloc[0]
            build = data_set['Build Number'].iloc[0]
            device = data_set['Target Device'].iloc[0]
            os_version = data_set['OS Version'].iloc[0]

            # Dynamic metadata
            unique_features = data_set['feature'].unique()
            unique_kpis = data_set['KPI Name'].unique()


            # KPI selection in sidebar
            st.sidebar.header("KPI Filter")
            selected_kpis = st.sidebar.multiselect(
                "Select KPIs for analysis",
                options=unique_kpis,
                default=unique_kpis[:3],
            )

            # Uploaded CSV file preview and metadata display
            with st.container(border=True):
                st.subheader("📄 Uploaded CSV File Preview")

                # Layout with larger columns
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write("#### OS:", os)
                    st.write("#### Build Number:", build)
                    st.write("#### Target Device:", device)
                    st.write("#### OS Version:", os_version)
                with col2:
                    st.write("#### Unique Features:", len(unique_features))
                    st.write(unique_features)
                    st.write("#### Unique KPIs:", len(unique_kpis))

                st.divider()

                st.subheader("🧩 KPI Mapping by Feature")
                grouped = data_set.groupby('feature')['KPI Name'].unique()

                for feature, kpis in grouped.items():
                    with st.expander(f"🔹 {feature}", expanded=False):
                        for kpi in sorted(kpis):
                            st.write(f"• {kpi}")


                # Refresh button (debug)
                # st.button("🔄 Refresh Data") 

            # KPI Analysis Section based on the selected KPIs
            for kpi in selected_kpis:

                # Container for each KPI analysis
                with st.container(border=True):
                    # Header for each KPI
                    st.subheader(f"📊 KPI: {kpi}")

                    # Trend Line Chart based on the load levels
                    st.markdown("#### Trend Chart")
                    kpi_data = data_set[data_set['KPI Name'] == kpi].copy()
                    kpi_data['Run'] = kpi_data.groupby('Load').cumcount() + 1
                    chart = alt.Chart(kpi_data).mark_line(point=True).encode(
                        x=alt.X('Run:O', title='Run Index'),
                        y=alt.Y('KPI Value:Q', title='KPI Value (seconds)'),
                        color=alt.Color('Load:N', title='Load Level'),
                        tooltip=[
                            alt.Tooltip('Load:N', title='Load'),
                            alt.Tooltip('Run:O', title='Run'),
                            alt.Tooltip('KPI Value:Q', title='KPI Value (sec)', format=".3f")
                        ]
                    ).properties(
                        # title=f"KPI Value Trends for '{kpi}' (in seconds)",
                        width=700,
                        height=400
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)  

                    # Bar Chart for average KPI values by load
                    st.markdown("#### Bar Chart")
                    mean_data = kpi_data.groupby('Load', as_index=False)['KPI Value'].mean()
                    bar_chart = alt.Chart(mean_data).mark_bar().encode(
                        x=alt.X('Load:N', title='Load Level'),
                        y=alt.Y('KPI Value:Q', title='Average KPI Value (sec)'),
                        color=alt.Color('Load:N', legend=None),
                        tooltip=[alt.Tooltip('Load:N'), alt.Tooltip('KPI Value:Q', format=".3f")]
                    ).properties(
                        # title='📊 Average KPI Value by Load Level',
                        width=700,
                        height=300
                    )
                    st.altair_chart(bar_chart, use_container_width=True)


                    # Summary Statistics Table
                    st.markdown("#### Summary Statistics by Load")
                    summary = kpi_data.groupby('Load')['KPI Value'].agg(['min', 'max', 'mean', 'median']).reset_index()
                    summary.columns = ['Load', 'Min (sec)', 'Max (sec)', 'Mean (sec)', 'Median (sec)']
                    st.dataframe(summary.style.format({'Min (sec)': '{:.3f}', 'Max (sec)': '{:.3f}', 'Mean (sec)': '{:.3f}', 'Median (sec)': '{:.3f}'}))

else: 
    '''Prompt user to upload a file and also convey the user regarding the CSV file columns.'''
    st.write("Please upload a CSV file containing performance data using the sidebar.")
    st.write(f"Upload the CSV file which contain following columns: {", ".join(REQUIRED_COLUMNS)}")
    st.warning("Please upload a CSV file to proceed.")
