# Invoice Chatbot Assignment

This project implements a small chatbot that can read invoices and answer basic questions such as:

- "How many invoices are due in the next 7 days?"
- "What is the total value of the invoice from Amazon?"
- "List all vendors with invoices > $2000."

## Files

- `invoice_chatbot.py` — main chatbot script
- `parsed_invoices.json` — sample invoices data
- `README.md` — this file

## How to Run

1. Install dependencies (optional for LLM):
   ```bash
   pip install openai
   ```

2. (Optional) Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

3. Run the chatbot:
   ```bash
   python invoice_chatbot.py
   ```


