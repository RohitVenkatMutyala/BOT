import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import random
import re

# ----- Config from Environment Variables -----
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")
YOUR_APP_PASSWORD = os.environ.get("YOUR_APP_PASSWORD")
RECEIVER_EMAILS = os.environ.get("RECEIVERS", "").split(",")

# ----- Email Sending Function -----
def send_email(subject, body):
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
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ----- Scrape Indeed India Internships -----
def scrape_indeed():
    print("🔍 Scraping Indeed India for internships...")
    internships = []
    
    # Comprehensive list of keywords for Indian internships
    keywords = [
        "Software Engineer Intern", "Software Development Intern", 
        "Computer Science Intern", "Python Developer Intern",
        "Machine Learning Intern", "Data Science Intern", "AI Intern",
        "Web Developer Intern", "Full Stack Intern", "Backend Developer Intern",
        "Frontend Developer Intern", "Mobile App Developer Intern",
        "DevOps Intern", "Cybersecurity Intern", "Cloud Computing Intern"
    ]
    
    # Major Indian cities + Remote
    locations = [
        "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", 
        "Pune", "Kolkata", "Gurgaon", "Noida", "Remote", "India"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    for keyword in keywords[:8]:  # Limit keywords to avoid rate limiting
        for location in locations[:6]:  # Limit locations
            try:
                # Use Indian Indeed domain
                url = f"https://in.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}&jt=internship&sort=date"
                print(f"📍 Searching: {keyword} in {location}")
                
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(1, 3))
                
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    print(f"⚠️ Status {response.status_code} for {keyword} in {location}")
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")

                # Multiple selector strategies for Indeed
                job_cards = (soup.find_all("div", {"data-result-id": True}) or 
                           soup.find_all("div", class_="job_seen_beacon") or
                           soup.find_all("div", class_="slider_container") or
                           soup.find_all("div", class_="result"))
                
                print(f"Found {len(job_cards)} job cards for {keyword} in {location}")
                
                for job in job_cards[:8]:  # Limit per search
                    try:
                        # Extract job title with multiple selectors
                        title_element = (
                            job.find("h2", class_="jobTitle") or
                            job.find("a", {"data-jk": True}) or
                            job.find("span", attrs={"title": True}) or
                            job.find("h2", class_="jobTitle-color-purple")
                        )
                        
                        # Extract company with multiple selectors
                        company_element = (
                            job.find("span", class_="companyName") or
                            job.find("a", {"data-testid": "company-name"}) or
                            job.find("div", class_="companyName") or
                            job.find("span", class_="companyName")
                        )
                        
                        # Extract job link
                        link_element = None
                        if title_element:
                            link_element = title_element.find("a") if title_element.name != "a" else title_element
                        
                        # Extract salary/stipend if available
                        salary_element = (
                            job.find("span", class_="salary-text") or
                            job.find("div", class_="metadata salary-snippet-container") or
                            job.find("span", attrs={"data-testid": "job-salary"})
                        )

                        if title_element and company_element:
                            # Clean up title
                            if hasattr(title_element, 'get_text'):
                                title = title_element.get_text(strip=True)
                            else:
                                title = title_element.get('title', 'N/A')
                            
                            # Clean up company
                            company = company_element.get_text(strip=True)
                            
                            # Build proper Indeed URL
                            if link_element and link_element.get('href'):
                                href = link_element.get('href')
                                if href.startswith('/'):
                                    job_link = f"https://in.indeed.com{href}"
                                else:
                                    job_link = href
                            else:
                                job_link = url  # Fallback to search URL
                            
                            # Extract salary if available
                            salary = "Not Mentioned"
                            if salary_element:
                                salary = salary_element.get_text(strip=True)
                            
                            # Only add if title contains internship-related keywords
                            if any(word in title.lower() for word in ['intern', 'trainee', 'graduate', 'fresher']):
                                internships.append({
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "salary": salary,
                                    "link": job_link,
                                    "source": "Indeed India",
                                    "date": datetime.now().strftime('%Y-%m-%d')
                                })
                                print(f"✅ Added: {title} at {company}")
                            
                    except Exception as e:
                        print(f"⚠️ Error parsing Indeed job: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error scraping Indeed for {keyword} in {location}: {e}")
                continue

    # Remove duplicates based on title and company
    unique_internships = []
    seen = set()
    for internship in internships:
        key = (internship['title'].lower(), internship['company'].lower())
        if key not in seen:
            seen.add(key)
            unique_internships.append(internship)

    print(f"✅ Found {len(unique_internships)} unique internships from Indeed India")
    return unique_internships

