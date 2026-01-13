# HR Bot (Gemini RAG)

An enterprise-grade Slack bot that uses **Retrieval-Augmented Generation (RAG)** to provide instant, grounded answers to HR policy questions. By connecting **Google Gemini** with a **Google Drive** knowledge base, the bot ensures employees get accurate information without HR intervention, while maintaining a human-in-the-loop fallback.

---

## Project Overview
HR departments often spend hours answering the same questions about leave, insurance, and company conduct. This project automates that process:
* **Why this project?** To bridge the gap between static PDF policies and interactive employee support.
* **The Goal:** Reduce HR ticket volume while ensuring 100% accuracy through document-grounded AI.

## Key Features
* **RAG-Powered Intelligence:** Uses Google Gemini to generate answers based *only* on official documents, preventing AI hallucinations.
* **Live Google Drive Integration:** Reads policies directly from a managed Drive folder—no manual database updates needed.
* **Slack-Native Experience:** Employees interact with the bot where they already work.
* **Smart Escalation:** If the AI cannot find an answer, it automatically emails the HR department with the employee's query and contact info.
* **Secure Tunneling:** Uses **ngrok** to bridge the local FastAPI development server with Slack's webhooks.

---

## System Architecture

The data flows through a modern AI pipeline:

1. **User Interaction:** Employee sends a message to the bot in **Slack**.
2. **Webhook Tunneling:** Slack sends a request to the **ngrok** public URL, which routes it to the local **FastAPI** server.
3. **Contextual Retrieval:** The server queries the **Google Drive API** to find relevant text chunks within the HR policy folder.
4. **Augmented Generation:** The user's prompt + retrieved policy text is sent to **Gemini Pro**.
5. **Human Fallback:** If the model determines the answer isn't in the docs, a Python **SMTP** script triggers an email to HR.
6. **Response:** The verified answer is posted back to the Slack thread.



---

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **AI Model:** Google Gemini Pro (Generative AI SDK)
* **API Integrations:** Slack Bolt SDK, Google Drive API
* **Communication:** SMTP for Email Escalation
* **Development Tools:** ngrok (Tunneling), Dotenv (Security)

---
