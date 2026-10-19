# 🐾 AI-Powered Desktop Virtual Pet Application
> Built with **Python 3.11**, **Django 5**, **SQLite**, and **Generative AI** for MCA Semester III GenAI Lab Practical Examination.

---

## 🚀 Quick Start Instructions (Windows & VS Code)

### 1. Open Project Folder in Terminal
```powershell
cd "c:\Users\Admin\Desktop\Ai-Powwered Virtual Pet Vpplication"
```

### 2. Activate the Virtual Environment
```powershell
.\venv\Scripts\activate
```

### 3. (Optional) Configure Google Gemini AI API Key
The app runs **100% offline** using its built-in Intelligent Fallback Response System.
If you have a Google Gemini API Key and want live cloud AI:
Open `.env` and paste your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run Automated Unit Tests (Verify All 9 Cases)
```powershell
python manage.py test
```
*Expected output: `Ran 9 tests in 0.050s - OK`*

### 5. Launch the Development Server
```powershell
python manage.py runserver
```

### 6. Open in Browser
Visit: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🧭 Application Pages & Features

| Route | Feature | Description |
|---|---|---|
| `/` | **Pet Dashboard** | Mascot stage, mood aura, hunger/happiness/energy stats, Feed/Play/Nap buttons, live timeline |
| `/chat/` | **AI Chat Room** | Conversational dialogue with your pet, prompt suggestions, AI / Fallback badges |
| `/create/` | **Pet Adoption** | Interactive creation form with live preview (Cat 🐱, Dog 🐶, Rabbit 🐰, Panda 🐼) |
| `/pets/` | **Pet Sanctuary** | View all adopted pets and switch active companion |
| `/admin/` | **Django Admin** | Superuser login (`admin` / `admin123`) to view raw SQLite records |

---

## 🧪 Testing Checklist (9 Mandated Test Cases)
- [x] **Test 1:** Pet creation (`name='Coco'`, Dog, Friendly)
- [x] **Test 2:** Feeding reduces hunger & increases happiness
- [x] **Test 3:** Playing increases happiness & decreases energy
- [x] **Test 4:** Chatting with "Hello!" returns contextual greeting
- [x] **Test 5:** "Are you hungry?" accurately reflects pet's hunger level
- [x] **Test 6:** State and interactions persist across database reloads
- [x] **Test 7:** Setting low energy ($\le 20$) triggers **Sleepy 😴** mood
- [x] **Test 8:** Seamless fallback execution when no API key is provided
- [x] **Test 9:** Numeric bounds checking clamps values between 0 and 100

---

## 📚 Examination Reference
For detailed algorithm explanations, database ER diagrams, prompt engineering design, and 10 viva questions, consult:
📄 **[`MCA_LAB_EXAM_MANUAL.md`](MCA_LAB_EXAM_MANUAL.md)**
