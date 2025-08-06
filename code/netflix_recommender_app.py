import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# Optional: OpenAI (only if needed for GPT)
import openai
#openai.api_key = st.secrets["openai"]["api_key"]  # store in .streamlit/secrets.toml
#openai.api_key = st.secrets["openai"]["api_key"]
openai.api_key = st.secrets["openai"]["api_key"]

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("gap_df_with_clusters.csv")

df = load_data()

st.title("🎬 Netflix Content Investment Recommender")

# --- Sidebar: Chatbot Mode ---
st.sidebar.markdown("## 🤖 Ask the Recommender")
user_question = st.sidebar.text_input("Ask something like: What’s underrepresented in Japan?")

if user_question:
    country_names = df['country'].dropna().unique()
    matched_country, score = process.extractOne(user_question, country_names)

    if score > 60:
        top_gaps = df[df['country'] == matched_country].sort_values(by='gap').head(3)
        genres = top_gaps['listed_in'].tolist()
        response = f"📍 In **{matched_country}**, the top underrepresented genres are: {', '.join(genres)}"
    else:
        response = "❌ Sorry, I couldn't find a matching country. Please try again."

    st.sidebar.success(response)

# --- Main Filter Mode (original app) ---
st.subheader("📈 Browse by Country / Cluster")
region_input = st.text_input("Filter by Country Name")
cluster_input = st.selectbox("Filter by Cluster", sorted(df['Cluster'].dropna().unique()))

filtered_df = df.copy()
if region_input:
    filtered_df = filtered_df[filtered_df['country'].str.contains(region_input, case=False, na=False)]
if cluster_input is not None:
    filtered_df = filtered_df[filtered_df['Cluster'] == cluster_input]

top_recommendations = (
    filtered_df.sort_values(by='gap')
    .groupby('country')
    .head(3)
    .groupby('country')['listed_in']
    .apply(list)
    .reset_index()
)
st.dataframe(top_recommendations)

st.download_button("📥 Download CSV", top_recommendations.to_csv(index=False), "recommendations.csv")
