import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from duckduckgo_search import DDGS # यह नया और बिल्कुल सही तरीका है

st.set_page_config(page_title="Mera ChatGPT Live", page_icon="🤖")
st.title("🤖 Mera ChatGPT (With Live Internet)")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Galti: Streamlit Secrets me GROQ_API_KEY nahi mili!")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

try:
    # Llama 3.3 मॉडल एकदम सही से काम करेगा
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key, temperature=0.2)
except Exception as e:
    st.error(f"Model initiate nahi hua: {e}")
    st.stop()

# पुरानी चैट स्क्रीन पर दिखाना
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

user_input = st.chat_input("Pucho kuch bhi...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Internet par check kiya ja raha hai aur AI soch raha hai..."):
            try:
                # लाइव इंटरनेट सर्च करने का सबसे लेटेस्ट तरीका
                with DDGS() as ddgs:
                    search_results = [r for r in ddgs.text(user_input, max_results=3)]
                
                # सर्च रिजल्ट्स को टेक्स्ट में बदलना
                search_text = ""
                for res in search_results:
                    search_text += f"Title: {res['title']}\nSnippet: {res['body']}\n\n"
                
                # मॉडल के लिए गाइडलाइन प्रॉम्ट
                system_prompt = SystemMessage(content=(
                    f"You are an up-to-date and highly accurate AI assistant with live internet access. "
                    f"The user is asking a question. Here is the latest live internet search data for this query:\n"
                    f"--- START SEARCH DATA ---\n{search_text}\n--- END SEARCH DATA ---\n"
                    f"Use this live information to provide the most correct and latest answer. Always prioritize these live results for recent events or facts."
                ))
                
                # चैट हिस्ट्री और सिस्टम प्रॉम्ट को कंबाइन करना
                messages_to_send = [system_prompt]
                for msg in st.session_state.chat_history:
                    messages_to_send.append(msg)
                
                new_human_msg = HumanMessage(content=user_input)
                messages_to_send.append(new_human_msg)
                
                # Groq को रिक्वेस्ट भेजना
                response = llm.invoke(messages_to_send)
                st.markdown(response.content)
                
                # चैट收藏 हिस्ट्री सेव करना
                st.session_state.chat_history.append(new_human_msg)
                st.session_state.chat_history.append(AIMessage(content=response.content))
                
            except Exception as e:
                st.error(f"Error: {e}")
                
