
import streamlit as st
import pandas as pd


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title="Guests Dashboard",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Guests Dashboard")


# --------------------------------------------------
# LOAD EXCEL FILE
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("guests.xlsx")
    return df


df = load_data()


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

# Remove unnecessary spaces from column names
df.columns = df.columns.astype(str).str.strip()

# Find the Age column regardless of capitalization
age_matches = [
    col for col in df.columns
    if col.lower() == "age"
]

# Check if the Age column exists
if not age_matches:
    st.error("Could not find an Age column in your Excel file.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

AGE_COLUMN = age_matches[0]

# Convert age values to numbers
# Invalid or empty values will become NaN
df[AGE_COLUMN] = pd.to_numeric(
    df[AGE_COLUMN],
    errors="coerce"
)


# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------

# Total number of guests
total_guests = len(df)

# Count only guests with valid age values
valid_ages = df[AGE_COLUMN].notna()

# Adults: 18 years old or older
adults = len(df[valid_ages & (df[AGE_COLUMN] >= 18)])

# Minors: under 18 years old
minors = len(df[valid_ages & (df[AGE_COLUMN] < 18)])

# Minors below 5 years old
minors_below_5 = len(df[valid_ages & (df[AGE_COLUMN] < 5)])

# Guests with missing or invalid ages
missing_ages = len(df[~valid_ages])


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Total Guests",
        value=f"{total_guests:,}"
    )

with col2:
    st.metric(
        label="🧑 Adults",
        value=f"{adults:,}"
    )

with col3:
    st.metric(
        label="🧒 Minors",
        value=f"{minors:,}"
    )

with col4:
    st.metric(
        label="👶 Children Below 5",
        value=f"{minors_below_5:,}"
    )


# --------------------------------------------------
# DATA QUALITY
# --------------------------------------------------

if missing_ages > 0:
    st.warning(
        f"{missing_ages} guest(s) have missing or invalid age values "
        "and were excluded from the age calculations."
    )


# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------

st.divider()

st.subheader("Guest Records")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
