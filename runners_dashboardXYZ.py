import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Running Events Dashboard",
    page_icon="🏃",
    layout="wide",
)

DATA_PATH = Path(__file__).with_name("data2.csv")

NUMERIC_COLS = [
    "Year of event",
    "Event number of finishers",
    "Event distance (km)",
    "Performance_seconds",
    "Events count",
    "age",
    "Event month",
]

CATEGORICAL_COLS = [
    "Athlete gender",
    "Club category",
    "Event season",
    "Event continent",
    "Athlete continent",
    "Same country",
    "Event country",
    "Athlete country",
    "Event name",
]

SCATTER_X_OPTIONS = [
    "Event distance (km)",
    "Performance_hours",
    "Performance_minutes",
    "Performance_seconds",
    "age",
    "Event number of finishers",
    "Events count",
    "Year of event",
    "Event month",
]

SCATTER_Y_OPTIONS = [
    "Performance_hours",
    "Performance_minutes",
    "Performance_seconds",
    "Event distance (km)",
    "age",
    "Event number of finishers",
    "Events count",
    "Year of event",
    "Event month",
]

BOXPLOT_X_OPTIONS = [
    "Athlete gender",
    "Club category",
    "Event season",
    "Event continent",
    "Athlete continent",
    "Same country",
    "Event country",
    "Athlete country",
    "Event name",
]

BOXPLOT_Y_OPTIONS = [
    "Performance_hours",
    "Performance_minutes",
    "Performance_seconds",
    "Event distance (km)",
    "age",
    "Event number of finishers",
    "Events count",
    "Year of event",
    "Event month",
]

SCATTER_COLOR_OPTIONS = [
    "Athlete gender",
    "Club category",
    "Event season",
    "Event continent",
    "Athlete continent",
    "Same country",
    None,
]

COLUMN_LABELS = {
    "Year of event": "שנת אירוע",
    "Event name": "שם אירוע",
    "Event number of finishers": "מספר מסיימים",
    "Athlete country": "מדינת הספורטאי",
    "Athlete gender": "מגדר",
    "Event distance (km)": 'מרחק (ק"מ)',
    "Performance_seconds": "זמן ביצוע (שניות)",
    "Performance_minutes": "זמן ביצוע (דקות)",
    "Performance_hours": "זמן ביצוע (שעות)",
    "Club category": "קטגוריית מועדון",
    "Events count": "מספר אירועים",
    "age": "גיל",
    "Event country": "מדינת האירוע",
    "Event continent": "יבשת האירוע",
    "Athlete continent": "יבשת הספורטאי",
    "Same country": "אותה מדינה",
    "Event month": "חודש האירוע",
    "Event season": "עונת האירוע",
}


@st.cache_data(show_spinner=True)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("string")

    if "Same country" in df.columns:
        df["Same country"] = df["Same country"].astype("string")

    df["Performance_hours"] = df["Performance_seconds"] / 3600.0
    df["Performance_minutes"] = df["Performance_seconds"] / 60.0
    return df


@st.cache_data(show_spinner=False)
def filter_data(
    df: pd.DataFrame,
    year_range: tuple[int, int],
    distance_range: tuple[float, float],
    age_range: tuple[float, float],
    genders: list[str],
    seasons: list[str],
    club_categories: list[str],
    event_continents: list[str],
    athlete_continents: list[str],
    same_country_values: list[str],
    max_finishers: int,
) -> pd.DataFrame:
    filtered = df.copy()

    filtered = filtered[
        filtered["Year of event"].between(year_range[0], year_range[1], inclusive="both")
    ]
    filtered = filtered[
        filtered["Event distance (km)"].between(distance_range[0], distance_range[1], inclusive="both")
    ]
    filtered = filtered[
        filtered["age"].between(age_range[0], age_range[1], inclusive="both")
    ]
    filtered = filtered[filtered["Event number of finishers"] <= max_finishers]

    if genders:
        filtered = filtered[filtered["Athlete gender"].isin(genders)]
    if seasons:
        filtered = filtered[filtered["Event season"].isin(seasons)]
    if club_categories:
        filtered = filtered[filtered["Club category"].isin(club_categories)]
    if event_continents:
        filtered = filtered[filtered["Event continent"].isin(event_continents)]
    if athlete_continents:
        filtered = filtered[filtered["Athlete continent"].isin(athlete_continents)]
    if same_country_values:
        filtered = filtered[filtered["Same country"].isin(same_country_values)]

    return filtered


