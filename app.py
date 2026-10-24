
import random
import html
import streamlit as st
import pandas as pd
import plotly.express as px

from questions import QUESTIONS
from evaluator import evaluate_answer
from database import setup_database, save_attempt, get_attempts


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="InterviewIQ",
    page_icon="🎯",
    layout="wide"
)

setup_database()


# ---------------- SESSION STATE ----------------

DEFAULTS = {
    "page": "Dashboard",
    "selected_subject": "Python",
    "subject": "Python",
    "level": "Beginner",
    "session_questions": [],
    "question_index": 0,
    "evaluated": False,
    "evaluation_result": None,
    "evaluated_question": None,
    "saved_attempts": set(),
    "interview_active": False,
    "session_signature": None,
    "evaluation_message": ""
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- CALLBACK FUNCTIONS ----------------

def go_to_page(page):
    st.session_state.page = page
    st.session_state.navigation_page = page


def go_to_practice(subject):
    st.session_state.selected_subject = subject
    st.session_state.subject = subject
    st.session_state.page = "Practice Interview"
    st.session_state.navigation_page = "Practice Interview"


def start_interview(subject, level):
    available_questions = QUESTIONS[subject][level]

    # Randomly choose up to 10 questions.
    selected_questions = random.sample(
        available_questions,
        k=min(10, len(available_questions))
    )

    st.session_state.subject = subject
    st.session_state.selected_subject = subject
    st.session_state.level = level
    st.session_state.session_questions = selected_questions
    st.session_state.question_index = 0
    st.session_state.evaluated = False
    st.session_state.evaluation_result = None
    st.session_state.evaluated_question = None
    st.session_state.saved_attempts = set()
    st.session_state.interview_active = True
    st.session_state.session_signature = (subject, level)
    st.session_state.evaluation_message = ""


def move_question(direction):
    total = len(st.session_state.session_questions)

    if total == 0:
        return

    new_index = st.session_state.question_index + direction

    st.session_state.question_index = max(
        0,
        min(new_index, total - 1)
    )

    st.session_state.evaluated = False
    st.session_state.evaluation_result = None
    st.session_state.evaluated_question = None
    st.session_state.evaluation_message = ""


def evaluate_current_answer(
    question_data,
    user_answer,
    subject,
    level,
    index
):
    if not user_answer or not user_answer.strip():
        st.session_state.evaluation_message = (
            "Please enter your answer first."
        )
        return

    result = evaluate_answer(question_data, user_answer)

    st.session_state.evaluated = True
    st.session_state.evaluation_result = result
    st.session_state.evaluated_question = question_data["question"]
    st.session_state.evaluation_message = ""

    attempt_key = (index, question_data["question"])

    if attempt_key not in st.session_state.saved_attempts:
        save_attempt(
            subject,
            level,
            question_data["question"],
            user_answer,
            result["score"]
        )

        st.session_state.saved_attempts.add(attempt_key)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #ffffff;
}

[data-testid="stHeader"] {
    background-color: #0b1120;
}

/* Dark sidebar */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e5e7eb !important;
}

/* Main page text */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label {
    color: #ffffff;
}

/* White answer box with black text */
.stTextArea textarea,
.stTextInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}

.stTextArea textarea::placeholder {
    color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
}

/* Select boxes */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #ffffff;
    color: #111827;
}

/* Buttons */
div.stButton > button,
div.stDownloadButton > button {
    background-color: #2563eb;
    color: #ffffff !important;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}

div.stButton > button p,
div.stButton > button span,
div.stDownloadButton > button p {
    color: #ffffff !important;
}

div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background-color: #1d4ed8;
}

/* Disabled buttons */
div.stButton > button:disabled {
    background-color: #374151 !important;
    color: #d1d5db !important;
}

div.stButton > button:disabled p {
    color: #d1d5db !important;
}

/* Cards */
.card {
    background-color: #172033;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #273449;
    margin-bottom: 12px;
}

