import streamlit as st
import openai
import requests
import wikipedia
from typing import Dict

# Streamlit App Configuration
st.set_page_config(page_title="Research Assistant", page_icon="🤖")
st.title("🤖 Research Assistant with OpenAI")

# Sidebar Configuration
st.sidebar.header("Settings")
st.sidebar.write("### OpenAI API Key")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

st.sidebar.write("### GitHub Repository")
st.sidebar.markdown(
    "[View on GitHub](https://github.com/xcaliver2001/document_gpt/blob/main/pages/challenge_day8.py)",
    unsafe_allow_html=True,
)

# Check if API key is provided
if not api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to continue.")
    st.stop()

# Set OpenAI API Key
openai.api_key = api_key

# OpenAI Assistant Function
# Ensure OpenAI library version is pinned to 0.28 to avoid compatibility issues
def openai_assistant(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a research assistant that provides accurate and concise information."},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error while querying OpenAI API: {e}"

# Wikipedia Search Function
def search_wikipedia(query: str) -> str:
    try:
        if not query.strip():
            return "Invalid query: Query is empty."
        summary = wikipedia.summary(query, sentences=5)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"Disambiguation error: {e.options[:5]} (Please specify one of these options)"
    except wikipedia.PageError:
        return "No page found for the given query. Please try a different topic."
    except Exception as e:
        return f"Error while searching Wikipedia: {str(e)}"

# Web Scraper Function
def scrape_website(url: str) -> str:
    try:
        if not url.startswith("http"):
            return "Invalid URL: URL must start with http or https."
        response = requests.get(url)
        response.raise_for_status()
        return response.text[:2000]
    except requests.exceptions.RequestException as e:
        return f"Error while scraping the website: {str(e)}"

# User Input and Execution
query = st.text_input("Enter your research query:")
if st.button("Run Research"):
    if not query.strip():
        st.error("Please enter a valid query.")
    else:
        with st.spinner("Running research..."):
            # Step 1: Use OpenAI Assistant for initial response
            openai_result = openai_assistant(f"Provide a brief overview of: {query}")

            # Step 2: Search Wikipedia
            wiki_result = search_wikipedia(query)

            # Step 3: Combine results
            combined_content = f"OpenAI Assistant Result:\n{openai_result}\n\nWikipedia Result:\n{wiki_result}"
            
            # Step 4: Display Results
            st.subheader("Research Results")
            st.write(combined_content)

            # Optional: Save results to a file
            filename = f"research_{query.replace(' ', '_')}.txt"
            st.download_button(
                "Download Research File",
                data=combined_content,
                file_name=filename,
                mime="text/plain",
            )

# Note for Users
st.sidebar.write("### Important Note")
st.sidebar.info("This application is designed to work with OpenAI Python library version 0.28. Run `pip install openai==0.28` to ensure compatibility.")
