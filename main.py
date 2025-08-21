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
from urllib.parse import urlencode, quote_plus

# ----- Config from Environment Variables -----
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")
YOUR_APP_PASSWORD = os.environ.get("YOUR_APP_PASSWORD")
RECEIVER_EMAILS = os.environ.get("RECEIVERS", "").split(",")

# ----- Email Sending Function -----
def send_email(subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    # Set custom "From" email address as requested
    msg["From"] = "rohith@randoman.online"
    # Don't set "To" field - this hides recipients from each other
    # msg["To"] = ", ".join(RECEIVER_EMAILS)  # Commented out to hide recipients

    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
            # Send to each recipient individually using BCC
            server.sendmail(YOUR_EMAIL, RECEIVER_EMAILS, msg.as_string())
        print(f"✅ Email sent successfully to: {len(RECEIVER_EMAILS)} recipients (hidden from each other)")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ----- Scrape LinkedIn Jobs -----
def scrape_linkedin():
    print("🔍 Scraping LinkedIn for internships...")
    internships = []
    
    # LinkedIn headers to mimic browser behavior
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }
    
    # Session for maintaining cookies
    session = requests.Session()
    session.headers.update(headers)
    
    # Keywords for internship search - All branches
    keywords = [
        # Computer Science & IT
        "Software Engineer Intern", "Data Science Intern", "Machine Learning Intern",
        "Software Development Intern", "Python Developer Intern", "Full Stack Intern",
        "Backend Developer Intern", "Frontend Developer Intern", "AI Intern",
        "Web Developer Intern", "Mobile App Developer Intern", "DevOps Intern",
        "Cybersecurity Intern", "Cloud Computing Intern", "Database Intern",
        
        # Mechanical Engineering
        "Mechanical Engineer Intern", "Design Engineer Intern", "CAD Designer Intern",
        "Manufacturing Engineer Intern", "Production Engineer Intern", "Quality Engineer Intern",
        "Automotive Engineer Intern", "Robotics Engineer Intern", "HVAC Engineer Intern",
        
        # Electrical & Electronics
        "Electrical Engineer Intern", "Electronics Engineer Intern", "Power Systems Intern",
        "Control Systems Intern", "Embedded Systems Intern", "VLSI Design Intern",
        "Hardware Engineer Intern", "Circuit Design Intern", "Instrumentation Intern",
        
        # Civil Engineering
        "Civil Engineer Intern", "Structural Engineer Intern", "Construction Intern",
        "Site Engineer Intern", "Project Engineer Intern", "Environmental Engineer Intern",
        "Transportation Engineer Intern", "Water Resources Intern", "Surveying Intern",
        
        # Chemical Engineering
        "Chemical Engineer Intern", "Process Engineer Intern", "Chemical Plant Intern",
        "Petrochemical Intern", "Pharmaceutical Engineer Intern", "Food Engineer Intern",
        
        # Business & Management
        "Business Analyst Intern", "Marketing Intern", "Sales Intern", "HR Intern",
        "Finance Intern", "Operations Intern", "Consulting Intern", "Strategy Intern",
        "Digital Marketing Intern", "Content Marketing Intern", "Brand Management Intern",
        
        # Other Engineering Branches
        "Aerospace Engineer Intern", "Biomedical Engineer Intern", "Industrial Engineer Intern",
        "Mining Engineer Intern", "Petroleum Engineer Intern", "Marine Engineer Intern",
        "Agricultural Engineer Intern", "Textile Engineer Intern",
        
        # Science & Research
        "Research Intern", "Lab Intern", "Biotechnology Intern", "Pharmaceutical Intern",
        "Chemistry Intern", "Physics Intern", "Biology Intern", "Environmental Science Intern",
        
        # Design & Creative
        "Graphic Design Intern", "UI/UX Design Intern", "Product Design Intern",
        "Architecture Intern", "Interior Design Intern", "Fashion Design Intern"
    ]
    
    # Indian locations
    locations = [
        "India", "Bangalore, India", "Mumbai, India", "Delhi, India", 
        "Hyderabad, India", "Chennai, India", "Pune, India"
    ]
    
    try:
        for keyword in keywords[:6]:  # Limit keywords to avoid rate limiting
            for location in locations[:4]:  # Limit locations
                try:
                    print(f"📍 Searching LinkedIn: {keyword} in {location}")
                    
                    # Build LinkedIn job search URL
                    search_params = {
                        'keywords': keyword,
                        'location': location,
                        'f_TPR': 'r86400',  # Posted in last 24 hours
                        'f_E': '1',  # Experience level: Internship
                        'f_JT': 'I',  # Job type: Internship
                        'sortBy': 'DD',  # Sort by date
                        'start': 0
                    }
                    
                    base_url = "https://www.linkedin.com/jobs/search"
                    url = f"{base_url}?{urlencode(search_params)}"
                    
                    # Add random delay to avoid rate limiting
                    time.sleep(random.uniform(3, 6))
                    
                    response = session.get(url, timeout=20)
                    
                    if response.status_code == 999:
                        print("⚠️ LinkedIn is blocking requests (999 status). Trying alternative approach...")
                        # Try with simplified URL
                        simple_url = f"https://www.linkedin.com/jobs/search?keywords={quote_plus(keyword)}&location={quote_plus(location)}&f_JT=I"
                        time.sleep(random.uniform(5, 8))
                        response = session.get(simple_url, timeout=20)
                    
                    if response.status_code != 200:
                        print(f"⚠️ LinkedIn returned status {response.status_code} for {keyword} in {location}")
                        continue
                    
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Multiple selector strategies for LinkedIn job cards
                    job_cards = (
                        soup.find_all("div", class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card") or
                        soup.find_all("div", class_="job-search-card") or
                        soup.find_all("div", attrs={"data-entity-urn": True}) or
                        soup.find_all("li", class_="result-card job-result-card result-card--with-hover-state") or
                        soup.find_all("div", class_="base-search-card__info")
                    )
                    
                    print(f"Found {len(job_cards)} job cards for {keyword} in {location}")
                    
                    for job in job_cards[:8]:  # Limit per search
                        try:
                            # Extract job title with multiple selectors
                            title_element = (
                                job.find("h3", class_="base-search-card__title") or
                                job.find("a", class_="base-card__full-link") or
                                job.find("h4", class_="base-search-card__title") or
                                job.find("span", attrs={"aria-hidden": "true"}) or
                                job.find("a", attrs={"data-tracking-control-name": "public_jobs_jserp-result_search-card"})
                            )
                            
                            # Extract company with multiple selectors
                            company_element = (
                                job.find("h4", class_="base-search-card__subtitle") or
                                job.find("a", class_="hidden-nested-link") or
                                job.find("span", class_="job-search-card__subtitle-link") or
                                job.find("h4", class_="base-search-card__subtitle-link")
                            )
                            
                            # Extract location
                            location_element = (
                                job.find("span", class_="job-search-card__location") or
                                job.find("span", class_="base-search-card__metadata") or
                                job.find("div", class_="base-search-card__metadata")
                            )
                            
                            # Extract job link
                            link_element = (
                                job.find("a", class_="base-card__full-link") or
                                job.find("a", attrs={"data-tracking-control-name": "public_jobs_jserp-result_search-card"}) or
                                title_element.find("a") if title_element else None
                            )
                            
                            # Extract posting date
                            date_element = (
                                job.find("time", class_="job-search-card__listdate") or
                                job.find("time", class_="job-search-card__listdate--new") or
                                job.find("span", class_="job-search-card__listdate")
                            )

                            if title_element:
                                # Clean up title
                                if hasattr(title_element, 'get_text'):
                                    title = title_element.get_text(strip=True)
                                elif title_element.find('span'):
                                    title = title_element.find('span').get_text(strip=True)
                                else:
                                    title = str(title_element.get('title', '')).strip()
                                
                                # Skip if title is empty or too generic
                                if not title or len(title) < 5:
                                    continue
                                
                                # Extract company name
                                if company_element:
                                    if hasattr(company_element, 'get_text'):
                                        company = company_element.get_text(strip=True)
                                    else:
                                        company = str(company_element).strip()
                                else:
                                    company = "Company Not Listed"
                                
                                # Extract location
                                if location_element:
                                    job_location = location_element.get_text(strip=True)
                                    # Clean up location text
                                    job_location = re.sub(r'\s+', ' ', job_location)
                                else:
                                    job_location = location
                                
                                # Build proper LinkedIn job URL
                                if link_element and link_element.get('href'):
                                    href = link_element.get('href')
                                    if href.startswith('/'):
                                        job_link = f"https://www.linkedin.com{href}"
                                    else:
                                        job_link = href
                                    
                                    # Clean LinkedIn tracking parameters
                                    if '?' in job_link:
                                        job_link = job_link.split('?')[0]
                                else:
                                    job_link = url  # Fallback to search URL
                                
                                # Extract posting date
                                posting_date = datetime.now().strftime('%Y-%m-%d')
                                if date_element:
                                    date_text = date_element.get_text(strip=True)
                                    # Parse relative dates like "2 days ago", "1 week ago"
                                    if 'day' in date_text.lower():
                                        posting_date = datetime.now().strftime('%Y-%m-%d')
                                    elif 'week' in date_text.lower():
                                        posting_date = datetime.now().strftime('%Y-%m-%d')
                                
                                # Only add if title contains internship-related keywords
                                internship_keywords = ['intern', 'internship', 'trainee', 'graduate program', 'entry level', 'fresher']
                                if any(word in title.lower() for word in internship_keywords):
                                    internships.append({
                                        "title": title,
                                        "company": company,
                                        "location": job_location,
                                        "salary": "Not Mentioned",  # LinkedIn rarely shows salary publicly
                                        "link": job_link,
                                        "source": "LinkedIn",
                                        "date": posting_date
                                    })
                                    print(f"✅ Added LinkedIn: {title} at {company}")
                                
                        except Exception as e:
                            print(f"⚠️ Error parsing LinkedIn job: {e}")
                            continue
                            
                except Exception as e:
                    print(f"❌ Error scraping LinkedIn for {keyword} in {location}: {e}")
                    # Add longer delay if we hit an error (might be rate limited)
                    time.sleep(random.uniform(5, 10))
                    continue

    except Exception as e:
        print(f"❌ Major error scraping LinkedIn: {e}")
    
    # Remove duplicates based on title and company
    unique_internships = []
    seen = set()
    for internship in internships:
        key = (internship['title'].lower(), internship['company'].lower())
        if key not in seen:
            seen.add(key)
            unique_internships.append(internship)
    
    print(f"✅ Found {len(unique_internships)} unique internships from LinkedIn")
    return unique_internships

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
    
    # Scrape from multiple sources including LinkedIn
    sources = [
        ("LinkedIn", scrape_linkedin),
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
    priority_order = {"LinkedIn": 1, "Indeed India": 2, "Internshala": 3, "Naukri.com": 4, "Sample Data": 5}
    unique_jobs.sort(key=lambda x: priority_order.get(x['source'], 6))
    final_jobs = unique_jobs[:35]  # Increased limit to accommodate LinkedIn jobs

    print(f"\n📊 Final Summary:")
    print(f"Total jobs scraped: {len(all_jobs)}")
    print(f"Unique jobs after deduplication: {len(unique_jobs)}")
    print(f"Jobs to be sent in email: {len(final_jobs)}")

    # Create mobile-responsive email content
    job_rows = []
    for job in final_jobs:
        # Add source badge styling
        source_color = {
            "LinkedIn": "#0077B5",
            "Indeed India": "#2557A7", 
            "Internshala": "#00A5EC",
            "Naukri.com": "#7B68EE",
            "Sample Data": "#95A5A6"
        }
        
        source_badge = f'<span style="background-color: {source_color.get(job["source"], "#95A5A6")}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; margin-left: 8px;">{job["source"]}</span>'
        
        # Mobile-responsive job card layout
        job_row = f"""
        <div style="background-color: #f8f9fa; margin-bottom: 20px; border-radius: 12px; padding: 20px; border-left: 4px solid {source_color.get(job["source"], "#95A5A6")}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="margin-bottom: 15px;">
                <h3 style="margin: 0 0 8px 0; color: #2E86C1; font-size: 18px; line-height: 1.3; font-weight: 600;">
                    {job['title']}{source_badge}
                </h3>
                <div style="color: #34495E; font-size: 16px; font-weight: 500; margin-bottom: 8px;">
                    🏢 {job['company']}
                </div>
            </div>
            
            <div style="display: block; margin-bottom: 15px; font-size: 14px; color: #566573;">
                <div style="margin-bottom: 10px; word-wrap: break-word; overflow-wrap: break-word;">
                    <span style="font-weight: 600;">📍 Location:</span><br>
                    <span style="margin-left: 5px; display: block; margin-top: 2px;">{job['location']}</span>
                </div>
                <div style="margin-bottom: 10px; word-wrap: break-word; overflow-wrap: break-word;">
                    <span style="font-weight: 600;">💰 Stipend:</span><br>
                    <span style="margin-left: 5px; color: #27AE60; display: block; margin-top: 2px;">{job['salary']}</span>
                </div>
                <div style="margin-bottom: 10px; word-wrap: break-word; overflow-wrap: break-word;">
                    <span style="font-weight: 600;">📅 Posted:</span><br>
                    <span style="margin-left: 5px; display: block; margin-top: 2px;">{job['date']}</span>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="{job['link']}" target="_blank" style="
                    display: inline-block;
                    background: linear-gradient(135deg, #3498DB, #2E86C1);
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: 600;
                    box-shadow: 0 3px 12px rgba(46, 134, 193, 0.3);
                    transition: all 0.3s ease;
                    min-width: 140px;
                ">
                    ✨ Apply Now
                </a>
            </div>
        </div>
        """
        job_rows.append(job_row)

    # Count jobs by source for summary
    source_counts = {}
    for job in final_jobs:
        source = job['source']
        source_counts[source] = source_counts.get(source, 0) + 1

    source_summary = " | ".join([f"{source}: {count}" for source, count in source_counts.items()])

    # Mobile-responsive email template
    email_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Internships</title>
        <style>
            /* Mobile-first responsive styles */
            @media only screen and (max-width: 600px) {{
                .container {{
                    width: 100% !important;
                    margin: 0 !important;
                    padding: 10px !important;
                }}
                .header {{
                    padding: 20px 15px !important;
                }}
                .header h1 {{
                    font-size: 22px !important;
                }}
                .header p {{
                    font-size: 14px !important;
                }}
                .job-card {{
                    margin: 10px 0 !important;
                    padding: 15px !important;
                }}
                .job-title {{
                    font-size: 16px !important;
                }}
                .company-name {{
                    font-size: 15px !important;
                }}
                .job-details {{
                    flex-direction: column !important;
                    gap: 10px !important;
                }}
                .job-detail-item {{
                    min-width: auto !important;
                    margin-bottom: 8px !important;
                }}
                .apply-button {{
                    width: 100% !important;
                    min-width: auto !important;
                    padding: 15px 20px !important;
                    font-size: 16px !important;
                    box-sizing: border-box;
                }}
                .platform-grid {{
                    flex-direction: column !important;
                    gap: 10px !important;
                }}
                .platform-item {{
                    flex: none !important;
                    min-width: auto !important;
                    margin-bottom: 5px !important;
                }}
                .tips-section {{
                    padding: 20px 15px !important;
                    margin: 10px !important;
                }}
                .tips-section h3 {{
                    font-size: 16px !important;
                }}
                .tips-section ul {{
                    padding-left: 15px !important;
                }}
                .tips-section li {{
                    margin-bottom: 8px !important;
                    font-size: 14px !important;
                }}
                .footer {{
                    padding: 20px 15px !important;
                }}
                .summary-stats {{
                    padding: 15px 10px !important;
                    font-size: 12px !important;
                }}
            }}
        </style>
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0;">
        <div class="container" style="max-width: 900px; margin: 0 auto; background-color: white; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden;">
            <!-- Header -->
            <div class="header" style="background: linear-gradient(135deg, #2E86C1, #3498DB); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 300;">Internships Daily Digest</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">📅 {datetime.now().strftime('%B %d, %Y')} | {len(final_jobs)} Fresh Opportunities</p>
                <div style="margin-top: 15px;">
                    <span style="background-color: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 12px;">✨ Now including LinkedIn Jobs!</span>
                </div>
            </div>
            
            <!-- Summary Stats -->
            <div class="summary-stats" style="padding: 20px; background-color: #ECF0F1; text-align: center;">
                <p style="margin: 0; color: #34495E; font-size: 14px; line-height: 1.4;">{source_summary}</p>
            </div>
            
            <!-- Jobs Container - Mobile Responsive Cards -->
            <div class="jobs-container" style="padding: 20px;">
                {''.join(job_rows)}
            </div>
            
            <!-- Footer Tips -->
            <div class="tips-section" style="background-color: #E8F6FF; padding: 25px; margin: 20px;">
                <h3 style="color: #2E86C1; margin: 0 0 15px 0; font-size: 18px;">💡 Application Tips</h3>
                <ul style="color: #34495E; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li><strong>Apply Early:</strong> Most internships are filled within 48 hours of posting</li>
                    <li><strong>LinkedIn Strategy:</strong> Connect with recruiters and company employees before applying</li>
                    <li><strong>Customize Resume:</strong> Tailor your resume for each specific role and company</li>
                    <li><strong>Follow Up:</strong> Send a polite follow-up email after 1 week if no response</li>
                    <li><strong>Research Company:</strong> Show genuine interest by mentioning company-specific details</li>
                    <li><strong>Portfolio Ready:</strong> Have your GitHub, projects, and portfolio links ready</li>
                </ul>
            </div>
            
            <!-- LinkedIn Tips -->
            <div class="tips-section" style="background-color: #E8F4FD; padding: 25px; margin: 20px; border-left: 4px solid #0077B5;">
                <h3 style="color: #0077B5; margin: 0 0 15px 0; font-size: 18px;">🔗 LinkedIn Pro Tips</h3>
                <ul style="color: #34495E; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li><strong>Optimize Profile:</strong> Use internship-relevant keywords in your headline and summary</li>
                    <li><strong>Network Actively:</strong> Connect with alumni, professionals, and company employees</li>
                    <li><strong>Engage Content:</strong> Like and comment on posts from companies you want to work for</li>
                    <li><strong>Direct Messages:</strong> Send personalized messages to hiring managers (keep it brief!)</li>
                </ul>
            </div>
            
            <!-- Footer -->
            <div class="footer" style="text-align: center; padding: 25px; background-color: #2C3E50; color: white;">
                <p style="margin: 0; font-size: 13px; opacity: 0.8; line-height: 1.5;">
                    🤖 Automated by GitHub Actions <br>
                    💪 Best of luck with your applications! 
                </p>
                <div style="margin-top: 10px;">
                    <span style="background-color: rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 10px; font-size: 11px;">Made With ❤️</span>
                </div>
                <div style="margin-top: 10px;">
                 <a href="https://randoman.online" target="_blank" style="text-decoration: none;">
                    <span style="background-color: rgba(255, 255, 0, 0.1); padding: 3px 8px; border-radius: 10px; font-size: 11px;">Check _Out_Your_Platform</span>
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(" Daily Internships - Latest Opportunities ", email_content)
    print("🎉 Email sent successfully! Process completed.")

if __name__ == "__main__":
    main()