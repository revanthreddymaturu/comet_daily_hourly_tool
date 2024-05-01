import streamlit as st
import pandas as pd
import os
from pathlib import Path
from io import StringIO

def process_and_save_csv(file_content, file_name):
    # Load the data
    data = pd.read_csv(StringIO(file_content))
    
    # Convert 'Time' column to datetime and set as index
    data['Time'] = pd.to_datetime(data['Time'])
    data.set_index('Time', inplace=True)
    
    # Remove duplicates based on index
    data = data[~data.index.duplicated(keep='first')]
    
    # Resample to hourly and daily averages
    hourly_data = data.resample('H').mean()
    daily_data = data.resample('D').mean()

    # Ensure continuous datetime range for both hourly and daily data
    all_hours = pd.date_range(start=hourly_data.index.min(), end=hourly_data.index.max(), freq='H')
    all_days = pd.date_range(start=daily_data.index.min(), end=daily_data.index.max(), freq='D')
    
    hourly_data = hourly_data.reindex(all_hours)
    daily_data = daily_data.reindex(all_days)

   # Convert DataFrames to CSV format
    hourly_csv = hourly_data.to_csv(index=True)
    daily_csv = daily_data.to_csv(index=True)

    return hourly_csv, daily_csv

# Main function to run the app
def main():
    st.title('CSV Data Processing Tool')

    # Allow user to upload CSV files
    uploaded_files = st.file_uploader('Upload CSV files', type=['csv'], accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            file_name = file.name
            file_content = file.getvalue()
            
            if st.button('Start Processing'):
                with st.spinner(f'Processing {file_name}...'):
                    hourly_csv, daily_csv = process_and_save_csv(file_content, file_name)
                
                # Display the processed files
                st.write('### Hourly Averages')
                st.write(hourly_csv, unsafe_allow_html=True)
                st.write('### Daily Averages')
                st.write(daily_csv, unsafe_allow_html=True)

                # Add download buttons
                st.markdown(get_download_link(hourly_csv, f'{file_name}_Hourly_Averages.csv'), unsafe_allow_html=True)
                st.markdown(get_download_link(daily_csv, f'{file_name}_Daily_Averages.csv'), unsafe_allow_html=True)

# Function to create a download link for a CSV file
def get_download_link(csv_content, file_name):
    csv = csv_content.encode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href


if __name__ == '__main__':
    main()
