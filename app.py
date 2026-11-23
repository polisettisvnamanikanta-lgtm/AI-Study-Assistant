
import streamlit as st
from google import genai
from pypdf import PdfReader
import os

st.set_page_config(page_title="AI Study Assistant",page_icon="📚",layout="centered")

MODEL_NAME = "gemini-3.5-flash-lite"

st.title("📚 AI Study Assistant")
st.write("Your personal AI-powered learning companion.")

learning_level = st.selectbox("Choose your learning level",["Beginner","Intermediate","Advanced"])

@st.cache_resource
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY",None)
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key missing. Configure GEMINI_API_KEY.")
    return genai.Client(api_key=api_key)

def generate_answer(prompt):
    client = get_client()
    return client.models.generate_content(model=MODEL_NAME,contents=prompt)

st.divider()
st.header("💬 1. Normal AI Learning")

question = st.text_area("Ask any question",height=120,placeholder="What would you like to learn today?")

if st.button("Generate Explanation",type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        prompt = f"""
You are an expert AI Study Assistant.

Student learning level: {learning_level}

Question: {question}

Explain using simple English.
Explain step by step.
Use proper headings and practical examples.
Explain difficult terms.
Include formulas wherever necessary.
Give a short revision summary at the end.
"""
        try:
            with st.spinner("Preparing your explanation..."):
                response = generate_answer(prompt)
            if response.text:
                st.subheader("📖 Your Explanation")
                st.markdown(response.text)
            else:
                st.warning("The AI returned an empty response.")
        except Exception as e:
            if "503" in str(e):
                st.error("Gemini is temporarily overloaded. Please try again.")
            elif "429" in str(e):
                st.error("API quota or rate limit reached.")
            else:
                st.error(f"Unable to generate explanation: {e}")

st.divider()
st.header("📄 2. Learn from PDF")

uploaded_file = st.file_uploader("Upload your PDF",type=["pdf"],key="pdf_upload")

pdf_text = ""

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text + "\n"
        st.success("PDF uploaded successfully!")
        st.write("Number of pages:",len(reader.pages))
    except Exception as e:
        st.error(f"Unable to read PDF: {e}")


if uploaded_file is not None and pdf_text.strip():
    if st.button("📝 Summarize PDF"):
        prompt = f"""
You are an expert study assistant.

Summarize the following PDF for a student.

Use simple English and include:
1. Main topic and purpose
2. Important concepts
3. Key points with headings
4. Important formulas and definitions
5. Short revision notes

Make the summary easy to understand and remember.

PDF CONTENT:
{pdf_text}
"""
        try:
            with st.spinner("Preparing your PDF summary..."):
                response = generate_answer(prompt)
            if response.text:
                st.subheader("📚 PDF Summary")
                st.markdown(response.text)
            else:
                st.warning("The AI returned an empty response.")
        except Exception as e:
            st.error(f"Unable to summarize PDF: {e}")


pdf_question = st.text_area("Ask a question about your PDF",height=100,placeholder="Ask something from your uploaded PDF...")

if st.button("Ask AI About PDF"):
    if uploaded_file is None:
        st.warning("Please upload a PDF first.")
    elif not pdf_text.strip():
        st.warning("No readable text found in this PDF.")
    elif not pdf_question.strip():
        st.warning("Please enter a question.")
    else:
        prompt = f"""
You are an expert AI Study Assistant.

Student learning level: {learning_level}

Answer the question using the PDF content below.
Use simple English and explain step by step.
If the answer is not available in the PDF, clearly say so.

PDF CONTENT:
{pdf_text}

STUDENT QUESTION:
{pdf_question}
"""
        try:
            with st.spinner("Finding your answer..."):
                response = generate_answer(prompt)
            if response.text:
                st.subheader("📖 Answer from PDF")
                st.markdown(response.text)
            else:
                st.warning("The AI returned an empty response.")
        except Exception as e:
            if "503" in str(e):
                st.error("Gemini is temporarily overloaded. Please try again.")
            elif "429" in str(e):
                st.error("API quota or rate limit reached.")
            else:
                st.error(f"Unable to generate answer: {e}")

st.divider()


st.divider()
st.header("🧠 3. AI Quiz Generator")

quiz_source = st.radio(
    "Choose quiz source",
    ["Normal Topic", "Uploaded PDF"],
    horizontal=True
)

num_questions = st.selectbox(
    "Number of questions",
    [5, 10, 15]
)

if quiz_source == "Normal Topic":
    quiz_topic = st.text_input(
        "Enter quiz topic",
        placeholder="Example: Digital Electronics"
    )
else:
    quiz_topic = ""

if st.button("Generate Quiz",type="primary"):
    if quiz_source == "Normal Topic" and not quiz_topic.strip():
        st.warning("Please enter a topic.")

    elif quiz_source == "Uploaded PDF" and not pdf_text.strip():
        st.warning("Please upload a readable PDF in the PDF section first.")

    else:
        if quiz_source == "Normal Topic":
            source_content = quiz_topic
            source_instruction = "Create questions about this topic."
        else:
            source_content = pdf_text
            source_instruction = "Create questions using the PDF content."

        quiz_prompt = f"""
You are an expert quiz creator.

{source_instruction}

Create exactly {num_questions} multiple-choice questions.

Student learning level: {learning_level}

Return ONLY valid JSON in this exact format:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option one",
        "B": "Option two",
        "C": "Option three",
        "D": "Option four"
      }},
      "answer": "A",
      "explanation": "Explain why this answer is correct."
    }}
  ]
}}

Make sure:
- Every question has four options.
- Only one option is correct.
- The correct answer is represented by A, B, C, or D.
- Questions are accurate and educational.

CONTENT:
{source_content}
"""

        try:
            import json

            with st.spinner("Generating your quiz..."):
                response = generate_answer(quiz_prompt)

            quiz_data = json.loads(response.text.strip().replace("```json", "").replace("```", "").strip())

            if len(quiz_data["questions"]) != num_questions:
                st.warning("The AI generated an unexpected number of questions. Please try again.")
            else:
                st.session_state.quiz_data = quiz_data
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False

        except Exception as e:
            st.error(f"Unable to generate quiz: {e}")

if "quiz_data" in st.session_state:
    st.subheader("📝 Your Quiz")

    for i, q in enumerate(st.session_state.quiz_data["questions"]):
        st.markdown(f"**Q{i+1}. {q['question']}**")

        selected = st.radio(
            f"Choose your answer for question {i+1}",
            ["Not answered", "A", "B", "C", "D"],
            format_func=lambda x, options=q["options"]: (
                "Select an answer" if x == "Not answered"
                else f"{x}. {options[x]}"
            ),
            key=f"quiz_answer_{i}"
        )

        st.session_state.quiz_answers[i] = selected

    if st.button("Submit Quiz"):
        st.session_state.quiz_submitted = True

    if st.session_state.get("quiz_submitted", False):
        score = 0

        for i, q in enumerate(st.session_state.quiz_data["questions"]):
            correct = q["answer"].strip().upper()
            selected = st.session_state.quiz_answers.get(i, "Not answered")

            if selected == correct:
                score += 1
                st.success(f"Question {i+1}: Correct!")
            else:
                st.error(f"Question {i+1}: Incorrect. Correct answer: {correct}")

            st.write("Explanation:", q["explanation"])

        st.divider()
        st.subheader(f"🏆 Your Score: {score}/{len(st.session_state.quiz_data['questions'])}")

        if st.button("Generate New Quiz"):
            del st.session_state.quiz_data
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

st.caption("AI Study Assistant | Powered by Google Gemini")
