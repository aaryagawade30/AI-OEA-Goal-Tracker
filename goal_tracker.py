import streamlit as st
import json
import os
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import re

# ---------- CONFIG ----------
st.set_page_config(page_title="Goal Tracker AI", page_icon="🎯")

genai.configure(api_key=os.environ.get("AIzaSyDo5IUo6jOQaRSbKUPjrhhF_VGPN4IWEJI"))
model = genai.GenerativeModel("gemini-1.5-flash")

FILE = "progress.json"

# ---------- DATA ----------
def load_data():
    if not os.path.exists(FILE):
        return {"history": [], "streak": 0, "goal": "", "days": 30}
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- SAFE JSON PARSER ----------
def extract_json(text):
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No valid JSON found in response")

# ---------- GOAL-SPECIFIC FALLBACKS ----------
def smart_fallback_plan(goal, day, difficulty):
    """Return realistic goal-specific tasks when AI fails."""
    g = goal.lower()
    num_tasks = 3 if difficulty == "easy" else 5 if difficulty == "hard" else 4

    if any(w in g for w in ["weight", "fat", "fit", "slim", "diet", "body", "kg", "lose", "health"]):
        all_tasks = [
            "Morning walk or jog for 30 minutes",
            "Do 3 sets of bodyweight squats, push-ups, and planks",
            "Drink at least 8 glasses of water today",
            "Eat a high-protein, low-carb meal for lunch",
            "Track your calories using a food diary or app",
            "Avoid sugar and processed snacks for the entire day",
            "Do 20 minutes of yoga or stretching before bed",
        ]
        topic = "Fitness & Nutrition"
        tip = "Small daily actions compound into big results. Stay consistent!"

    elif any(w in g for w in ["placement", "job", "interview", "career", "hiring", "resume", "leetcode", "coding", "programming"]):
        all_tasks = [
            "Solve 3 DSA problems on LeetCode (easy to medium)",
            "Revise one core CS topic: OS, DBMS, or Networking",
            "Mock interview: answer 5 common HR questions aloud",
            "Update your resume with 1 new project or skill",
            "Read about the company culture of 2 target companies",
            "Practice system design: design a URL shortener",
            "Review your weak areas from previous mock tests",
        ]
        topic = "Placement Preparation"
        tip = "Practice like it's the real interview — pressure builds champions."

    elif any(w in g for w in ["python", "code", "program", "developer", "software"]):
        all_tasks = [
            "Write a Python script solving a real-world problem",
            "Complete one chapter/module from your current course",
            "Debug and improve a previous project you built",
            "Read official documentation for one library you use",
            "Build a small feature: a calculator, to-do app, or API call",
            "Watch one tutorial and type along with the code",
            "Push today's work to GitHub with a proper commit message",
        ]
        topic = "Coding Practice"
        tip = "The best way to learn coding is to write code every single day."

    elif any(w in g for w in ["study", "exam", "test", "score", "marks", "academic"]):
        all_tasks = [
            "Study for 2 focused Pomodoro sessions (25 min each)",
            "Make summary notes for today's chapter",
            "Solve 10 practice questions from last year's papers",
            "Teach back a concept to yourself without notes",
            "Review yesterday's material for 15 minutes",
            "Create a mind map of the current topic",
            "Set a specific target score and plan backward from it",
        ]
        topic = "Academic Study"
        tip = "Active recall beats passive reading — test yourself constantly."

    else:
        all_tasks = [
            f"Spend 45 minutes working directly on: {goal}",
            f"Research one method or technique related to {goal}",
            "Write down 3 obstacles and your plan to overcome them",
            "Connect with someone who has achieved a similar goal",
            f"Track measurable progress toward your goal today",
        ]
        topic = "Goal Progress"
        tip = "Break your goal into today's single most important action."

    return {
        "topic": topic,
        "tasks": all_tasks[:num_tasks],
        "tip": tip
    }

def smart_fallback_feedback(goal, completion, streak):
    if completion >= 80:
        fb = f"Excellent work! You completed {completion}% of your tasks — outstanding dedication toward '{goal}'. Your {streak}-day streak shows real commitment."
        tip = "Push yourself with one extra challenge tomorrow to maintain this momentum."
    elif completion >= 60:
        fb = f"Good job completing {completion}% today toward '{goal}'. You're making solid progress and your {streak}-day streak is intact."
        tip = "Identify which task took longest and time-box it better tomorrow."
    elif completion >= 40:
        fb = f"You completed {completion}% today. That's a start, but you can do better for '{goal}'. Use the streak reset as motivation to bounce back."
        tip = "Start tomorrow with your easiest task first to build momentum early."
    else:
        fb = f"Only {completion}% completed today. Don't give up on '{goal}' — reflect on what blocked you and plan to remove that obstacle tomorrow."
        tip = "Set a specific time block tomorrow and remove all distractions during it."
    return {"feedback": fb, "tomorrow_tip": tip}

