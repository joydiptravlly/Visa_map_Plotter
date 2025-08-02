import streamlit as st
import pandas as pd
import plotly.express as px

all_countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina",
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados",
    "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana",
    "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon",
    "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo",
    "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
    "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guatemala", "Guinea", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya",
    "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali",
    "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
    "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands",
    "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman",
    "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
    "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
    "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
    "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo",
    "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu",
    "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

def load_passport_data(selected_country):
    file_map = {
        "India": "India _visa_status.xlsx",
        "Japan": "Japan_visa_status.xlsx",
        "Germany": "Germany_visa_status.xlsx",
        "United Arab Emirates": "UAE_visa_status.xlsx"
    }
    file_name = file_map.get(selected_country)
    if not file_name:
        st.error("No dataset found for the selected country.")
        st.stop()
    df = pd.read_excel(file_name)
    return df

def prepare_visa_data(passport_df):
    df = passport_df.copy()
    df = df.rename(columns={
        'Countries': 'Destination',
        'Visa Requirement': 'Visa Type',
        'VR for schengen Visa holders': 'Schengen Visa Status',
        'VR for US Visa holders': 'US Visa Status',
        'Source': 'Source URL'   
    })
    
    df['Source URL'] = df['Source URL'].fillna('www.google.com').replace('', 'www.google.com')
    return df[['Destination', 'Visa Type', 'Schengen Visa Status', 'US Visa Status', 'Source URL']]


visa_colors = {
    'visa free': 'green',
    'visa on arrival': 'orange',
    'e-visa': 'blue',
    'visa required': 'red',
    'admission refused': 'gray'
}

def map_visa_type_to_color(visa_type):
    if pd.isna(visa_type):
        return 'lightgray'
    if not isinstance(visa_type, str):
        visa_type = str(visa_type)
    return visa_colors.get(visa_type.strip().lower(), 'lightgray')

st.set_page_config(page_title="Visa Map Plotter", layout="wide")
st.title("🌍 Visa Requirement Map Viewer")

st.markdown("""
Explore visa requirements for any destination country  
from your selected passport country.
""")

allowed_passports = [
    "India",
    "Japan",
    "Germany",
    "United Arab Emirates"
]
selected_passport = st.selectbox("Select your passport country:", allowed_passports)

schengen_status = st.selectbox("Do you have a valid Schengen Visa?", ["No", "Yes"])
us_status = st.selectbox("Do you have a valid US Visa?", ["No", "Yes"])

passport_df = load_passport_data(selected_passport)
visa_info_df = prepare_visa_data(passport_df)

# ✅ Merge with master country list
master_df = pd.DataFrame({'Destination': all_countries})
merged_df = master_df.merge(visa_info_df, on='Destination', how='left')
merged_df['Visa Type'] = merged_df['Visa Type'].fillna('No data')
merged_df['Schengen Visa Status'] = merged_df['Schengen Visa Status'].fillna('N/A')
merged_df['US Visa Status'] = merged_df['US Visa Status'].fillna('N/A')
merged_df['Color'] = merged_df['Visa Type'].apply(map_visa_type_to_color)

#Pick destination
selected_destination = st.selectbox("Select your destination country:", all_countries)
destination_info = merged_df[merged_df['Destination'].str.strip().str.lower() == selected_destination.strip().lower()]

if not destination_info.empty:
    # ----------------- Extract original visa values -----------------
    visa_type = destination_info['Visa Type'].values[0].strip().lower()
    schengen_vr = destination_info['Schengen Visa Status'].values[0].strip().lower() if schengen_status == 'Yes' else None
    us_vr = destination_info['US Visa Status'].values[0].strip().lower() if us_status == 'Yes' else None

    # ----------------- Source URL fix -----------------
    source_url = destination_info['Source URL'].values[0] if 'Source URL' in destination_info.columns else ''
    if not source_url or str(source_url).strip() == "":
        source_url = "https://www.google.com"
    elif not source_url.startswith("http"):
        source_url = "https://" + source_url

    # ----------------- Priority mapping -----------------
    priority = {
        'visa free': 1,
        'visa on arrival': 2,
        'e-visa': 3,
        'visa required': 4
    }

    valid_statuses = ['visa free', 'visa on arrival', 'e-visa', 'visa required']

    visa_options = []
    if visa_type in valid_statuses:
        visa_options.append(visa_type)
    if schengen_vr in valid_statuses:
        visa_options.append(schengen_vr)
    if us_vr in valid_statuses:
        visa_options.append(us_vr)

    best_visa_status = min(visa_options, key=lambda x: priority.get(x, 999))

    # ----------------- Display results -----------------
    st.subheader(f"Travel Info from {selected_passport} to {selected_destination}")
    st.markdown(f"**Visa Type:** {visa_type}")
    st.markdown(f"**Schengen Visa Status:** {schengen_vr if schengen_status == 'Yes' else 'N/A'}")
    st.markdown(f"**US Visa Status:** {us_vr if us_status == 'Yes' else 'N/A'}")
    st.markdown(
        f'**Official Source:** [Visit Source Website]({source_url})',
        unsafe_allow_html=True
    )

    # ✅ ✅ New smart summary
    summary = f"Since you have an **{selected_passport}** passport"
    if schengen_status == "Yes":
        summary += " and a **Schengen Visa**"
    if us_status == "Yes":
        summary += " and a **US Visa**"
    summary += f", you are eligible to travel to **{selected_destination}** with visa status: **{best_visa_status}**."

    st.markdown("---")
    st.markdown(summary)

else:
    st.warning(f"No visa info found for {selected_destination}.")



visa_info_df['Hover'] = visa_info_df.apply(
    lambda row: f"""
    {row['Destination']}<br>
    Visa: {row['Visa Type']}<br>
    Schengen Visa: {row['Schengen Visa Status'] if schengen_status == 'Yes' else 'N/A'}<br>
    US Visa: {row['US Visa Status'] if us_status == 'Yes' else 'N/A'}<br>
    Source: {row['Source URL']}
    """,
    axis=1
)

fig = px.choropleth(
    visa_info_df,
    locations="Destination",
    locationmode="country names",
    color="Visa Type",
    color_discrete_map=visa_colors,
    hover_name="Destination",
    hover_data={'Hover': True},
    title=f"Visa Map for {selected_passport} Passport"
)
fig.update_geos(projection_type="natural earth")
st.plotly_chart(fig, use_container_width=True)

# process to run this code:
#1. install all dependencies
#2. put the all dataset file(.xlsx file) and the code file in same folder
#3.Run with this Commanad:streamlit run visa_map_plotter.py

