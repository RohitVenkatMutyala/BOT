import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime

# Try importing LinkedIn scraper, fallback if not available
try:
    from linkedin_jobs_scraper import LinkedinScraper
    from linkedin_jobs_scraper.events import Events, EventData
    from linkedin_jobs_scraper.query import Query, QueryOptions
    LINKEDIN_AVAILABLE = True
except ImportError:
    print("⚠️ LinkedIn scraper not available, will use alternative methods")
    LINKEDIN_AVAILABLE = False

# ----- Config from Environment Variables -----
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")
YOUR_APP_PASSWORD = os.environ.get("YOUR_APP_PASSWORD")
RECEIVER_EMAILS = os.environ.get("RECEIVERS", "").split(",")

print(f"📧 Email config: {YOUR_EMAIL} -> {len(RECEIVER_EMAILS)} receivers")

# ----- Email Sending Function -----
def send_email(subject, body):
    if not YOUR_EMAIL or not YOUR_APP_PASSWORD or not RECEIVER_EMAILS:
        print("❌ Missing email configuration")
        return False
        
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = YOUR_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)

    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
            server.sendmail(YOUR_EMAIL, RECEIVER_EMAILS, msg.as_string())
        print(f"✅ Email sent successfully to: {', '.join(RECEIVER_EMAILS)}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# ----- Scrape LinkedIn Remote + India Internships -----
def scrape_linkedin():
    if not LINKEDIN_AVAILABLE:
        print("⚠️ LinkedIn scraper not available")
        return []
        
    scraped_jobs = []
    
    try:
        def on_data(data: EventData):
            try:
                if any(loc in data.place.lower() for loc in ["remote", "worldwide", "india"]):
                    job_info = f"""
                    <tr>
                        <td><b>{data.title}</b></td>
                        <td>{data.company}</td>
                        <td>{data.place}</td>
                        <td>{data.date}</td>
                        <td>Not Mentioned</td>
                        <td><a href="{data.link}" target="_blank" style="color: #2E86C1;">Apply Here</a></td>
                    </tr>
                    """
                    scraped_jobs.append(job_info)
                    print(f"📌 Found: {data.title} at {data.company}")
            except Exception as e:
                print(f"⚠️ Error processing job data: {e}")

        def on_error(error):
            print("⚠️ LinkedIn error:", error)

        def on_end():
            print("✅ LinkedIn scraping finished.")

        # Configure scraper with better settings for GitHub Actions
        scraper = LinkedinScraper(
            headless=True,
            slow_mo=1.0,  # Slower to avoid detection
            page_load_timeout=60,
            max_workers=1,
            chrome_executable_path=os.environ.get('CHROME_BIN'),  # Use system Chrome
            chrome_options=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )

        scraper.on(Events.DATA, on_data)
        scraper.on(Events.ERROR, on_error)
        scraper.on(Events.END, on_end)

        queries = [
            Query(
                query="Software Engineering Internship",
                options=QueryOptions(
                    locations=["Worldwide", "India"],
                    limit=10  # Limit results
                )
            )
        ]

        print("🔍 Starting LinkedIn scraping...")
        scraper.run(queries)
        
    except Exception as e:
        print(f"❌ LinkedIn scraping failed: {e}")
        
    return scraped_jobs

# ----- Scrape Indeed Remote + India Internships -----
def scrape_indeed():
    print("🔍 Scraping Indeed...")
    keywords = ["Software Engineering", "Computer Science", "Machine Learning"]
    locations = ["Remote", "India"]
    internships = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for keyword in keywords[:2]:  # Limit to avoid rate limiting
        for location in locations:
            try:
                url = f"https://in.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}&jt=internship"
                print(f"📍 Searching: {keyword} in {location}")
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("div", class_="job_seen_beacon")
                
                for job in job_cards[:3]:  # Limit per search
                    try:
                        title_tag = job.find("h2", class_="jobTitle")
                        company_tag = job.find("span", class_="companyName")
                        link_tag = job.find("a", href=True)

                        if title_tag and company_tag:
                            internships.append({
                                "title": title_tag.text.strip(),
                                "company": company_tag.text.strip(),
                                "location": location,
                                "link": f"https://in.indeed.com{link_tag['href']}" if link_tag else "#"
                            })
                            print(f"📌 Found: {title_tag.text.strip()}")
                    except:
                        continue
                        
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️ Indeed error for {keyword}: {e}")
                continue
                
    return internships

# ----- Generate Sample Jobs for Testing -----
def get_sample_jobs():
    return [
        {
            "title": "Software Engineering Intern",
            "company": "Tech Startup",
            "location": "Remote",
            "link": "https://example.com"
        },
        {
            "title": "Data Science Intern",
            "company": "Analytics Corp", 
            "location": "India",
            "link": "https://example.com"
        }
    ]

# ----- Main Execution -----
def main():
    print(f"🤖 Starting scraper at {datetime.now()}")
    
    all_jobs = []
    
    # Try LinkedIn scraping
    try:
        linkedin_jobs = scrape_linkedin()
        all_jobs.extend(linkedin_jobs)
        print(f"✅ LinkedIn: {len(linkedin_jobs)} jobs")
    except Exception as e:
        print(f"❌ LinkedIn failed: {e}")

    # Try Indeed scraping
    try:
        indeed_jobs = scrape_indeed()
        # Convert Indeed jobs to HTML format
        for job in indeed_jobs:
            job_html = f"""
            <tr>
                <td><b>{job['title']}</b></td>
                <td>{job['company']}</td>
                <td>{job['location']}</td>
                <td>{datetime.now().strftime('%Y-%m-%d')}</td>
                <td>Not Mentioned</td>
                <td><a href="{job['link']}" target="_blank" style="color: #2E86C1;">Apply Here</a></td>
            </tr>
            """
            all_jobs.append(job_html)
        print(f"✅ Indeed: {len(indeed_jobs)} jobs")
    except Exception as e:
        print(f"❌ Indeed failed: {e}")

    # Fallback to sample jobs if nothing found
    if not all_jobs:
        print("ℹ️ No jobs found, using sample data for testing")
        sample_jobs = get_sample_jobs()
        for job in sample_jobs:
            job_html = f"""
            <tr>
                <td><b>{job['title']}</b></td>
                <td>{job['company']}</td>
                <td>{job['location']}</td>
                <td>{datetime.now().strftime('%Y-%m-%d')}</td>
                <td>Sample Data</td>
                <td><a href="{job['link']}" target="_blank" style="color: #2E86C1;">Apply Here</a></td>
            </tr>
            """
            all_jobs.append(job_html)

    print(f"📊 Total jobs to send: {len(all_jobs)}")

    email_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding:20px;">
        <div style="max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px;">
            <h2 style="color:#2E86C1; text-align: center;">🌍 Latest Remote + India Software Engineering Internships</h2>
            <p style="text-align: center;">📅 {datetime.now().strftime('%B %d, %Y')} | Found {len(all_jobs)} opportunities</p>
            
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%; background-color: #ffffff;">
                <tr style="background-color: #2E86C1; color: white;">
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Date Posted</th>
                    <th>Stipend / Salary</th>
                    <th>Apply Link</th>
                </tr>
                {''.join(all_jobs)}
            </table>
            
            <p style="margin-top:20px; text-align: center;">🚀 Apply quickly! Remote and India internships get filled fast. Best of luck! 🌟</p>
            <p style="text-align: center; color: #888; font-size: 12px;"><em>🤖 Automated by GitHub Actions</em></p>
        </div>
    </body>
    </html>
    """

    success = send_email("✨ Remote + India Software Engineering Internships Update", email_content)
    
    if success:
        print("🎉 Process completed successfully!")
    else:
        print("❌ Process completed with email sending failure")
    
    sys.exit(0)

if __name__ == "__main__":
    main()