@st.cache_data(show_spinner=False)
def sample_for_scatter(df: pd.DataFrame, sample_size: int, seed: int = 42) -> pd.DataFrame:
    if len(df) <= sample_size:
        return df.copy()
    return df.sample(n=sample_size, random_state=seed)


@st.cache_data(show_spinner=False)
def grouped_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = (
        df.groupby(group_col, dropna=False)
        .agg(
            runners=("Performance_seconds", "size"),
            avg_performance_hours=("Performance_hours", "mean"),
            median_performance_hours=("Performance_hours", "median"),
            avg_distance_km=("Event distance (km)", "mean"),
            avg_age=("age", "mean"),
        )
        .reset_index()
        .sort_values("runners", ascending=False)
    )
    return summary


@st.cache_data(show_spinner=False)
def format_seconds(seconds: float) -> str:
    if pd.isna(seconds):
        return "—"
    seconds = float(seconds)
    days = int(seconds // 86400)
    seconds %= 86400
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    if days > 0:
        return f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@st.cache_data(show_spinner=False)
def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "rows": int(len(df)),
        "avg_time": format_seconds(df["Performance_seconds"].mean()),
        "median_time": format_seconds(df["Performance_seconds"].median()),
        "avg_distance": float(df["Event distance (km)"].mean()),
        "avg_age": float(df["age"].mean()),
        "countries": int(df["Event country"].nunique()),
        "events": int(df["Event name"].nunique()),
    }


st.title("🏃 Running Events Dashboard")
st.caption("דשבורד אינטראקטיבי לניתוח רצים, מרחקים, זמנים, גילאים ומרוצים.")

if not DATA_PATH.exists():
    st.error(f"לא נמצא קובץ נתונים בנתיב: {DATA_PATH}")
    st.stop()

df = load_data(str(DATA_PATH))

with st.sidebar:
    st.header("סינון נתונים")

    min_year = int(df["Year of event"].min())
    max_year = int(df["Year of event"].max())
    year_range = st.slider("שנות אירוע", min_year, max_year, (min_year, max_year))

    min_distance = float(df["Event distance (km)"].min())
    max_distance = float(df["Event distance (km)"].max())
    distance_range = st.slider(
        "טווח מרחק (ק\"מ)",
        min_value=float(math.floor(min_distance)),
        max_value=float(math.ceil(max_distance)),
        value=(float(math.floor(min_distance)), float(math.ceil(max_distance))),
    )

    min_age = int(df["age"].min())
    max_age = int(df["age"].max())
    age_range = st.slider("טווח גיל", min_age, max_age, (min_age, max_age))

    genders = st.multiselect(
        "מגדר", sorted(df["Athlete gender"].dropna().unique().tolist()), default=sorted(df["Athlete gender"].dropna().unique().tolist())
    )
    seasons = st.multiselect(
        "עונה", sorted(df["Event season"].dropna().unique().tolist()), default=sorted(df["Event season"].dropna().unique().tolist())
    )
    club_categories = st.multiselect(
        "סוג מועדון", sorted(df["Club category"].dropna().unique().tolist()), default=sorted(df["Club category"].dropna().unique().tolist())
    )
    event_continents = st.multiselect(
        "יבשת האירוע",
        sorted(df["Event continent"].dropna().unique().tolist()),
        default=sorted(df["Event continent"].dropna().unique().tolist()),
    )
    athlete_continents = st.multiselect(
        "יבשת הספורטאי",
        sorted(df["Athlete continent"].dropna().unique().tolist()),
        default=sorted(df["Athlete continent"].dropna().unique().tolist()),
    )
    same_country_values = st.multiselect(
        "אותה מדינה לספורטאי ולאירוע",
        sorted(df["Same country"].dropna().unique().tolist()),
        default=sorted(df["Same country"].dropna().unique().tolist()),
    )

    max_finishers_default = int(df["Event number of finishers"].quantile(0.99))
    max_finishers = st.slider(
        "מספר מסיימים מרבי באירוע",
        min_value=int(df["Event number of finishers"].min()),
        max_value=int(df["Event number of finishers"].max()),
        value=max_finishers_default,
    )

    st.subheader("גרף פיזור")
    sample_size = st.slider("גודל דגימה לגרף פיזור", 5000, 200000, 50000, step=5000)
    scatter_x_col = st.selectbox(
        "פיזור - ציר X",
        SCATTER_X_OPTIONS,
        index=0,
        format_func=lambda c: COLUMN_LABELS.get(c, c),
    )
    scatter_y_col = st.selectbox(
        "פיזור - ציר Y",
        SCATTER_Y_OPTIONS,
        index=0,
        format_func=lambda c: COLUMN_LABELS.get(c, c),
    )
    scatter_color = st.selectbox(
        "צביעת גרף פיזור לפי",
        ["ללא צבע"] + [c for c in SCATTER_COLOR_OPTIONS if c is not None],
        index=1,
        format_func=lambda c: "ללא צבע" if c == "ללא צבע" else COLUMN_LABELS.get(c, c),
    )
    scatter_color = None if scatter_color == "ללא צבע" else scatter_color

    st.subheader("בוקספלוט")
    box_x_col = st.selectbox(
        "בוקספלוט - ציר X",
        BOXPLOT_X_OPTIONS,
        index=0,
        format_func=lambda c: COLUMN_LABELS.get(c, c),
    )
    box_y_col = st.selectbox(
        "בוקספלוט - ציר Y",
        BOXPLOT_Y_OPTIONS,
        index=0,
        format_func=lambda c: COLUMN_LABELS.get(c, c),
    )

