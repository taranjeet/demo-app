import csv
import queue
import threading
from io import StringIO

import requests
import streamlit as st

from embedchain import App
from embedchain.config import BaseLlmConfig
from embedchain.helpers.callbacks import (StreamingStdOutCallbackHandlerYield,
                                          generate)


@st.cache_resource
def mospi_ai():
    app = App()
    return app


# Function to read the CSV file row by row
def read_csv_row_by_row(file_path):
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            yield row


@st.cache_resource
def add_data_to_app():
    app = mospi_ai()
    url = "https://gist.githubusercontent.com/taranjeet/3722cba958f0c0934b18c5e8075ee0e7/raw/791f53ecfd6da035db2aec6a6e705dac4ce42eb2/d1.csv"  # noqa:E501
    response = requests.get(url)
    csv_file = StringIO(response.text)
    for row in csv.reader(csv_file):  
      app.add(row[0], data_type="pdf_file")


app = mospi_ai()
add_data_to_app()

assistant_avatar_url = "data:image/png;base64,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"  # noqa: E501


st.title("🙏 MOSPI AI")

styled_caption = '<p style="font-size: 17px; color: #aaa;">🚀 An <a href="https://github.com/embedchain/embedchain">Embedchain</a> app powered with MOSPI\'s wisdom!</p>'  # noqa: E501
st.markdown(styled_caption, unsafe_allow_html=True)  # noqa: E501

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
                Hi, I'm MOSPI AI
            """,  # noqa: E501
        }
    ]

for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar=assistant_avatar_url if role == "assistant" else None):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=assistant_avatar_url):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""

        q = queue.Queue()

        def app_response(result):
            config = BaseLlmConfig(stream=True, callbacks=[StreamingStdOutCallbackHandlerYield(q)])
            answer, citations = app.chat(prompt, config=config, citations=True)
            result["answer"] = answer
            result["citations"] = citations

        results = {}
        thread = threading.Thread(target=app_response, args=(results,))
        thread.start()

        for answer_chunk in generate(q):
            full_response += answer_chunk
            msg_placeholder.markdown(full_response)

        thread.join()
        answer, citations = results["answer"], results["citations"]
        if citations:
            full_response += "\n\n**Sources**:\n"
            for i, citations in enumerate(citations):
                full_response += f"{i+1}. {citations[1]}\n"

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
