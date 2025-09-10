import os
import re
import json
import datetime

#  Sample Invoices (parsed)
invoices = [
    {
        "vendor": "Amazon",
        "invoice_number": "INV-0012",
        "invoice_date": "2025-08-20",
        "due_date": "2025-09-05",
        "total": 2450.00,
    },
    {
        "vendor": "Microsoft",
        "invoice_number": "INV-0043",
        "invoice_date": "2025-08-25",
        "due_date": "2025-09-10",
        "total": 3100.00,
    },
]

#  Rule-based engine
def answer_with_rules(query, invoices):
    q = query.lower()
    today = datetime.date.today()

    # how many invoices due in next N days?
    m = re.search(r"next\s+(\d+)\s+days", q)
    if "how many invoices are due" in q and m:
        days = int(m.group(1))
        cutoff = today + datetime.timedelta(days=days)
        due_list = [
            inv
            for inv in invoices
            if today <= datetime.date.fromisoformat(inv["due_date"]) <= cutoff
        ]
        if not due_list:
            return f"0 invoices due in the next {days} days."
        lines = [
            f"{len(due_list)} invoice{'s' if len(due_list)>1 else ''}:\n"
            + "\n".join(
                [
                    f"- {inv['vendor']}, due {inv['due_date']}, ${inv['total']:,.2f}"
                    for inv in due_list
                ]
            )
        ]
        return "\n".join(lines)

    # total value of invoice from vendor
    m = re.search(r"total value of the invoice from\s+([a-zA-Z0-9 ]+)", q)
    if m:
        vendor = m.group(1).strip().lower()
        invs = [inv for inv in invoices if inv["vendor"].lower() == vendor]
        if not invs:
            return f"No invoice found from {m.group(1).strip()}."
        tot = sum(inv["total"] for inv in invs)
        return f"${tot:,.2f}"

    # listing vendors with invoices > X
    m = re.search(r"invoices\s*>\s*\$?([0-9,]+(?:\.\d+)?)", q)
    if "vendors" in q and m:
        amt = float(m.group(1).replace(",", ""))
        invs = [inv for inv in invoices if inv["total"] > amt]
        if not invs:
            return f"No vendors with invoices > ${amt:,.2f}."
        return ", ".join([f"{inv['vendor']} (${inv['total']:,.0f})" for inv in invs])

    # listing all vendors
    if "list" in q and "vendors" in q:
        return ", ".join([f"{inv['vendor']} (${inv['total']:,.2f})" for inv in invoices])

    return (
        "Sorry — I couldn't parse that. Try asking:\n"
        "- How many invoices are due in the next 7 days?\n"
        "- What is the total value of the invoice from Amazon?\n"
        "- List all vendors with invoices > $2,000."
    )

#  LLM engine (OpenAI) 
def answer_with_openai(query, invoices):
    try:
        import openai

        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            return None, "No API key set."
        openai.api_key = key

        system = "You are an assistant that answers invoice-related questions."
        user_prompt = f"Here is the parsed invoice data:\n```json\n{json.dumps(invoices, indent=2)}\n```\n\nQuestion: {query}\nAnswer concisely."

        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
            temperature=0,
            max_tokens=200,
        )
        ans = resp["choices"][0]["message"]["content"].strip()
        return ans, None
    except Exception as e:
        return None, str(e)

#  Unified query function 
def answer_query(query, invoices):
    if os.environ.get("OPENAI_API_KEY"):
        ans, err = answer_with_openai(query, invoices)
        if ans:
            return ans + " [via LLM]"
    return answer_with_rules(query, invoices) + " [via rules]"

#  Main loop 
if __name__ == "__main__":
    print("💬 Invoice Chatbot Ready!")
    print("Type 'exit' to quit.\n")
    while True:
        q = input("Q: ")
        if q.lower() in {"exit", "quit"}:
            break
        print("A:", answer_query(q, invoices))
