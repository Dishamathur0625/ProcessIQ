import streamlit as st

from components.sidebar import sidebar
from components.top_bar import top_bar
from components.summary_cards import summary_cards

from modules.ingestion.loader import FileLoader
from modules.ingestion.validation import DataValidator
from components.variable_table import variable_table
from components.missing_chart import missing_chart
from components.preview_table import preview_table
from components.time_series import time_series
from components.distribution import distribution
from components.boxplot import boxplot
from components.download import download
from components.export import export_module


st.set_page_config(
    page_title="ProcessIQ",
    page_icon="📊",
    layout="wide"
)

with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# -----------------------------
# Session State
# -----------------------------

if "df" not in st.session_state:
    st.session_state.df = None

if "validation" not in st.session_state:
    st.session_state.validation = None

if "filename" not in st.session_state:
    st.session_state.filename = None


# -----------------------------
# Sidebar
# -----------------------------

sidebar()


# -----------------------------
# Header
# -----------------------------

st.title("ProcessIQ")

st.caption("Industrial Data Analytics Platform")


# -----------------------------
# Upload
# -----------------------------

uploaded_file = st.file_uploader(

    "Upload Dataset",

    type=["csv", "xlsx", "xls"]

)


if uploaded_file is not None:

    try:

        df = FileLoader.load(uploaded_file)

        validation = DataValidator.validate(df)

        st.session_state.df = df

        st.session_state.validation = validation

        st.session_state.filename = uploaded_file.name

        st.success("Dataset uploaded successfully.")

    except Exception as e:

        st.error(str(e))


# -----------------------------
# If no dataset uploaded
# -----------------------------

if st.session_state.df is None:

    top_bar(
        file_name="No file uploaded",
        rows="-",
        columns="-",
        time_range="-"
    )

    summary_cards(
        rows=0,
        columns=0,
        missing=0,
        quality=0
    )

    st.info("Upload a dataset to begin analysis.")

    st.stop()


# -----------------------------
# Real Data
# -----------------------------

validation = st.session_state.validation


quality = round(

    100 - validation["missing_percentage"],

    2

)


top_bar(

    file_name=st.session_state.filename,

    rows=validation["rows"],

    columns=validation["columns"],

    time_range="-"

)


summary_cards(

    validation["rows"],

    validation["columns"],

    validation["missing_values"],

    quality

)
st.write("")

c1, c2, c3 = st.columns([2.5, 1.4, 2])

with c1:

    variable_table(st.session_state.df)

with c2:

    missing_chart(st.session_state.df)

with c3:

    preview_table(st.session_state.df)

st.write("")

c1, c2, c3 = st.columns([2.4, 1.4, 1.4])

with c1:
    time_series(st.session_state.df)

with c2:
    distribution(st.session_state.df)

with c3:
    boxplot(st.session_state.df)

st.write("")

left, center, right = st.columns([1.5, 1.8, 1])


with right:
    download(st.session_state.df)

st.divider()

export_module(st.session_state.df)