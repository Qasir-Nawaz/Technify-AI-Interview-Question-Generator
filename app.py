import streamlit as st
from groq import Groq
import json

st.set_page_config(page_title="Job Interview Question Generator", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #1a1a4e, #24243e) !important; }
    section[data-testid="stSidebar"] { background: #1e1b4b !important; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .stButton > button { border-radius: 10px; font-weight: 600; }
    .question-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 20px 24px; margin: 14px 0; border-left: 4px solid #6366f1; }
    .hr-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 20px 24px; margin: 14px 0; border-left: 4px solid #34d399; }
    .result-card { background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2)); border: 1px solid rgba(99,102,241,0.4); border-radius: 20px; padding: 30px; text-align: center; margin: 20px 0; }
    .score-big { font-size: 72px; font-weight: 900; }
    .feedback-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; margin: 8px 0; }
    div[data-testid="stTextArea"] textarea { background: #1e1b4b !important; color: #e2e8f0 !important; border: 1px solid #4f46e5 !important; border-radius: 10px !important; }
    div[data-testid="stTextInput"] input { background: #1e1b4b !important; color: #e2e8f0 !important; border: 1px solid #4f46e5 !important; }
    div[data-testid="stSelectbox"] > div > div { background: #1e1b4b !important; color: #e2e8f0 !important; border: 1px solid #4f46e5 !important; }
    div[data-testid="stMultiSelect"] > div > div { background: #1e1b4b !important; color: #e2e8f0 !important; border: 1px solid #4f46e5 !important; }
    .stMarkdown p { color: #e2e8f0 !important; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    label { color: #a5b4fc !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #a78bfa !important; }
    div[data-testid="metric-container"] { background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

ALL_TOPICS = {
    "Programming Languages": ["Python", "C++", "C", "Java", "JavaScript", "TypeScript", "Go", "PHP", "Swift", "Kotlin", "Rust"],
    "Web Development": ["HTML", "CSS", "React", "Vue.js", "Angular", "Node.js", "Express.js", "Django", "Flask", "Next.js", "REST APIs", "GraphQL"],
    "Database": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Firebase", "Oracle", "SQL Server"],
    "DevOps & Cloud": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Git", "CI/CD", "Terraform"],
    "AI & Data Science": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Pandas", "NumPy", "TensorFlow", "PyTorch", "Scikit-learn"],
    "Cybersecurity": ["Network Security", "Penetration Testing", "Ethical Hacking", "Cryptography", "SIEM", "Firewall", "SOC"],
    "Mobile Development": ["Flutter", "React Native", "Android (Kotlin)", "iOS (Swift)", "Firebase"],
    "ICT": ["Computer Basics", "MS Word", "MS Excel", "MS PowerPoint", "Internet & Email", "Networking Basics", "Hardware & Software", "Operating Systems", "Spreadsheets", "Data Entry"],
    "Mathematics": ["Algebra", "Calculus", "Statistics", "Probability", "Linear Algebra", "Discrete Mathematics", "Trigonometry", "Number Theory"],
    "Physics": ["Mechanics", "Thermodynamics", "Electricity & Magnetism", "Optics", "Modern Physics", "Waves & Sound"],
    "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Atomic Structure", "Chemical Bonding", "Reactions"],
    "Biology": ["Cell Biology", "Genetics", "Human Anatomy", "Ecology", "Evolution", "Microbiology", "Botany"],
    "English": ["Grammar", "Writing Skills", "Comprehension", "Vocabulary", "Essay Writing", "Communication Skills"],
    "Pakistan Studies": ["History of Pakistan", "Geography", "Government & Politics", "Economy", "Culture & Society"],
    "Data Structures & Algorithms": ["Arrays", "Linked Lists", "Stacks & Queues", "Trees", "Graphs", "Sorting Algorithms", "Searching Algorithms", "Dynamic Programming", "Big O Notation"],
    "OOP Concepts": ["Classes & Objects", "Inheritance", "Polymorphism", "Encapsulation", "Abstraction", "Design Patterns"],
    "Computer Networks": ["OSI Model", "TCP/IP", "DNS", "HTTP/HTTPS", "Routing & Switching", "Network Protocols", "Wireless Networks"],
    "Operating Systems": ["Process Management", "Memory Management", "File Systems", "Deadlocks", "Scheduling", "Linux Commands", "Windows OS"],
    "Software Engineering": ["SDLC", "Agile & Scrum", "Requirements Engineering", "Testing", "Version Control", "Project Management", "UML Diagrams"],
    "Law (Wakeelat)": ["Constitutional Law", "Contract Law", "Criminal Law", "Civil Law", "Family Law", "Corporate Law", "Intellectual Property", "Human Rights Law", "International Law", "Islamic Law (Fiqh)", "Pakistan Penal Code (PPC)", "Court Procedures", "Evidence Law", "Property Law"]
}

if "stage" not in st.session_state:
    st.session_state.stage = "setup"
if "questions" not in st.session_state:
    st.session_state.questions = None
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "result" not in st.session_state:
    st.session_state.result = None

with st.sidebar:
    st.markdown("## Settings")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.markdown("---")
    difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    num_q = st.slider("Questions per section", 3, 25, 10)
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("1. Enter API key\n2. Choose category\n3. Select topics\n4. Generate questions\n5. Write answers\n6. Check result!")

st.markdown("""
<div style='text-align:center;padding:30px 20px 10px;'>
    <h1 style='background:linear-gradient(90deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:40px;font-weight:900;margin:0;'>Job Interview Question Generator</h1>
    <p style='color:#94a3b8;font-size:15px;margin:10px 0 20px;'>Choose your skills, solve questions, and check your result!</p>
    <div style='display:inline-block;background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.35);border-radius:50px;padding:10px 28px;'>
        <span style='color:#a5b4fc;font-size:13px;font-weight:600;letter-spacing:1px;'>Developed by &nbsp;</span>
        <span style='color:#e2e8f0;font-size:15px;font-weight:800;'>Qasir Nawaz Marri</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

if st.session_state.stage == "setup":
    st.markdown("### Select Category and Topics")
    category = st.selectbox("Category", list(ALL_TOPICS.keys()))
    topics_in_cat = ALL_TOPICS[category]
    selected = st.multiselect("Topics / Technologies", options=topics_in_cat, default=topics_in_cat[:3], placeholder="Select...")
    custom = st.text_input("Custom topic (optional)", placeholder="e.g. GraphQL, Solidity...")
    if custom and custom not in selected:
        selected.append(custom)
    if selected:
        st.info(f"Selected: {', '.join(selected)}")
    st.divider()
    if st.button("Generate Interview Questions", use_container_width=True, type="primary"):
        if not api_key:
            st.error("Please enter your API key in the sidebar!")
        elif not selected:
            st.error("Please select at least one topic!")
        else:
            with st.spinner(f"Generating {category} Questions Please Wait..."):
                try:
                    client = Groq(api_key=api_key)
                    prompt = f"""You are an expert interviewer. Generate exactly {num_q} technical and {num_q} HR interview questions.
Topics: {', '.join(selected)}
Difficulty: {difficulty}
- Easy: very simple, beginner level, like explaining to a new student with no experience
- Medium: practical usage and real world examples
- Hard: advanced, system design, optimization
Return ONLY valid JSON, no extra text:
{{"technical":[{{"question":"...","hint":"...","topic":"..."}}],"hr":[{{"question":"...","hint":"..."}}]}}
Exactly {num_q} items in each array."""
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4000,
                        temperature=0.7
                    )
                    raw = response.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
                    data = json.loads(raw)
                    st.session_state.questions = data
                    st.session_state.answers = {}
                    st.session_state.result = None
                    st.session_state.selected = selected
                    st.session_state.category = category
                    st.session_state.difficulty = difficulty
                    st.session_state.num_q = num_q
                    st.session_state.stage = "quiz"
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Failed to parse response. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

elif st.session_state.stage == "quiz":
    data = st.session_state.questions
    st.markdown(f"### Topics: `{', '.join(st.session_state.selected)}` | `{st.session_state.difficulty}`")
    tab1, tab2 = st.tabs([f"Technical ({len(data['technical'])} Qs)", f"HR & Behavioral ({len(data['hr'])} Qs)"])
    with tab1:
        for i, q in enumerate(data["technical"]):
            st.markdown(f'<div class="question-card"><b style="color:#e2e8f0;font-size:16px;">Q{i+1}. {q["question"]}</b><br><br><span style="background:rgba(99,102,241,0.2);color:#a5b4fc;padding:3px 10px;border-radius:20px;font-size:12px;">{q.get("topic","Technical")}</span></div>', unsafe_allow_html=True)
            with st.expander("Show Hint"):
                st.info(q.get("hint",""))
            st.session_state.answers[f"tech_{i}"] = st.text_area("Answer:", key=f"ans_tech_{i}", placeholder="Write your answer here...", height=90, label_visibility="collapsed")
    with tab2:
        for i, q in enumerate(data["hr"]):
            st.markdown(f'<div class="hr-card"><b style="color:#e2e8f0;font-size:16px;">Q{i+1}. {q["question"]}</b><br><br><span style="background:rgba(52,211,153,0.2);color:#6ee7b7;padding:3px 10px;border-radius:20px;font-size:12px;">Behavioral</span></div>', unsafe_allow_html=True)
            with st.expander("Show Hint"):
                st.info(q.get("hint",""))
            st.session_state.answers[f"hr_{i}"] = st.text_area("Answer:", key=f"ans_hr_{i}", placeholder="Write your answer here...", height=90, label_visibility="collapsed")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Questions", use_container_width=True):
            st.session_state.stage = "setup"
            st.session_state.questions = None
            st.rerun()
    with col2:
        if st.button("Check Result!", use_container_width=True, type="primary"):
            answered = [v for v in st.session_state.answers.values() if v and v.strip()]
            if len(answered) < 1:
                st.error("Please write at least 1 answer!")
            else:
                st.session_state.stage = "result"
                st.rerun()

elif st.session_state.stage == "result":
    data = st.session_state.questions
    answers = st.session_state.answers
    total_questions = len(data["technical"]) + len(data["hr"])
    answered_count = len([v for v in answers.values() if v and v.strip()])
    with st.spinner("Evaluating your result..."):
        try:
            client = Groq(api_key=api_key)
            qa_pairs = []
            for i, q in enumerate(data["technical"]):
                ans = answers.get(f"tech_{i}","").strip()
                if ans:
                    qa_pairs.append(f"Technical Q{i+1}: {q['question']}\nAnswer: {ans}")
                else:
                    qa_pairs.append(f"Technical Q{i+1}: {q['question']}\nAnswer: NOT ANSWERED")
            for i, q in enumerate(data["hr"]):
                ans = answers.get(f"hr_{i}","").strip()
                if ans:
                    qa_pairs.append(f"HR Q{i+1}: {q['question']}\nAnswer: {ans}")
                else:
                    qa_pairs.append(f"HR Q{i+1}: {q['question']}\nAnswer: NOT ANSWERED")
            eval_prompt = f"""You are a strict interviewer evaluating interview answers.
Total questions: {total_questions}
Questions answered: {answered_count}
Unanswered questions must get score 0.
Difficulty: {st.session_state.difficulty}
Topics: {', '.join(st.session_state.selected)}
All Q&As:
{chr(10).join(qa_pairs)}
STRICT RULES:
- Score each question out of 10
- NOT ANSWERED = score 0
- correct_count = questions with score 7 or above
- wrong_count = total_questions - correct_count
- total_score = (sum of all scores) / (total_questions * 10) * 100, round to integer
- Be honest and strict
Return ONLY valid JSON:
{{"total_score":10,"grade":"F","verdict":"Needs More Practice","correct_count":2,"wrong_count":18,"total_questions":{total_questions},"answered":{answered_count},"summary":"honest 2-3 line summary","strengths":["s1","s2"],"improvements":["i1","i2","i3"],"advice":"detailed professional advice","hire_recommendation":"No Hire","individual":[{{"question":"...","score":0,"status":"wrong","feedback":"Not answered"}}]}}"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": eval_prompt}],
                max_tokens=4000,
                temperature=0.1
            )
            raw = response.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
            st.session_state.result = json.loads(raw)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

    result = st.session_state.result
    score = result.get("total_score", 0)
    correct = result.get("correct_count", 0)
    wrong = result.get("wrong_count", 0)
    total = result.get("total_questions", total_questions)
    answered = result.get("answered", answered_count)
    score_color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"

    st.markdown(f"""
<div class="result-card">
<div class="score-big" style="color:{score_color};">{score}%</div>
<h2 style="color:#e2e8f0;">{result.get("verdict","")}</h2>
<h3 style="color:#94a3b8;">Grade: {result.get("grade","")}</h3>
<p style="color:#cbd5e1;font-size:15px;">{result.get("summary","")}</p>
<span style="background:rgba(99,102,241,0.3);color:#a5b4fc;padding:8px 20px;border-radius:20px;font-weight:700;font-size:15px;">{result.get("hire_recommendation","")}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("### Result Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Questions", total)
    c2.metric("Answered", answered)
    c3.metric("Correct (7+/10)", correct)
    c4.metric("Wrong / Skipped", wrong)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Strengths")
        for s in result.get("strengths", []):
            st.markdown(f'<div class="feedback-card"><span style="color:#6ee7b7;">✓</span> <span style="color:#e2e8f0;">{s}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown("### Areas to Improve")
        for imp in result.get("improvements", []):
            st.markdown(f'<div class="feedback-card"><span style="color:#fbbf24;">→</span> <span style="color:#e2e8f0;">{imp}</span></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### Pro Advice")
    st.info(result.get("advice", ""))

    st.divider()
    st.markdown("### Question-wise Feedback")
    individual = result.get("individual", [])
    correct_qs = [item for item in individual if item.get("score", 0) >= 7]
    wrong_qs = [item for item in individual if item.get("score", 0) < 7]

    tab_c, tab_w = st.tabs([f"Correct ({len(correct_qs)})", f"Wrong / Skipped ({len(wrong_qs)})"])
    with tab_c:
        if correct_qs:
            for item in correct_qs:
                st.markdown(f'<div class="feedback-card"><b style="color:#e2e8f0;">{item.get("question","")}</b><br><span style="color:#22c55e;font-weight:700;">Score: {item.get("score",0)}/10</span> | <span style="color:#94a3b8;">{item.get("feedback","")}</span></div>', unsafe_allow_html=True)
        else:
            st.warning("No correct answers!")
    with tab_w:
        if wrong_qs:
            for item in wrong_qs:
                q_score = item.get("score", 0)
                color = "#f59e0b" if q_score >= 4 else "#ef4444"
                st.markdown(f'<div class="feedback-card"><b style="color:#e2e8f0;">{item.get("question","")}</b><br><span style="color:{color};font-weight:700;">Score: {q_score}/10</span> | <span style="color:#94a3b8;">{item.get("feedback","")}</span></div>', unsafe_allow_html=True)
        else:
            st.success("All questions correct!")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again", use_container_width=True):
            st.session_state.stage = "quiz"
            st.session_state.answers = {}
            st.session_state.result = None
            st.rerun()
    with col2:
        if st.button("New Topic", use_container_width=True, type="primary"):
            st.session_state.stage = "setup"
            st.session_state.questions = None
            st.session_state.answers = {}
            st.session_state.result = None
            st.rerun()
