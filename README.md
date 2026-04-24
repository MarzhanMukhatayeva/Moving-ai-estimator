🚚 Moving AI Estimator

An automated moving cost estimation system built using Google Forms, Google Apps Script, Azure Functions (Python), Google Routes API, and OpenAI.

⸻

📌 Project Overview

This project automates the process of generating moving estimates.

Customers submit move details through a Google Form, and the system:
	•	calculates travel time
	•	applies business logic for labor estimation
	•	computes pricing deterministically in Python
	•	generates a professional, customer-ready estimate using AI

The goal is to reduce manual work, improve consistency, and simulate a real-world logistics backend system.

⸻

🔄 System Workflow
Customer
   ↓
Google Form (input data)
   ↓
Google Sheets (stores responses)
   ↓
Google Apps Script (trigger)
   ↓
Azure Function (Python backend)
   ├── Google Routes API → Travel Time
   ├── Business Logic → Labor Estimate
   ├── Price Calculation → Final Cost
   └── OpenAI → Customer-friendly explanation
   ↓
Results returned to Google Sheets
Core Features
	•	📍 Automatic travel time calculation (Google Routes API)
	•	🧠 Deterministic labor estimation (Python logic)
	•	💰 Accurate price calculation (not AI-based)
	•	🤖 AI-generated professional estimate text
	•	🔄 Fully automated pipeline from form → result

⸻

🧠 Technologies Used
	•	Python (Azure Functions)
	•	Google Apps Script
	•	Google Forms / Google Sheets
	•	Google Routes API
	•	OpenAI API

⸻

💰 Pricing Logic (Important)

Pricing is calculated entirely in Python, not by AI.

Logic:
	•	Base labor time depends on:
	•	apartment size
	•	Additional time is added for:
	•	number of boxes
	•	stairs
	•	lack of elevator
	•	Travel time is calculated separately
	•	Total billable time:
    total time = labor time + travel time
    Final price:
    price = total time × hourly rate

    Example Output:
    Labor time: 4.0–6.0 hours
Travel time: 35 minutes
Total time: 4.6–6.6 hours
Rate: $129/hr
Estimated price: $600–$850

🤖 Role of AI

AI is NOT used for calculations.

Instead, OpenAI is used to:
	•	generate clean, human-readable estimates
	•	explain the reasoning (stairs, elevator, etc.)
	•	format output as a professional email

⸻

📂 Project Structure
azure-function/
   function_app.py       # Main backend logic
   host.json

apps-script/
   code.js               # Google Apps Script trigger

screenshots/
   googleform.png
   googlesheet.png

   🔐 Environment Variables
   GOOGLE_MAPS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=your_model

🚀 Example Output
Hi,

Thank you for reaching out to Seven Moving.

For this 1-bedroom move, our recommendation is 2 movers with an 18ft truck.

Estimated labor time: 4–6 hours  
Travel time: 35 minutes  
Estimated total time: 4.5–6.5 hours  

At the current rate, the estimated price range is $600–$850.

Please note this is a preliminary estimate and may vary based on inventory and building access.

Best regards,    
Seven Moving  

💡 Future Improvements
	•	📧 Automatic email sending to customers
	•	📊 Dashboard for tracking estimates
	•	🧠 Smarter pricing optimization using ML
	•	📱 Frontend UI for customer interaction

⸻

👤 Author

Marzhan Mukhatayeva
:::