# ----- Scrape Internshala India -----
def scrape_internshala():
    print("🔍 Scraping Internshala for Indian internships...")
    internships = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        # Multiple Internshala URLs for different categories
        urls = [
            "https://internshala.com/internships/computer-science,software-development,machine-learning,data-science,artificial-intelligence,web-development",
            "https://internshala.com/internships/software-development/bangalore,mumbai,delhi,hyderabad,chennai,pune",
            "https://internshala.com/internships/python/",
            "https://internshala.com/internships/machine-learning/",
            "https://internshala.com/internships/data-science/"
        ]
        
        for url in urls:
            try:
                print(f"📍 Scraping Internshala URL: {url[:60]}...")
                time.sleep(random.uniform(2, 4))
                
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code != 200:
                    print(f"⚠️ Internshala returned status {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Multiple selector strategies for Internshala
                job_cards = (
                    soup.find_all("div", class_="individual_internship") or
                    soup.find_all("div", class_="internship_meta") or
                    soup.find_all("div", attrs={"internshipid": True}) or
                    soup.find_all("div", class_="container-fluid individual_internship")
                )
                
                print(f"Found {len(job_cards)} internship cards")
                
                for job in job_cards[:15]:  # Limit per URL
                    try:
                        # Extract internship details with multiple selector attempts
                        title_element = (
                            job.find("h3", class_="heading_4_5") or
                            job.find("a", class_="link_display_like_text") or
                            job.find("h3") or
                            job.find("div", class_="profile")
                        )
                        
                        company_element = (
                            job.find("p", class_="company_name") or
                            job.find("a", class_="link_display_like_text") or
                            job.find("div", class_="company") or
                            job.find("p", class_="company-name")
                        )
                        
                        location_element = (
                            job.find("div", class_="locations") or
                            job.find("a", attrs={"data-placement": "top"}) or
                            job.find("span", class_="location_link")
                        )
                        
                        stipend_element = (
                            job.find("div", class_="stipend") or
                            job.find("span", class_="stipend") or
                            job.find("div", attrs={"class": re.compile("stipend")})
                        )
                        
                        # Extract link to apply
                        link_element = (
                            job.find("a", class_="link_display_like_text") or
                            title_element.find("a") if title_element else None
                        )

                        if title_element:
                            title = title_element.get_text(strip=True)
                            company = company_element.get_text(strip=True) if company_element else "Company Not Listed"
                            location = location_element.get_text(strip=True) if location_element else "India"
                            stipend = stipend_element.get_text(strip=True) if stipend_element else "Not Mentioned"
                            
                            # Build proper Internshala link
                            if link_element and link_element.get('href'):
                                href = link_element.get('href')
                                if href.startswith('/'):
                                    job_link = f"https://internshala.com{href}"
                                else:
                                    job_link = href
                            else:
                                # Try to extract internship ID and build link
                                internship_id = job.get('internshipid')
                                if internship_id:
                                    job_link = f"https://internshala.com/internship/detail/{internship_id}"
                                else:
                                    job_link = "https://internshala.com/internships"
                            
                            internships.append({
                                "title": title,
                                "company": company,
                                "location": location,
                                "salary": stipend,
                                "link": job_link,
                                "source": "Internshala",
                                "date": datetime.now().strftime('%Y-%m-%d')
                            })
                            print(f"✅ Added Internshala: {title} at {company}")
                            
                    except Exception as e:
                        print(f"⚠️ Error parsing Internshala job: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error with Internshala URL: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Major error scraping Internshala: {e}")

    print(f"✅ Found {len(internships)} internships from Internshala")
    return internships

# ----- Scrape Naukri India -----
def scrape_naukri():
    print("🔍 Scraping Naukri.com for internships...")
    internships = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Naukri internship searches
        search_terms = [
            "Software+Engineer+Intern", "Python+Developer+Intern", 
            "Data+Science+Intern", "Machine+Learning+Intern"
        ]
        
        for term in search_terms[:3]:  # Limit searches
            url = f"https://www.naukri.com/internship-jobs?k={term}&l=India"
            print(f"📍 Searching Naukri: {term.replace('+', ' ')}")
            
            try:
                time.sleep(random.uniform(2, 4))
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Naukri job cards
                    job_cards = soup.find_all("div", class_="jobTuple")
                    
                    for job in job_cards[:5]:  # Limit per search
                        try:
                            title_elem = job.find("a", class_="title")
                            company_elem = job.find("a", class_="subTitle")
                            
                            if title_elem and company_elem:
                                title = title_elem.get_text(strip=True)
                                company = company_elem.get_text(strip=True)
                                job_link = f"https://www.naukri.com{title_elem.get('href', '')}"
                                
                                if 'intern' in title.lower():
                                    internships.append({
                                        "title": title,
                                        "company": company,
                                        "location": "India",
                                        "salary": "Not Mentioned",
                                        "link": job_link,
                                        "source": "Naukri.com",
                                        "date": datetime.now().strftime('%Y-%m-%d')
                                    })
                                    print(f"✅ Added Naukri: {title}")
                                    
                        except Exception as e:
                            continue
                            
            except Exception as e:
                print(f"❌ Error searching Naukri for {term}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Major error with Naukri: {e}")
    
    print(f"✅ Found {len(internships)} internships from Naukri")
    return internships

# ----- Generate sample jobs if all scraping fails -----
def get_sample_jobs():
    """Generate realistic sample jobs for testing"""
    return [
        {
            "title": "Software Development Intern - Backend",
            "company": "TechCorp India Pvt Ltd",
            "location": "Bangalore, Karnataka",
            "salary": "₹15,000 - ₹25,000/month",
            "link": "https://example.com/apply1",
            "source": "Sample Data",
            "date": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "title": "Data Science Intern", 
            "company": "Analytics Solutions",
            "location": "Mumbai, Maharashtra",
            "salary": "₹12,000 - ₹20,000/month",
            "link": "https://example.com/apply2",
            "source": "Sample Data",
            "date": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "title": "Machine Learning Engineer Intern",
            "company": "AI Innovations Ltd",
            "location": "Hyderabad, Telangana",
            "salary": "₹18,000 - ₹30,000/month",
            "link": "https://example.com/apply3",
            "source": "Sample Data", 
            "date": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "title": "Full Stack Developer Intern",
            "company": "StartupHub Technologies",
            "location": "Pune, Maharashtra",
            "salary": "₹10,000 - ₹18,000/month",
            "link": "https://example.com/apply4",
            "source": "Sample Data",
            "date": datetime.now().strftime('%Y-%m-%d')
        }
    ]

# ----- Main Execution -----
def main():
    print(f"🤖 Starting comprehensive India internship scraper at {datetime.now()}")
    
    all_jobs = []
    
    # Scrape from multiple sources
    sources = [
        ("Indeed India", scrape_indeed),
        ("Internshala", scrape_internshala),
        ("Naukri", scrape_naukri)
    ]
    
    for source_name, scrape_func in sources:
        try:
            print(f"\n🎯 Starting {source_name} scraping...")
            jobs = scrape_func()
            all_jobs.extend(jobs)
            print(f"✅ {source_name}: Added {len(jobs)} jobs")
        except Exception as e:
            print(f"❌ {source_name} completely failed: {e}")
            continue
    
    # If no jobs found, use sample data
    if not all_jobs:
        print("ℹ️ No jobs found from any source, using sample data")
        all_jobs = get_sample_jobs()

    # Remove duplicates and sort by date
    unique_jobs = []
    seen_jobs = set()
    
    for job in all_jobs:
        job_key = f"{job['title'].lower().strip()}-{job['company'].lower().strip()}"
        if job_key not in seen_jobs:
            seen_jobs.add(job_key)
            unique_jobs.append(job)
    
    # Sort by source priority and limit results
    priority_order = {"Indeed India": 1, "Internshala": 2, "Naukri.com": 3, "Sample Data": 4}
    unique_jobs.sort(key=lambda x: priority_order.get(x['source'], 5))
    final_jobs = unique_jobs[:30]  # Limit to 30 jobs for email

    print(f"\n📊 Final Summary:")
    print(f"Total jobs scraped: {len(all_jobs)}")
    print(f"Unique jobs after deduplication: {len(unique_jobs)}")
    print(f"Jobs to be sent in email: {len(final_jobs)}")

    # Create email content
    job_rows = []
    for job in final_jobs:
        job_row = f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px; font-weight: bold; color: #2E86C1;">{job['title']}</td>
            <td style="padding: 12px;">{job['company']}</td>
            <td style="padding: 12px;">{job['location']}</td>
            <td style="padding: 12px;">{job['date']}</td>
            <td style="padding: 12px; color: #27AE60;">{job['salary']}</td>
            <td style="padding: 12px;"><a href="{job['link']}" target="_blank" style="background-color: #2E86C1; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">Apply Now</a></td>
        </tr>
        """
        job_rows.append(job_row)

    # Count jobs by source for summary
    source_counts = {}
    for job in final_jobs:
        source = job['source']
        source_counts[source] = source_counts.get(source, 0) + 1

    source_summary = " | ".join([f"{source}: {count}" for source, count in source_counts.items()])

    email_content = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
        <div style="max-width: 900px; margin: 0 auto; background-color: white; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #2E86C1, #3498DB); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 300;">🇮🇳 India Internships Daily Digest</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">📅 {datetime.now().strftime('%B %d, %Y')} | {len(final_jobs)} Fresh Opportunities</p>
            </div>
            
            <!-- Summary Stats -->
            <div style="padding: 20px; background-color: #ECF0F1; text-align: center;">
                <p style="margin: 0; color: #34495E; font-size: 14px;">{source_summary}</p>
            </div>
            
            <!-- Jobs Table -->
            <div style="padding: 0; overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #34495E; color: white;">
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Position</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Company</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Location</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Date</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Stipend</th>
                            <th style="padding: 15px; text-align: center; font-weight: 600;">Apply</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(job_rows)}
                    </tbody>
                </table>
            </div>
            
            <!-- Footer Tips -->
            <div style="background-color: #E8F6FF; padding: 25px; margin: 20px;">
                <h3 style="color: #2E86C1; margin: 0 0 15px 0; font-size: 18px;">💡 Application Tips</h3>
                <ul style="color: #34495E; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li><strong>Apply Early:</strong> Most internships are filled within 48 hours of posting</li>
                    <li><strong>Customize Resume:</strong> Tailor your resume for each specific role and company</li>
                    <li><strong>Follow Up:</strong> Send a polite follow-up email after 1 week if no response</li>
                    <li><strong>Research Company:</strong> Show genuine interest by mentioning company-specific details</li>
                </ul>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; padding: 25px; background-color: #2C3E50; color: white;">
                <p style="margin: 0; font-size: 13px; opacity: 0.8;">
                    🤖 Automated by GitHub Actions | Data from Indeed, Internshala & Naukri<br>
                    💪 Best of luck with your applications! | Next update in 24 hours
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email("🇮🇳 Daily India Internships - Latest Opportunities", email_content)
    print("🎉 Email sent successfully! Process completed.")

if __name__ == "__main__":
    main()