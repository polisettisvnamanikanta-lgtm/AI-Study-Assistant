
import streamlit as st
from google import genai
import os

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered"
)

MODEL_NAME = "gemini-3.5-flash-lite"

st.title("📚 AI Study Assistant")
st.write("Your personal AI-powered learning companion.")
st.divider()

learning_level = st.selectbox(
    "Choose your learning level",
    ["Beginner", "Intermediate", "Advanced"]
)

question = st.text_area(
    "Enter your question",
    height=130,
    placeholder="What would you like to learn today?"
)

@st.cache_resource
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", None)

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "API key missing. Configure GEMINI_API_KEY."
        )

    return genai.Client(api_key=api_key)


if st.button("Generate Explanation", type="primary"):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:

        prompt = f"""
You are an expert AI Study Assistant.

Student learning level: {learning_level}

Student question:
{question}

Follow these instructions:

1. Use simple and clear English.
2. Explain the topic step by step.
3. Use proper headings.
4. Give practical examples.
5. Explain difficult terms.
6. Include formulas wherever necessary.
7. Highlight important points.
8. Give a short revision summary at the end.

For Beginner:
Start from the basics and explain slowly.

For Intermediate:
Give detailed explanations with examples.

For Advanced:
Give deeper technical explanations and relevant details.

Make the answer accurate, educational and easy to remember.
"""

        try:
            client = get_client()

            with st.spinner("Preparing your explanation..."):

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )

            if response.text:
                st.success("Explanation generated successfully!")
                st.markdown("## 📖 Your Explanation")
                st.markdown(response.text)
            else:
                st.warning("The AI returned an empty response. Try again.")

        except Exception as e:

            error_message = str(e)
            error_lower = error_message.lower()

            if "503" in error_message:
                st.error(
                    "Gemini is temporarily overloaded. "
                    "Please wait and try again."
                )

            elif "429" in error_message:
                st.error(
                    "API quota or rate limit reached. "
                    "Check your Google AI Studio usage."
                )

            elif "404" in error_message:
                st.error(
                    "The selected model is unavailable to your API key. "
                    "Check the model access in Google AI Studio."
                )

            elif "api key" in error_lower or "api_key" in error_lower:
                st.error("Check your Gemini API key configuration.")

            else:
                st.error(f"Unable to generate explanation: {error_message}")

st.divider()

st.caption("AI Study Assistant | Powered by Google Gemini")
