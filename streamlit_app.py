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
# Change these column names to match your Excel file
# --------------------------------------------------

AGE_COLUMN = "Age"


# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------

# Total number of guests
total_guests = len(df)

# Adults: 18 years old or older
adults = len(df[df[AGE_COLUMN] >= 18])

# Minors: under 18 years old
minors = len(df[df[AGE_COLUMN] < 18])

# Minors below 5 years old
minors_below_5 = len(df[df[AGE_COLUMN] < 5])


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
# DATA PREVIEW
# --------------------------------------------------

st.divider()

st.subheader("Guest Records")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