filtered_df = filter_data(
    df,
    year_range,
    distance_range,
    age_range,
    genders,
    seasons,
    club_categories,
    event_continents,
    athlete_continents,
    same_country_values,
    max_finishers,
)

if filtered_df.empty:
    st.warning("לא נמצאו נתונים אחרי הסינון. נסה להרחיב את הפילטרים.")
    st.stop()

kpis = compute_kpis(filtered_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("מספר רשומות", f"{kpis['rows']:,}")
c2.metric("זמן ממוצע", kpis["avg_time"])
c3.metric("חציון זמן", kpis["median_time"])
c4.metric("מרחק ממוצע", f"{kpis['avg_distance']:.1f} ק\"מ")
c5.metric("גיל ממוצע", f"{kpis['avg_age']:.1f}")
c6.metric("מספר אירועים", f"{kpis['events']:,}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "סקירה כללית",
    "פיזור ובוקספלוט",
    "השוואות וטרנדים",
    "טבלת סיכום",
])

with tab1:
    left, right = st.columns(2)

    with left:
        by_season = grouped_summary(filtered_df, "Event season")
        fig = px.bar(
            by_season,
            x="Event season",
            y="runners",
            text_auto=True,
            title="כמות רצים לפי עונה",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        by_gender = grouped_summary(filtered_df, "Athlete gender")
        fig = px.bar(
            by_gender,
            x="Athlete gender",
            y="median_performance_hours",
            text_auto=".2f",
            title="חציון זמן ביצוע לפי מגדר (שעות)",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:
        fig = px.histogram(
            filtered_df,
            x="age",
            nbins=30,
            title="התפלגות גילאים",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with bottom_right:
        top_countries = (
            filtered_df["Event country"].value_counts(dropna=True).head(15).reset_index()
        )
        top_countries.columns = ["Event country", "Count"]
        fig = px.bar(
            top_countries,
            x="Count",
            y="Event country",
            orientation="h",
            title="15 המדינות המובילות במספר רשומות אירוע",
        )
        fig.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    scatter_df = sample_for_scatter(filtered_df.dropna(subset=[scatter_x_col, scatter_y_col]), sample_size)
    st.caption(
        f"גרף הפיזור מוצג על דגימה של {len(scatter_df):,} רשומות מתוך {len(filtered_df):,} לשיפור ביצועים."
    )

    fig_scatter = px.scatter(
        scatter_df,
        x=scatter_x_col,
        y=scatter_y_col,
        color=scatter_color,
        hover_data=[
            "Event name",
            "Athlete gender",
            "age",
            "Event season",
            "Event country",
        ],
        title=f"גרף פיזור: {COLUMN_LABELS.get(scatter_x_col, scatter_x_col)} מול {COLUMN_LABELS.get(scatter_y_col, scatter_y_col)}",
        opacity=0.5,
    )
    fig_scatter.update_layout(
        height=560,
        xaxis_title=COLUMN_LABELS.get(scatter_x_col, scatter_x_col),
        yaxis_title=COLUMN_LABELS.get(scatter_y_col, scatter_y_col),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    boxplot_df = filtered_df.dropna(subset=[box_x_col, box_y_col]).copy()
    if box_x_col == "Event name":
        top_event_names = boxplot_df[box_x_col].value_counts().head(20).index
        boxplot_df = boxplot_df[boxplot_df[box_x_col].isin(top_event_names)]
        st.caption("כאשר בוחרים 'שם אירוע' בציר X מוצגים רק 20 האירועים עם הכי הרבה רשומות כדי לשמור על קריאות הגרף.")

    fig_box = px.box(
        boxplot_df,
        x=box_x_col,
        y=box_y_col,
        points=False,
        title=f"בוקספלוט: {COLUMN_LABELS.get(box_y_col, box_y_col)} לפי {COLUMN_LABELS.get(box_x_col, box_x_col)}",
    )
    fig_box.update_layout(
        height=560,
        xaxis_title=COLUMN_LABELS.get(box_x_col, box_x_col),
        yaxis_title=COLUMN_LABELS.get(box_y_col, box_y_col),
    )
    st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    left, right = st.columns(2)

    with left:
        by_year = (
            filtered_df.groupby("Year of event")
            .agg(
                avg_performance_hours=("Performance_hours", "mean"),
                median_performance_hours=("Performance_hours", "median"),
                avg_distance=("Event distance (km)", "mean"),
                runners=("Performance_hours", "size"),
            )
            .reset_index()
            .sort_values("Year of event")
        )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=by_year["Year of event"],
                y=by_year["avg_performance_hours"],
                mode="lines+markers",
                name="זמן ממוצע (שעות)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=by_year["Year of event"],
                y=by_year["median_performance_hours"],
                mode="lines+markers",
                name="חציון זמן (שעות)",
            )
        )
        fig.update_layout(height=450, title="טרנד ביצועים לאורך השנים", xaxis_title="שנה", yaxis_title="שעות")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.scatter(
            sample_for_scatter(filtered_df.dropna(subset=["age"]), min(sample_size, 80000)),
            x="age",
            y="Performance_hours",
            color="Athlete gender" if "Athlete gender" in filtered_df.columns else None,
            trendline="ols",
            title="גיל מול זמן ביצוע",
            opacity=0.45,
        )
        fig.update_layout(height=450, xaxis_title="גיל", yaxis_title="זמן (שעות)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("השוואת קבוצות")
    compare_col = st.selectbox(
        "בחר עמודה להשוואה",
        ["Club category", "Event continent", "Athlete continent", "Event season", "Athlete gender"],
        index=0,
        key="compare_col",
        format_func=lambda c: COLUMN_LABELS.get(c, c),
    )
    compare_df = grouped_summary(filtered_df, compare_col).head(20)
    fig = px.bar(
        compare_df,
        x=compare_col,
        y=["avg_performance_hours", "avg_distance_km", "avg_age"],
        barmode="group",
        title=f"השוואה בין קבוצות לפי {COLUMN_LABELS.get(compare_col, compare_col)}",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("טבלת סיכום לפי חלוקה")
    summary_group = st.selectbox(
        "בחר עמודת קיבוץ",
        ["Athlete gender", "Club category", "Event season", "Event continent", "Athlete continent", "Event country"],
        index=0,
        key="summary_group",
        format_func=lambda c: COLUMN_LABELS.get(c, c),
    )
    summary_df = grouped_summary(filtered_df, summary_group)
    summary_df = summary_df.rename(
        columns={
            summary_group: "Group",
            "runners": "Rows",
            "avg_performance_hours": "Avg performance (hours)",
            "median_performance_hours": "Median performance (hours)",
            "avg_distance_km": "Avg distance (km)",
            "avg_age": "Avg age",
        }
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    csv_data = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="הורד טבלת סיכום כ-CSV",
        data=csv_data,
        file_name="dashboard_summary.csv",
        mime="text/csv",
    )
