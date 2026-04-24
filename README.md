# 🚚 Moving AI Estimator

An automated moving cost estimation system built using Google Forms, Google Apps Script, Azure Functions (Python), Google Routes API, and OpenAI.

---

## 📌 Overview

This project automates the process of generating moving estimates for customers.

### Workflow
1. A customer submits a Google Form
2. Google Apps Script triggers on form submission
3. Form data is sent to an Azure Function (Python backend)
4. The backend:
   - calculates travel time using Google Routes API
   - applies base business logic
   - enhances the estimate using OpenAI
5. The final estimate is written to Google Sheets and emailed to the customer

---

## 🧠 Architecture

```text
Google Form
   ↓
Apps Script (trigger)
   ↓
Azure Function (Python API)
   ├── Google Routes API (travel time)
   ├── Business Logic (crew, truck, hours)
   └── OpenAI (estimate text)
   ↓
Google Sheets + Email

⚙️ Tech Stack
	•	Python
	•	Azure Functions
	•	Google Apps Script
	•	Google Forms
	•	Google Sheets
	•	Google Routes API
	•	OpenAI API

⸻

🚀 Features
	•	Automated moving estimate generation
	•	Travel time calculation using Google Routes API
	•	Rule-based recommendations for crew size, truck size, and labor hours
	•	AI-generated customer-facing email text
	•	Google Sheets integration
	•	Automated email delivery
	•	End-to-end workflow automation

⸻

🏗️ Project Structure
moving-ai-estimator/
├── README.md
├── azure-function/
│   ├── function_app.py
│   ├── host.json
│   ├── requirements.txt
│   └── local.settings.json      # local only, do not upload
├── apps-script/
│   └── Code.gs
├── docs/
│   ├── SevenMoving_Advanced_Portfolio.pdf
│   └── moving_estimator_architecture.pdf
└── samples/
    └── sample_request.json
    🔧 Backend Responsibilities

The Azure Function backend is responsible for:
	•	receiving HTTP requests from Apps Script
	•	validating request data
	•	calculating travel time with Google Routes API
	•	applying base recommendation logic
	•	calling OpenAI for estimate enhancement
	•	returning structured JSON back to Apps Script

⸻

📜 Apps Script Responsibilities

The Google Apps Script layer is responsible for:
	•	triggering automatically when a form is submitted
	•	extracting form values from Google Sheets
	•	sending request payloads to Azure Functions
	•	parsing the JSON response
	•	writing results back to the sheet
	•	sending the estimate email to the customer

⸻

🧮 Estimation Logic

The system separates deterministic logic from AI enhancement.

Deterministic logic

Handled in Python:
	•	travel time calculation
	•	crew recommendation
	•	truck recommendation
	•	labor hour range

AI logic

Handled by OpenAI:
	•	refining the estimate wording
	•	explaining the recommendation
	•	generating customer-friendly email text

⸻

❗ Why AI does not calculate travel time

Travel time is calculated explicitly using Google Routes API inside the Python backend.

This design ensures that:
	•	route data is accurate
	•	core numbers are not guessed by AI
	•	business-critical values remain deterministic
	•	AI is only used where it adds value

⸻

💡 Why this architecture

This project intentionally separates responsibilities:
	•	Apps Script handles Google-side automation and orchestration
	•	Azure Functions act as the backend/server
	•	Google Routes API provides exact travel data
	•	OpenAI enhances output and communication

This makes the system more maintainable, scalable, and closer to a real production workflow.

⸻

🧪 Example Request
{
  "from_address": "Boston, MA",
  "to_address": "Cambridge, MA",
  "move_size": "1 bedroom",
  "boxes": "10",
  "stairs": "false",
  "elevator": "true"
}
Example Response Structure
{
  "base_to_from": {
    "status": "OK",
    "minutes": 18,
    "miles": 6.4
  },
  "to_to_base": {
    "status": "OK",
    "minutes": 22,
    "miles": 7.1
  },
  "total_travel_minutes": 40,
  "base_recommendation": {
    "crew_base": "2 movers",
    "truck_base": "18ft truck",
    "labor_low": 3.0,
    "labor_high": 5.0
  },
  "ai_result": {
    "status": "OK",
    "estimate_text": "Customer-facing estimate email"
  }
}
🔐 Security

All sensitive values are handled through environment variables.

Examples:
	•	GOOGLE_MAPS_API_KEY
	•	OPENAI_API_KEY
	•	OPENAI_MODEL

Important

Do not upload:
	•	real API keys
	•	Azure function access keys
	•	customer emails
	•	private addresses
	•	local.settings.json with real values

📬 Output

The system produces:
	•	travel time data
	•	base moving recommendation
	•	AI-enhanced estimate
	•	customer-ready email text
	•	Google Sheets updates
	•	automated email delivery

  🌍 Real-World Use Case

This project was designed for real moving company operations to reduce manual estimate work and improve consistency in customer communication.

It demonstrates:
	•	backend API design
	•	cloud function architecture
	•	external API integration
	•	workflow automation
	•	practical AI orchestration

🚀 Future Improvements

Possible next steps:
	•	add unit tests
	•	split Python logic into multiple modules
	•	improve retry/error handling
	•	add logging/monitoring
	•	support more move types and pricing rules
	•	add admin dashboard or review interface

	## Screenshots

### Google Form (User Input)
![Google Form](screenshots/googleform.png)

### Google Sheet (Automated Results + Email Output)
![Google Sheet](screenshots/googlesheet.png)

## ⚠️ Environment Variables

This project uses environment variables for security.

You need to configure:

- GOOGLE_MAPS_API_KEY
- OPENAI_API_KEY

Azure Function URL should also be configured in Apps Script.