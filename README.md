# 🎯 Goal Tracker AI

An AI-powered daily productivity and goal tracking application built using Python and Streamlit. The app generates personalized daily tasks, tracks progress, maintains streaks, and provides AI-generated feedback using Google Gemini API.

---

## 🚀 Features

- 🤖 AI-generated personalized daily plans
- 📈 Progress tracking with streak system
- 🎯 Adaptive difficulty based on user performance
- 💡 AI-generated motivational feedback
- 📊 Interactive analytics and completion history
- 🛡️ Smart fallback logic when AI responses fail
- 🧠 Prompt engineering with structured JSON responses
- 💾 Persistent local data storage using JSON

---

## 🛠️ Tech Stack

- Frontend/UI: Streamlit
- Backend: Python
- AI Integration: Google Gemini 1.5 Flash API
- Data Handling: Pandas
- Storage: JSON

---

## 📂 Project Structure

```bash
├── app.py
├── progress.json
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/goal-tracker-ai.git
cd goal-tracker-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Gemini API Key

For Linux/Mac:

```bash
export GOOGLE_API_KEY="your_api_key"
```

For Windows:

```bash
set GOOGLE_API_KEY=your_api_key
```

### 4. Run the Application

```bash
streamlit run app.py
```

---

## 📸 Workflow

1. User enters a goal and duration.
2. AI generates personalized daily tasks.
3. User marks completed tasks.
4. Progress percentage and streak are updated.
5. AI provides personalized feedback and tips.
6. Historical analytics are visualized using charts.

---

## 🧠 AI Capabilities

- Personalized task generation
- Goal-specific recommendations
- Dynamic difficulty adjustment
- Structured JSON response parsing
- Feedback generation based on completion percentage

---

## 📊 Example Goals

- Lose weight
- Crack placements
- Learn Python
- Improve coding skills
- Prepare for exams

---

## 🔮 Future Improvements

- User authentication
- Cloud database integration
- Weekly/monthly AI reports
- Mobile responsive UI
- Notification system

---

## 👨‍💻 Author

Developed by Venkatesh Gawade
