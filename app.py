import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun # इंटरनेट सर्च के लिए

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
    # सर्च करने और सटीक रहने के लिए temperature को 0 पर सेट करना बेस्ट है
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key, temperature=0.0)
    search_tool = DuckDuckGoSearchRun() # सर्च टूल चालू किया
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
                # 1. सबसे पहले इंटरनेट से इस सवाल का लाइव रिजल्ट निकालें
                search_result = search_tool.run(user_input)
                
                # 2. मॉडल के लिए एक सख्त गाइडलाइन (System Prompt) बनाएं जिसमें लाइव डेटा हो
                system_prompt = SystemMessage(content=(
                    f"You are a highly accurate AI assistant with live internet access. "
                    f"The user is asking a question. Here is the latest live internet search result for this query:\n"
                    f"--- START SEARCH RESULTS ---\n{search_result}\n--- END SEARCH RESULTS ---\n"
                    f"Use this search data to provide the most up-to-date and factually correct answer. "
                    f"If the user asks about Mersenne Prime, ensure you mention Luke Durant's 2024 discovery based on the data."
                ))
                
                # 3. हिस्ट्री की लिस्ट तैयार करें
                messages_to_send = [system_prompt]
                for msg in st.session_state.chat_history:
                    messages_to_send.append(msg)
                
                # नया सवाल जोड़ें
                new_human_msg = HumanMessage(content=user_input)
                messages_to_send.append(new_human_msg)
                
                # 4. Groq API को लाइव डेटा के साथ भेजें
                response = llm.invoke(messages_to_send)
                st.markdown(response.content)
                
                # हिस्ट्री सेव करें
                st.session_state.chat_history.append(new_human_msg)
                st.session_state.chat_history.append(AIMessage(content=response.content))
                
            except Exception as e:
                st.error(f"Error: {e}")
              