.small-text {
    color: #b7c3d8 !important;
    font-size: 14px;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #172033;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #273449;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR NAVIGATION ----------------

pages = [
    "Dashboard",
    "Practice Interview",
    "Performance History"
]

if "navigation_page" not in st.session_state:
    st.session_state.navigation_page = st.session_state.page

st.sidebar.title("🎯 InterviewIQ")
st.sidebar.caption("AI Interview Practice")

# Synchronize sidebar selection with button navigation.
if st.session_state.navigation_page != st.session_state.page:
    st.session_state.navigation_page = st.session_state.page

st.sidebar.radio(
    "Navigation",
    pages,
    key="navigation_page",
    on_change=lambda: go_to_page(
        st.session_state.navigation_page
    )
)

st.sidebar.markdown("---")
st.sidebar.write("Practice. Improve. Succeed.")

page = st.session_state.page


# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.title("🎯 InterviewIQ")
    st.subheader("AI-Based Interview Preparation Platform")

    st.write(
        "Practice technical and HR interview questions, "
        "evaluate your answers, and track your progress."
    )

    history = get_attempts()

    total_attempts = len(history)

    if total_attempts > 0:
        scores = pd.to_numeric(history["score"], errors="coerce")
        average_score = scores.mean()
        best_score = scores.max()
    else:
        average_score = 0
        best_score = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Attempts", total_attempts)
    col2.metric("Average Score", f"{average_score:.2f}%")
    col3.metric("Best Score", f"{best_score:.2f}%")

    st.markdown("---")
    st.subheader("Choose Your Interview Subject")

    subjects = list(QUESTIONS.keys())
    cols = st.columns(3)

    for index, subject in enumerate(subjects):

        with cols[index % 3]:

            total_questions = sum(
                len(items)
                for items in QUESTIONS[subject].values()
            )

            st.markdown(
                f"""
                <div class="card">
                    <h3>{html.escape(subject)}</h3>
                    <p class="small-text">
                        {total_questions} available questions
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.button(
                f"Practice {subject}",
                key=f"practice_{subject}",
                use_container_width=True,
                on_click=go_to_practice,
                args=(subject,)
            )

    st.info(
        "Choose a subject and start practising. "
        "Each interview randomly selects up to 10 questions."
    )


# ---------------- PRACTICE INTERVIEW ----------------

elif page == "Practice Interview":

    st.title("📝 Practice Interview")

    subjects = list(QUESTIONS.keys())

    current_subject = st.session_state.selected_subject

    if current_subject not in subjects:
        current_subject = subjects[0]

    subject_index = subjects.index(current_subject)

    selected_subject = st.selectbox(
        "Select Subject",
        subjects,
        index=subject_index,
        key="practice_subject"
    )

    levels = ["Beginner", "Intermediate", "Advanced"]

    selected_level = st.selectbox(
        "Select Difficulty",
        levels,
        index=levels.index(st.session_state.level),
        key="practice_level"
    )

    st.markdown("---")

    st.button(
        "🎲 Start New Interview",
        key="start_interview_button",
        use_container_width=True,
        on_click=start_interview,
        args=(selected_subject, selected_level)
    )

    current_signature = (selected_subject, selected_level)

    if (
        st.session_state.interview_active
        and st.session_state.session_signature != current_signature
    ):
        st.warning(
            "Your subject or difficulty has changed. "
            "Click Start New Interview to load new questions."
        )

    questions = st.session_state.session_questions

    if not st.session_state.interview_active or not questions:

        st.info(
            "Choose your subject and difficulty, then click "
            "Start New Interview."
        )

    elif st.session_state.session_signature != current_signature:

        st.info(
            "Click Start New Interview to load questions "
            "for the selected subject and difficulty."
        )

    else:

        index = st.session_state.question_index
        total = len(questions)

        question_data = questions[index]
        question_text = question_data["question"]

        st.progress((index + 1) / total)

        st.write(
            f"**Question {index + 1} of {total}** "
            f"• {selected_subject} • {selected_level}"
        )

        st.markdown(
            f"""
            <div class="card">
                <h3>Interview Question</h3>
                <p>{html.escape(question_text)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        answer_key = (
            f"answer_{selected_subject}_{selected_level}_{index}"
        )

        user_answer = st.text_area(
            "Type your answer here",
            key=answer_key,
            height=180,
            placeholder="Write your answer in your own words..."
        )

        st.button(
            "Evaluate Answer",
            key=f"evaluate_{index}",
            use_container_width=True,
            on_click=evaluate_current_answer,
            args=(
                question_data,
                user_answer,
                selected_subject,
                selected_level,
                index
            )
        )

        if st.session_state.evaluation_message:
            st.warning(st.session_state.evaluation_message)

        # Display evaluation results.
        if (
            st.session_state.evaluated
            and st.session_state.evaluated_question == question_text
            and st.session_state.evaluation_result is not None
        ):

            result = st.session_state.evaluation_result

            st.markdown("---")
            st.subheader("📊 Evaluation Result")

            col1, col2, col3 = st.columns(3)

            col1.metric("Overall Score", f"{result['score']}%")
            col2.metric("Text Similarity", f"{result['similarity']}%")
            col3.metric("Keyword Coverage", f"{result['coverage']}%")

            if result["score"] >= 75:
                st.success("Good answer! Keep practising.")
            elif result["score"] >= 40:
                st.warning("Fair attempt. Add more relevant concepts.")
            else:
                st.error("Try improving your answer with key concepts.")

            left, right = st.columns(2)

            with left:
                st.markdown("#### Concepts Found")

                if result["found"]:
                    for keyword in result["found"]:
                        st.write(f"✅ {keyword}")
                else:
                    st.write("No expected keywords detected.")

            with right:
                st.markdown("#### Concepts to Improve")

                if result["missing"]:
                    for keyword in result["missing"]:
                        st.write(f"❌ {keyword}")
                else:
                    st.write("All expected keywords were detected.")

            with st.expander("View Reference Answer"):
                st.write(question_data["answer"])

        st.markdown("---")

        previous_col, position_col, next_col = st.columns([1, 2, 1])

        with previous_col:
            st.button(
                "⬅ Previous Question",
                key=f"previous_{index}",
                disabled=(index == 0),
                use_container_width=True,
                on_click=move_question,
                args=(-1,)
            )

        with position_col:
            st.markdown(
                f"<p style='text-align:center;'>"
                f"Question {index + 1} / {total}</p>",
                unsafe_allow_html=True
            )

        with next_col:
            st.button(
                "Next Question ➡",
                key=f"next_{index}",
                disabled=(index == total - 1),
                use_container_width=True,
                on_click=move_question,
                args=(1,)
            )

        if index == total - 1:
            st.info(
                "You reached the last question. "
                "Start a new interview for another random set."
            )


# ---------------- PERFORMANCE HISTORY ----------------

elif page == "Performance History":

    st.title("📈 Performance History")

    history = get_attempts()

    if history.empty:

        st.info(
            "No interview attempts yet. Complete an interview "
            "to see your performance history."
        )

    else:

        history["score"] = pd.to_numeric(
            history["score"], errors="coerce"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Attempts", len(history))
        col2.metric(
            "Average Score",
            f"{history['score'].mean():.2f}%"
        )
        col3.metric(
            "Best Score",
            f"{history['score'].max():.2f}%"
        )

        st.markdown("---")
        st.subheader("Average Score by Subject")

        chart_data = (
            history.groupby("subject", as_index=False)["score"]
            .mean()
        )

        figure = px.bar(
            chart_data,
            x="subject",
            y="score",
            title="Average Interview Score",
            labels={
                "subject": "Subject",
                "score": "Average Score (%)"
            }
        )

        figure.update_layout(
            paper_bgcolor="#0b1120",
            plot_bgcolor="#172033",
            font_color="white",
            yaxis_range=[0, 100]
        )

        st.plotly_chart(figure, use_container_width=True)

        st.markdown("---")
        st.subheader("Previous Attempts")

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

        csv_data = history.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download History as CSV",
            data=csv_data,
            file_name="interview_history.csv",
            mime="text/csv"
        )
