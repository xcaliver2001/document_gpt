import json
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
import streamlit as st
from langchain.retrievers import WikipediaRetriever
from langchain.schema import BaseOutputParser, output_parser

class JsonOutputParser(BaseOutputParser):
    def parse(self, text):
        text = text.replace("```", "").replace("json", "")
        return json.loads(text)

output_parser = JsonOutputParser()

st.set_page_config(
    page_title="QuizGPT",
    page_icon="❓",
)

st.title("QuizGPT")

# Allow the user to set OpenAI API key
with st.sidebar:
    st.markdown("### OpenAI API Key")
    openai_api_key = st.text_input("Enter your OpenAI API key", type="password")
    if openai_api_key:
        llm = ChatOpenAI(
            temperature=0.1,
            model="gpt-3.5-turbo-1106",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=openai_api_key,
        )
    else:
        st.warning("Please enter your OpenAI API key to proceed.")
        st.stop()

# Sidebar link to GitHub repository
st.sidebar.markdown("### Repository")
st.sidebar.markdown(
    "[View on GitHub](https://github.com/your-repo-link)"
)

# Difficulty selection
difficulty = st.sidebar.selectbox("Select difficulty level", ("Easy", "Medium", "Hard"))

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

questions_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a helpful assistant that is role playing as a teacher.
         
    Based ONLY on the following context make 3 (THREE) questions to test the user's knowledge about the text.
    
    Each question should have 4 answers, three of them must be incorrect and one should be correct.
         
    Use (o) to signal the correct answer.
         
    Question examples:
         
    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
         
    Your turn!
         
    Context: {context}
""",
        )
    ]
)

questions_chain = {"context": format_docs} | questions_prompt | llm

formatting_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a powerful formatting algorithm.
     
    You format exam questions into JSON format.
    Answers with (o) are the correct ones.
     
    Example Input:

    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
    
     
    Example Output:
     
    ```json
    {{ "questions": [
            {{
                "question": "What is the color of the ocean?",
                "answers": [
                        {{
                            "answer": "Red",
                            "correct": false
                        }},
                        {{
                            "answer": "Yellow",
                            "correct": false
                        }},
                        {{
                            "answer": "Green",
                            "correct": false
                        }},
                        {{
                            "answer": "Blue",
                            "correct": true
                        }}
                ]
            }},
                        {{
                "question": "What is the capital or Georgia?",
                "answers": [
                        {{
                            "answer": "Baku",
                            "correct": false
                        }},
                        {{
                            "answer": "Tbilisi",
                            "correct": true
                        }},
                        {{
                            "answer": "Manila",
                            "correct": false
                        }},
                        {{
                            "answer": "Beirut",
                            "correct": false
                        }}
                ]
            }},
                        {{
                "question": "When was Avatar released?",
                "answers": [
                        {{
                            "answer": "2007",
                            "correct": false
                        }},
                        {{
                            "answer": "2001",
                            "correct": false
                        }},
                        {{
                            "answer": "2009",
                            "correct": true
                        }},
                        {{
                            "answer": "1998",
                            "correct": false
                        }}
                ]
            }},
            {{
                "question": "Who was Julius Caesar?",
                "answers": [
                        {{
                            "answer": "A Roman Emperor",
                            "correct": true
                        }},
                        {{
                            "answer": "Painter",
                            "correct": false
                        }},
                        {{
                            "answer": "Actor",
                            "correct": false
                        }},
                        {{
                            "answer": "Model",
                            "correct": false
                        }}
                ]
            }}
        ]
     }}
    ```
    Your turn!

    Questions: {context}

""",
        )
    ]
)

formatting_chain = formatting_prompt | llm

@st.cache_data(show_spinner="Loading file...")
def split_file(file):
    file_content = file.read()
    file_path = f"./.cache/quiz_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    return docs

@st.cache_data(show_spinner="Making quiz...")
def run_quiz_chain(_docs, topic):
    chain = {"context": questions_chain} | formatting_chain | output_parser
    return chain.invoke(_docs)

@st.cache_data(show_spinner="Searching Wikipedia...")
def wiki_search(term):
    retriever = WikipediaRetriever(top_k_results=5)
    docs = retriever.get_relevant_documents(term)
    return docs

with st.sidebar:
    docs = None
    topic = None
    choice = st.selectbox(
        "Choose what you want to use.",
        (
            "File",
            "Wikipedia Article",
        ),
    )
    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx , .txt or .pdf file",
            type=["pdf", "txt", "docx"],
        )
        if file:
            docs = split_file(file)
    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            docs = wiki_search(topic)

if not docs:
    st.markdown(
        """
    Welcome to QuizGPT.
                
    I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
                
    Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    response = run_quiz_chain(docs, topic if topic else file.name)
    with st.form("questions_form"):
        st.write("Answer the following questions:")
        user_answers = {}
        score = 0
        for idx, question in enumerate(response["questions"]):
            st.write(question["question"])
            user_answers[idx] = st.radio(
                "Select an option.",
                [answer["answer"] for answer in question["answers"]],
                key=f"question_{idx}",  # Ensure unique key
            )
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            for idx, question in enumerate(response["questions"]):
                selected_answer = user_answers[idx]
                correct_answer = next(
                    (answer["answer"] for answer in question["answers"] if answer["correct"]), None
                )
                if selected_answer == correct_answer:
                    st.success(f"Correct! The answer is: {correct_answer}")
                    score += 1
                else:
                    st.error(f"Wrong! The correct answer was: {correct_answer}")
            if score == len(response["questions"]):
                st.balloons()
                st.success("Congratulations! You got a perfect score!")
            else:
                st.warning(f"You scored {score}/{len(response['questions'])}. Try again!")