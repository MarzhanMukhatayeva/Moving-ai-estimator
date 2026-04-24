# 🚚 Moving AI Estimator

An automated moving cost estimation system built using Google Forms, Google Apps Script, Azure Functions (Python), Google Routes API, and OpenAI.

---

## 📌 Project Overview

This project automates the process of estimating moving costs by collecting customer data through a Google Form and processing it through a backend system hosted on Azure.

The system calculates travel time, analyzes move details, and generates a smart estimate.

---
## 🔄 System Workflow
```markdown
## 🔄 System Architecture

The system follows an event-driven architecture:

```text
[Customer]
    ↓
[Google Form]
    ↓
[Google Sheets]
    ↓ (onFormSubmit trigger)
[Google Apps Script]
    ↓ (HTTP request)
[Azure Function (Python API)]
    ├── Calls Google Routes API → Travel Time
    ├── Applies Estimate Logic
    └── (Optional) Calls OpenAI API → Natural language output
    ↓
[Processed Result]
    ↓
[Google Sheets Output]

```text
Customer submits moving details
        ↓
Google Form collects the information
        ↓
Google Sheets stores the form response
        ↓
Google Apps Script detects a new submission
        ↓
Apps Script sends the data to Azure Function
        ↓
Azure Function processes the request
        ↓
Google Routes API calculates travel time
        ↓
Estimate logic calculates crew size, labor time, and pricing
        ↓
The result is written back to Google Sheets
## ⚙️ How It Works

1. Customer submits a Google Form
2. Google Apps Script triggers on form submission
3. Data is sent to an Azure Function (Python)
4. Azure Function:
   - Calculates travel time using Google Maps API
   - Processes move details (apartment size, stairs, boxes)
   - Generates estimate logic
5. Results are returned to Google Sheets

---

## 🧠 Technologies Used

- Python (Azure Functions)
- Google Apps Script
- Google Forms / Google Sheets
- Google Routes API
- OpenAI API

---

## 📂 Project Structure
azure-function/     # Backend logic (Python)
apps-script/        # Google Apps Script integration
screenshots/        # Project screenshots

---

## 🔐 Environment Variables
GOOGLE_MAPS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

---

## 🚀 Features

- Automated travel time calculation
- Dynamic moving cost estimation
- Google Forms integration
- Real-time data processing
- Scalable cloud backend (Azure)

---

## 📸 Screenshots

(Add your screenshots here)

---

## 💡 Future Improvements

- Email automation with estimates
- UI dashboard
- Pricing optimization using AI

---

## 👤 Author

Marzhan Mukhatayeva
