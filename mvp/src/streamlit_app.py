from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from open_housing_mvp import config

APP_ROOT = Path(__file__).resolve().parent
MODEL_PATH = APP_ROOT / config.MODEL_PATH
FEATURES_PATH = APP_ROOT / config.FEATURES_PATH

st.set_page_config(page_title="OpenHousing Prediction", page_icon="🏠", layout="centered")

st.markdown(
    """
    <style>
        .stMultiSelect [data-testid="stWidgetLabel"] {
            color: #0b6b3f;
            font-weight: 700;
        }
        .stMultiSelect [data-baseweb="select"] {
            background: #f7fff8;
            border: 1px solid #1c8f58;
        }
        .stMultiSelect [role="listbox"] {
            background: #0f7d4a;
            color: #ffffff;
        }
        .stMultiSelect [role="option"] {
            color: #ffffff;
            background: #0f7d4a;
        }
        .stMultiSelect [data-baseweb="tag"] {
            background: #0f7d4a;
            color: #ffffff;
            border: 1px solid #0c693f;
        }
        .stMultiSelect [data-baseweb="tag"] span {
            color: #ffffff;
        }
        .stButton > button {
            background: linear-gradient(135deg, #0f7d4a, #1ea76b);
            color: #ffffff;
            border: none;
            font-weight: 700;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #0c6940, #1b8553);
            color: #ffffff;
        }
        .stInfo, .stWarning, .stSuccess {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("OpenHousing — House Price Predictor")
st.caption("Choose the features you want to edit, then press the prediction button.")

model_available = MODEL_PATH.exists() and FEATURES_PATH.exists()
if not model_available:
    st.warning("The model is not available yet. Run `python -m open_housing_mvp.train` first.")

feature_order = [
    "crim", "zn", "indus", "chas", "nox", "rm", "age",
    "dis", "rad", "tax", "ptratio", "b", "lstat",
]

FEATURE_LABELS = {
    "crim": "Crime Rate",
    "zn": "Residential Zoning",
    "indus": "Industrial Area",
    "chas": "Near Charles River",
    "nox": "Air Pollution",
    "rm": "Average Rooms",
    "age": "Older Homes (%)",
    "dis": "Distance to Employment",
    "rad": "Highway Access",
    "tax": "Property Tax Rate",
    "ptratio": "Student–Teacher Ratio",
    "b": "Neighborhood Demographic Index",
    "lstat": "Lower-Income Population (%)",
}

FEATURE_DESCRIPTIONS = {
    "crim": "Per-capita crime rate in the neighborhood",
    "zn": "Percentage of land zoned for large residential lots",
    "indus": "Percentage of land used for non-retail businesses",
    "chas": "Whether the property borders the Charles River",
    "nox": "Nitrogen oxide concentration (air quality)",
    "rm": "Average number of rooms per home",
    "age": "Percentage of homes built before 1940",
    "dis": "Distance to major employment centers",
    "rad": "Accessibility to major highways",
    "tax": "Local property tax rate",
    "ptratio": "Number of students per teacher in local schools",
    "b": "Historical demographic variable (generally not recommended for end users)",
    "lstat": "Percentage of residents with lower socioeconomic status",
}

if model_available:
    model = joblib.load(MODEL_PATH)
    feature_order = joblib.load(FEATURES_PATH)

feature_defaults = {
    "crim": 0.00632,
    "zn": 18.0,
    "indus": 2.31,
    "chas": 0,
    "nox": 0.538,
    "rm": 6.575,
    "age": 65.2,
    "dis": 4.09,
    "rad": 1,
    "tax": 296,
    "ptratio": 15.3,
    "b": 396.9,
    "lstat": 4.98,
}

selected_features = st.multiselect(
    "Select the variables to use",
    options=feature_order,
    default=feature_order,
    format_func=lambda feature: FEATURE_LABELS.get(feature, feature),
    help="For the MVP, select all variables to run a full prediction with the complete feature set.",
)

if len(selected_features) == 0:
    st.info("Select all variables to enable prediction.")

with st.form("prediction_form"):
    values: dict[str, float | int] = {}
    columns = st.columns(2)

    for idx, feature in enumerate(feature_order):
        col = columns[idx % 2]
        default = feature_defaults.get(feature, 0.0)

        if feature in selected_features:
            label = FEATURE_LABELS.get(feature, feature)
            help_text = FEATURE_DESCRIPTIONS.get(feature, "")

            if feature == "chas":
                values[feature] = col.selectbox(
                    label,
                    options=[0, 1],
                    index=int(default),
                    key=f"input_{feature}",
                    help=help_text,
                )
            else:
                numeric_default = float(default)
                values[feature] = col.number_input(
                    label,
                    value=numeric_default,
                    min_value=0.0,
                    step=0.01,
                    key=f"input_{feature}",
                    help=help_text,
                )

    submitted = st.form_submit_button(
        "Predict price",
        use_container_width=True,
        disabled=not model_available or len(selected_features) == 0,
    )

if submitted and model_available:
    full_values = {feature: feature_defaults.get(feature, 0.0) for feature in feature_order}
    full_values.update(values)

    row = pd.DataFrame([full_values])[feature_order]
    predicted_price = float(model.predict(row)[0])
    st.success(f"Estimated price: ${predicted_price:,.0f} USD")
