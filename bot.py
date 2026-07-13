import time, requests, os
from jobspy import scrape_jobs
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

BASE_RESUME = """KARAN SHAH
📞 8879430860
📧 karanshah2402@gmail.com
📍 Kandivali West, Mumbai

PROFESSIONAL SUMMARY
Results-driven derivatives trader with hands-on experience in futures and options markets. Skilled in executing and managing complex options strategies, including delta hedging and volatility-based trades. Strong analytical mindset with a solid foundation in financial markets and risk management.

WORK EXPERIENCE
Silver Stream Equities Pvt. Ltd.
Trader – Derivatives Market | Oct 2024 – Present
- Actively trading in futures and options within the derivatives market
- Executing delta hedging strategies to manage risk exposure
- Implementing advanced options strategies including straddle, strangle, condor, and volatility-based trades
- Analyzing market movements and implied volatility to optimize trading decisions

Deputy Manager – Institutional Desk | Kotak Securities | Sep 2023 – Oct 2024
- Managed institutional dealing operations for options and cash futures, servicing AMC, DII, and FII clients
- Collaborated with sales and research teams to optimise trade execution strategies
- Operated Greeksoft trading terminal for institutional dealing and Omnesys for order execution
- Executed cash-futures arbitrage strategies using Greeksoft terminal

Derivatives Trader | Silver Stream Equities Pvt. Ltd. | Mar 2022 – Aug 2023
- Specialising in options strategy construction including straddles, strangles, and butterfly spreads
- Developed systematic implied volatility-based trading approach
- Executed delta-neutral positions using multi-leg hedging, managing Greeks risk

CORE SKILLS
Futures & Options Trading, Delta Hedging, Options Greeks, Implied Volatility Analysis, Institutional Client Execution, Greeksoft & Omnesys Terminals, NISM Series VIII & XV

EDUCATION & CERTIFICATIONS
Company Secretary (CS) – ICSI, M.Com & B.Com – Mumbai University
NISM Series XV – Research Analyst, NISM Series VIII – Equity Derivatives"""

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})

def tailor_resume(jd_text, company, role):
    prompt = f"""You are an expert resume writer for Institutional Trading/Dealer roles in India.
    Rewrite this resume to match the JD. Keep 100% truthful. Add ATS keywords: Institutional Dealing, Cash, F&O, Greeksoft, Omnesys, NISM VIII, AMC, DII, FII, Arbitrage.

    BASE RESUME: {BASE_RESUME}
    TARGET ROLE: {role} at {company}
    JOB DESCRIPTION: {jd_text}

    Output only the tailored resume in markdown, max 1 page."""
    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
    return res.choices[0].message.content

job_titles = ["Institutional Dealer", "Institutional Equity Dealer", "Institutional Trader"]
seen_jobs = set()

send_telegram("✅ Karan Job Bot Started! I will check for new jobs every 3 hours.")

while True:
    for title in job_titles:
        jobs = scrape_jobs(site_name=["naukri", "indeed"], search_term=title, location="Mumbai, India", hours_old=48)
        for _, job in jobs.iterrows():
            if job['job_url'] not in seen_jobs:
                seen_jobs.add(job['job_url'])
                try:
                    tailored = tailor_resume(job['description'], job['company'], job['title'])
                    msg = f"""🔔 *New Job Match*

*Role*: {job['title']}
*Company*: {job['company']}
*Location*: {job['location']}
*Apply Link*: {job['job_url']}

*Tailored Resume for this role:*
{tailored}"""
                    send_telegram(msg)
                except Exception as e:
                    send_telegram(f"Error tailoring job: {e}")
    time.sleep(10800) # 3 hours
