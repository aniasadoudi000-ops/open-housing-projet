from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.environ.get("API_KEY", "")

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
        .stInfo, .stWarning, .stSuccess, .stError {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("OpenHousing — House Price Predictor")
st.caption("Fill in every feature below, then press the prediction button.")
st.caption(f"Calling API at: {API_URL}")

# This app is a pure client of the FastAPI backend — it holds no model file
# and does no prediction itself. Every /predict call goes over HTTP to the
# deployed API, exactly like the architecture diagram: Client -> API.


@st.cache_data(ttl=15)
def check_api_health() -> tuple[bool, str]:
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()
        return data.get("model_loaded", False), data.get("status", "unknown")
    except requests.RequestException as exc:
        return False, f"unreachable ({exc})"


model_available, api_status = check_api_health()
if not model_available:
    st.warning(f"The API is not ready to predict (status: {api_status}).")

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
    values: dict[str, float | int | None] = {}
    columns = st.columns(2)

    for idx, feature in enumerate(feature_order):
        col = columns[idx % 2]

        if feature in selected_features:
            label = FEATURE_LABELS.get(feature, feature)
            help_text = FEATURE_DESCRIPTIONS.get(feature, "")

            if feature == "chas":
                values[feature] = col.selectbox(
                    label,
                    options=[0, 1],
                    index=None,
                    placeholder="Choose 0 or 1",
                    key=f"input_{feature}",
                    help=help_text,
                )
            else:
                values[feature] = col.number_input(
                    label,
                    value=None,
                    min_value=0.0,
                    step=0.01,
                    placeholder="Enter a value",
                    key=f"input_{feature}",
                    help=help_text,
                )

    submitted = st.form_submit_button(
        "Predict price",
        use_container_width=True,
        disabled=len(selected_features) == 0,
    )

if submitted:
    missing = [f for f in selected_features if values.get(f) is None]
    if missing:
        missing_labels = ", ".join(FEATURE_LABELS.get(f, f) for f in missing)
        st.error(f"Please fill in every field before predicting. Missing: {missing_labels}")
    else:
        full_values = {feature: 0.0 for feature in feature_order}
        full_values.update(values)
        payload = {feature: full_values[feature] for feature in feature_order}

        try:
            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                headers={"X-API-Key": API_KEY},
                timeout=10,
            )
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            if response.status_code == 200:
                predicted_price = response.json()["predicted_price"]
                st.success(f"Estimated price: ${predicted_price:,.0f} USD")
            elif response.status_code == 401:
                st.error("API rejected the request: invalid or missing API key (check the API_KEY env var).")
            elif response.status_code == 503:
                st.error("The API's model is not loaded yet.")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
