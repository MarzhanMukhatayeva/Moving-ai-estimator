🚚 Moving AI Estimator

An end-to-end automated system for generating moving cost estimates and sending them directly to customers.

Built using Google Forms, Google Apps Script, Azure Functions (Python), Google Routes API, and OpenAI.

⸻

📌 Project Overview

This project automates the full process of generating moving estimates.

A customer submits move details through a Google Form, and the system:
	•	calculates travel time
	•	estimates labor based on real business logic
	•	calculates pricing deterministically in Python
	•	generates a professional estimate email using AI
	•	automatically sends the estimate to the customer

This simulates a real-world backend system used in logistics and service businesses.

⸻
## 🏗 Architecture

Frontend: Google Forms  
Processing: Google Apps Script  
Backend: Azure Functions (Python)  
APIs: Google Routes API, OpenAI API  
Storage: Google Sheets  


🔄 System Workflow
Customer
   ↓
Google Form (input data)
   ↓
Google Sheets (stores responses)
   ↓
Google Apps Script (trigger on submit)
   ↓
Azure Function (Python backend)
   ├── Google Routes API → Travel Time
   ├── Business Logic → Labor Estimate
   ├── Price Calculation → Final Cost
   └── OpenAI → Email generation
   ↓
Google Apps Script
   ↓
📧 Email sent to customer automatically

⚙️ Core Features
	•	📍 Automatic travel time calculation (Google Routes API)
	•	🧠 Deterministic labor estimation (Python logic)
	•	💰 Accurate price calculation (NOT AI-based)
	•	🤖 AI-generated professional estimate email
	•	📧 Automatic email delivery to customer
	•	🔄 Fully automated pipeline from form submission to client response

	💰 Pricing Logic (Python)

Pricing is calculated entirely in Python using deterministic logic.

How it works:
	•	Base labor time depends on apartment size
	•	Additional time is added for:
	•	number of boxes
	•	stairs
	•	lack of elevator
	•	Travel time is calculated separately using Google Routes API

Formula:
Total Time = Labor Time + Travel Time
Price = Total Time × Hourly Rate

Example:
Labor time: 4.0–6.0 hours
Travel time: 35 minutes
Total time: 4.6–6.6 hours
Rate: $129/hr
Estimated price: $600–$850

🤖 Role of AI

AI is NOT used for calculations.

Instead, OpenAI is used to:
	•	generate clear, customer-friendly estimates
	•	explain factors like stairs, elevator, and complexity
	•	format the output as a professional email

⸻

📧 Automated Email System

After form submission:
	1.	Data is processed in Azure
	2.	Travel time and pricing are calculated
	3.	AI generates a professional estimate message
	4.	Google Apps Script automatically sends the email to the customer

This replicates a real-world automated customer response system.

⸻

🧠 Technologies Used
	•	Python (Azure Functions)
	•	Google Apps Script
	•	Google Forms / Google Sheets
	•	Google Routes API
	•	OpenAI API

⸻

📂 Project Structure
azure-function/
   function_app.py       # Backend logic (travel, pricing, AI)
   host.json

apps-script/
   code.js               # Form trigger + email automation

screenshots/
   googleform.png
   googlesheet.png

🔐 Environment Variables
GOOGLE_MAPS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=your_model

🚀 Example Output (Email)
Hi,

Thank you for reaching out to Seven Moving.

For this 1-bedroom move, our recommendation is 2 movers with an 18ft truck.

Estimated labor time: 4–6 hours  
Travel time: 35 minutes  
Estimated total time: 4.5–6.5 hours  

At the current rate, the estimated price range is $600–$850.

Please note this is a preliminary estimate and may vary depending on inventory, building access, stairs, elevator, and parking.

Best regards,  
 
Moving company  

## ⚙️ Challenges & Solutions

- Google Maps API errors (REQUEST_DENIED, routing issues)
  → Fixed by enabling correct APIs and billing configuration

- Data inconsistencies between Apps Script and Azure
  → Standardized JSON structure and logging

- Ensuring deterministic pricing
  → Separated business logic from AI components

👤 Author

Marzhan Mukhatayeva
