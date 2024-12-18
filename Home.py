import streamlit as st

from datetime import datetime

today = datetime.today().strftime('%H:%M:%S')

st.set_page_config(
    page_title="FullstackGPT Home",
    page_icon="🤖",
)

st.title(today)

st.markdown(
    """
# Hello!
            
Welcome to my FullstackGPT Portfolio!
            
Here are the apps I made:
            
- [ ] [DocumentGPT](/DocumentGPT)
- [ ] [PrivateGPT](/PrivateGPT)
- [ ] [QuizGPT](/QuizGPT)
- [ ] [SiteGPT](/SiteGPT)
- [ ] [MeetingGPT](/MeetingGPT)
- [ ] [InvestorGPT](/InvestorGPT)
"""
)

st.title("title")
with st.sidebar :
    st.title("sidebar")
    st.text_input("text" )

tab_one, tab_two, tab_three = st.tabs(["A", "B", "C"])

with tab_one:
    st.write("A")

with tab_two:
    st.write("B")

with tab_three:
    st.write("C")

inputs = st.selectbox("select", ["A", "B", "C"])

if inputs == "A":
    st.write("A is selected")
elif inputs == "B":
    st.write("B is selected")
else:
    st.write("C is selected")

st.multiselect("multiselect", ["A", "B", "C"])

st.slider("slider", 0, 100, 50)

st.select_slider("select_slider", options=["A", "B", "C"])  