# ---------- AI FUNCTIONS ----------
def ai_generate_plan(goal, day, total_days, difficulty, last_completion):
    num_tasks = {"easy": 3, "normal": 4, "hard": 5}.get(difficulty, 4)
    last_info = f"Yesterday the user completed {last_completion}% of tasks." if last_completion is not None else "This is the user's first day."

    prompt = f"""You are a practical daily task planner. The user has a specific personal goal.

User's goal: "{goal}"
Current day: {day} out of {total_days} total days
Difficulty level: {difficulty} (generate exactly {num_tasks} tasks)
{last_info}

Generate {num_tasks} REALISTIC, SPECIFIC, ACTIONABLE tasks for TODAY that directly help achieve "{goal}".

STRICT RULES:
- Tasks must be physically doable TODAY (not vague advice)
- If goal is fitness/weight loss: give specific exercises (sets/reps), meal targets, water intake
- If goal is learning/coding: give specific topics to study, problems to solve with numbers
- If goal is career/placement: give specific interview prep activities, resume tasks
- NEVER write "Study [goal name]" — that is meaningless
- NEVER write "Practice key concepts" — too vague
- Each task must be completable in 20-60 minutes
- Vary focus from previous days

Respond with ONLY valid JSON, no markdown, no explanation:
{{"topic": "2-4 word focus area", "tasks": ["task 1", "task 2", "task 3"], "tip": "Motivational sentence under 15 words."}}"""

    try:
        res = model.generate_content(prompt)
        parsed = extract_json(res.text)
        tasks = parsed.get("tasks", [])
        # Reject if AI returned generic garbage
        bad_phrases = [f"study {goal.lower()}", "practice key concepts", "revise previous work"]
        if not tasks or any(any(bp in t.lower() for bp in bad_phrases) for t in tasks):
            raise ValueError("AI returned generic tasks — using smart fallback")
        return parsed
    except Exception as e:
        return smart_fallback_plan(goal, day, difficulty)


def ai_generate_feedback(goal, day, completion, tasks, streak):
    prompt = f"""You are a supportive but honest AI coach reviewing someone's daily progress.

User's goal: "{goal}"
Day {day} completion: {completion}%
Tasks they had today: {json.dumps(tasks)}
Current streak: {streak} days

Write personalized feedback referencing their actual goal and completion rate.

Respond with ONLY valid JSON, no markdown:
{{"feedback": "2-3 sentences of honest personalized feedback.", "tomorrow_tip": "One concrete actionable tip for tomorrow under 20 words."}}"""

    try:
        res = model.generate_content(prompt)
        parsed = extract_json(res.text)
        if not parsed.get("feedback") or not parsed.get("tomorrow_tip"):
            raise ValueError("Incomplete response")
        return parsed
    except Exception as e:
        return smart_fallback_feedback(goal, completion, streak)

# ---------- DIFFICULTY ----------
def adjust_difficulty(history):
    if len(history) < 2:
        return "normal"
    if history[-1]["completion"] < 40:
        return "easy"
    if history[-1]["completion"] > 80 and history[-2]["completion"] > 80:
        return "hard"
    return "normal"

def difficulty_badge(d):
    return {"easy": "🟢 Easy", "normal": "🔵 Normal", "hard": "🔴 Hard"}.get(d, "🔵 Normal")

def completion_color(pct):
    if pct >= 80: return "🟢"
    if pct >= 60: return "🔵"
    if pct >= 40: return "🟡"
    return "🔴"

