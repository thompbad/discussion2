import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Athens Airbnb Dashboard",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("listing (1).csv")

    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    df = df.dropna(subset=["price", "room_type", "neighbourhood_cleansed"])
    df = df[(df["price"] > 0) & (df["price"] <= 500)]

    return df

df = load_data()

st.title("Inside Airbnb Athens Dashboard")
st.write(
    "This dashboard explores Airbnb listings in Athens by room type, neighborhood, "
    "price, availability, and review activity."
)

st.sidebar.header("Filters")

room_options = sorted(df["room_type"].dropna().unique())
selected_rooms = st.sidebar.multiselect(
    "Select room type",
    room_options,
    default=room_options
)

price_range = st.sidebar.slider(
    "Select price range",
    int(df["price"].min()),
    int(df["price"].max()),
    (int(df["price"].min()), 250)
)

neighborhood_options = sorted(df["neighbourhood_cleansed"].dropna().unique())
selected_neighborhoods = st.sidebar.multiselect(
    "Select neighborhoods",
    neighborhood_options,
    default=neighborhood_options[:10]
)

filtered = df[
    (df["room_type"].isin(selected_rooms)) &
    (df["price"] >= price_range[0]) &
    (df["price"] <= price_range[1]) &
    (df["neighbourhood_cleansed"].isin(selected_neighborhoods))
]

st.subheader("Filtered Dataset Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Listings", f"{len(filtered):,}")
col2.metric("Average Price", f"€{filtered['price'].mean():.2f}")
col3.metric("Median Price", f"€{filtered['price'].median():.2f}")

st.divider()

# Chart 1: Average price by room type
avg_price = (
    filtered.groupby("room_type", as_index=False)["price"]
    .mean()
    .sort_values("price", ascending=False)
)

price_chart = alt.Chart(avg_price).mark_bar().encode(
    x=alt.X("price:Q", title="Average Price (€)"),
    y=alt.Y("room_type:N", sort="-x", title="Room Type"),
    tooltip=["room_type", alt.Tooltip("price:Q", format=".2f")]
).properties(
    title="Average Price by Room Type",
    height=300
)

# Chart 2: Listings by neighborhood
neighborhood_counts = (
    filtered.groupby("neighbourhood_cleansed", as_index=False)
    .size()
    .rename(columns={"size": "listing_count"})
    .sort_values("listing_count", ascending=False)
    .head(15)
)

neighborhood_chart = alt.Chart(neighborhood_counts).mark_bar().encode(
    x=alt.X("listing_count:Q", title="Number of Listings"),
    y=alt.Y("neighbourhood_cleansed:N", sort="-x", title="Neighborhood"),
    tooltip=["neighbourhood_cleansed", "listing_count"]
).properties(
    title="Top Neighborhoods by Listing Count",
    height=400
)

left, right = st.columns(2)
with left:
    st.altair_chart(price_chart, use_container_width=True)
with right:
    st.altair_chart(neighborhood_chart, use_container_width=True)

st.divider()

# Chart 3: Price vs availability
scatter = alt.Chart(filtered).mark_circle(size=60, opacity=0.5).encode(
    x=alt.X("availability_365:Q", title="Availability in the Next 365 Days"),
    y=alt.Y("price:Q", title="Price (€)"),
    color=alt.Color("room_type:N", title="Room Type"),
    tooltip=[
        "name",
        "room_type",
        "neighbourhood_cleansed",
        alt.Tooltip("price:Q", format=".2f"),
        "availability_365",
        "number_of_reviews"
    ]
).interactive().properties(
    title="Price Compared with Yearly Availability",
    height=450
)

st.altair_chart(scatter, use_container_width=True)

st.divider()

# Chart 4: Reviews by room type
if "number_of_reviews" in filtered.columns:
    reviews = (
        filtered.groupby("room_type", as_index=False)["number_of_reviews"]
        .mean()
        .sort_values("number_of_reviews", ascending=False)
    )

    review_chart = alt.Chart(reviews).mark_bar().encode(
        x=alt.X("number_of_reviews:Q", title="Average Number of Reviews"),
        y=alt.Y("room_type:N", sort="-x", title="Room Type"),
        tooltip=["room_type", alt.Tooltip("number_of_reviews:Q", format=".2f")]
    ).properties(
        title="Average Reviews by Room Type",
        height=300
    )

    st.altair_chart(review_chart, use_container_width=True)

st.subheader("Filtered Data Preview")
st.dataframe(filtered[
    [
        "name",
        "neighbourhood_cleansed",
        "room_type",
        "price",
        "availability_365",
        "number_of_reviews"
    ]
].head(100))