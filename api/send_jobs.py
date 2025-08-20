import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions
from bs4 import BeautifulSoup
import requests

# ----- Configuration -----
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")
YOUR_APP_PASSWORD = os.environ.get("YOUR_APP_PASSWORD")
RECEIVER_EMAILS = os.environ.get("RECEIVERS", "").split(",")

# ----- Email Sending Function -----
def send_email(subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = YOUR_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
            server.sendmail(YOUR_EMAIL, RECEIVER_EMAILS, msg.as_string())
        print(f"✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ----- LinkedIn Scraper -----
def scrape_linkedin():
    scraped_jobs = []

    def on_data(data: EventData):
        if "remote" in data.place.lower() or "worldwide" in data.place.lower() or "india" in data.place.lower():
            job_info = f"""
            <tr>
                <td><b>{data.title}</b></td>
                <td>{data.company}</td>
                <td>{data.place}</td>
                <td>{data.date}</td>
                <td>Not Mentioned</td>
                <td><a href="{data.link}" target="_blank">Apply Here</a></td>
            </tr>
            """
            scraped_jobs.append(job_info)

    scraper = LinkedinScraper(headless=True, slow_mo=0.5, max_workers=1)
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, lambda e: print("⚠️", e))
    scraper.on(Events.END, lambda: print("✅ LinkedIn scraping finished."))

    queries = [Query("Software Engineering Internship", options=QueryOptions(locations=["Worldwide","India"]))]

    scraper.run(queries)  # synchronous
    return scraped_jobs

# ----- Indeed Scraper -----
def scrape_indeed():
    keywords = ["Software Engineering", "Computer Science", "Machine Learning", "AI"]
    locations = ["Remote", "India"]
    internships = []

    for keyword in keywords:
        for location in locations:
            url = f"https://www.indeed.com/jobs?q={keyword.replace(' ','+')}&l={location.replace(' ','+')}&jt=internship"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("div", class_="job_seen_beacon")
            for job in job_cards:
                title_tag = job.find("h2", class_="jobTitle")
                company_tag = job.find("span", class_="companyName")
                link_tag = job.find("a", href=True)
                if title_tag and company_tag and link_tag:
                    internships.append({
                        "title": title_tag.text.strip(),
                        "company": company_tag.text.strip(),
                        "location": location,
                        "link": "https://www.indeed.com" + link_tag["href"]
                    })
    return internships

# ----- Vercel HTTP Handler -----
def handler(request, response):
    linkedin_jobs = scrape_linkedin()
    indeed_jobs = scrape_indeed()

    all_jobs = linkedin_jobs.copy()
    for job in indeed_jobs:
        all_jobs.append(f"""
        <tr>
            <td><b>{job['title']}</b></td>
            <td>{job['company']}</td>
            <td>{job['location']}</td>
            <td>Not Mentioned</td>
            <td>Not Mentioned</td>
            <td><a href="{job['link']}" target="_blank">Apply Here</a></td>
        </tr>
        """)

    if not all_jobs:
        return response.json({"message": "No Remote + India internships found."})

    email_content = f"""
    <html>
    <body>
        <h2>🌍 Latest Remote + India Software Engineering Internships</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>Job Title</th>
                <th>Company</th>
                <th>Location</th>
                <th>Date Posted</th>
                <th>Stipend / Salary</th>
                <th>Apply Link</th>
            </tr>
            {''.join(all_jobs)}
        </table>
    </body>
    </html>
    """

    send_email("✨ Remote + India Software Engineering Internships Update", email_content)
    return response.json({"message": "Email sent successfully!"})