# ---------- SESSION STATE ----------
for key, default in [
    ("tasks", []), ("topic", ""), ("tip", ""),
    ("submitted", False), ("feedback", {}),
    ("difficulty", "normal"), ("plan_generated", False)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- LOAD ----------
data = load_data()

# ---------- UI ----------
st.title("🎯 Goal Tracker AI")
st.caption("AI-powered daily plans that adapt to your real progress")

col1, col2 = st.columns([3, 1])
with col1:
    goal = st.text_input("Your goal", value=data.get("goal", ""),
                         placeholder="e.g. Lose 5kg, Crack placement, Learn Python...")
with col2:
    days = st.number_input("Total days", 1, 365, value=data.get("days", 30))

day_num = len(data["history"]) + 1
history = data.get("history", [])
streak = data.get("streak", 0)
avg = round(sum(h["completion"] for h in history) / len(history)) if history else 0

c1, c2, c3 = st.columns(3)
c1.metric("📅 Day", day_num)
c2.metric("🔥 Streak", f"{streak} days")
c3.metric("📊 Avg", f"{avg}%" if history else "—")

st.divider()

# ---------- GENERATE ----------
if st.button("✨ Generate Today's Plan", type="primary", disabled=not bool(goal.strip())):
    data["goal"] = goal.strip()
    data["days"] = days
    save_data(data)

    difficulty = adjust_difficulty(history)
    last = history[-1]["completion"] if history else None

    with st.spinner(f"🤖 Building your Day {day_num} plan for: {goal}..."):
        plan = ai_generate_plan(goal.strip(), day_num, days, difficulty, last)

    st.session_state.tasks = plan.get("tasks", [])
    st.session_state.topic = plan.get("topic", "Today's Focus")
    st.session_state.tip = plan.get("tip", "")
    st.session_state.difficulty = difficulty
    st.session_state.submitted = False
    st.session_state.feedback = {}
    st.session_state.plan_generated = True
    st.rerun()

# ---------- SHOW PLAN ----------
if st.session_state.plan_generated and st.session_state.tasks:
    diff = st.session_state.difficulty

    st.subheader(f"📋 Day {day_num}: {st.session_state.topic}")
    st.caption(f"Difficulty: {difficulty_badge(diff)}")

    if st.session_state.tip:
        st.info(f"💡 {st.session_state.tip}")

    st.markdown("**Check off each task as you complete it:**")
    checked_list = []
    for i, task in enumerate(st.session_state.tasks):
        done = st.checkbox(task, key=f"chk_{i}_{day_num}",
                           disabled=st.session_state.submitted)
        checked_list.append(done)

    total = len(st.session_state.tasks)
    done_count = sum(checked_list)
    pct = int((done_count / total) * 100) if total else 0

    st.progress(pct / 100)
    st.write(f"**Progress: {done_count}/{total} tasks — {pct}%**")

    if not st.session_state.submitted:
        if st.button("✅ Submit Progress", type="primary"):
            if pct >= 60:
                data["streak"] = data.get("streak", 0) + 1
            else:
                data["streak"] = 0

            data["history"].append({
                "day": day_num,
                "completion": pct,
                "date": str(datetime.now().date()),
                "topic": st.session_state.topic
            })
            save_data(data)

            with st.spinner("🤖 Generating your personalized feedback..."):
                fb = ai_generate_feedback(
                    data["goal"], day_num, pct,
                    st.session_state.tasks, data["streak"]
                )

            st.session_state.feedback = fb
            st.session_state.submitted = True
            st.rerun()

# ---------- FEEDBACK ----------
if st.session_state.submitted and st.session_state.feedback:
    fb = st.session_state.feedback
    updated = load_data()
    new_streak = updated.get("streak", 0)
    last_pct = updated["history"][-1]["completion"] if updated["history"] else 0
    icon = completion_color(last_pct)

    st.success(f"{icon} Day {day_num} complete — {last_pct}% | 🔥 Streak: {new_streak} days")
    st.markdown("**🤖 AI Feedback:**")
    st.info(fb.get("feedback", ""))
    st.markdown("**📌 For Tomorrow:**")
    st.warning(fb.get("tomorrow_tip", ""))

    if st.button("📅 Plan Next Day", type="primary"):
        st.session_state.plan_generated = False
        st.session_state.submitted = False
        st.session_state.tasks = []
        st.session_state.feedback = {}
        st.rerun()

# ---------- HISTORY ----------
if data["history"]:
    st.divider()
    st.subheader("📊 Progress History")
    df = pd.DataFrame(data["history"])
    st.line_chart(df.set_index("day")["completion"], use_container_width=True)

    with st.expander("📋 View all days"):
        for h in reversed(data["history"]):
            icon = completion_color(h["completion"])
            topic = h.get("topic", "—")
            st.write(f"**Day {h['day']}** | {h['date']} | {topic} | {icon} {h['completion']}%")

    st.divider()
    if st.button("🗑️ Reset All Progress"):
        if os.path.exists(FILE):
            os.remove(FILE)
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()