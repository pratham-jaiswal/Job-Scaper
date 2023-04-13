from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_timesjob(keywords, location):
    keywords = keywords.replace(" ","%20").lower()
    location = location.replace(" ","%20").lower()
    df = pd.DataFrame()
    sequence = 1
    job_links = []
    min_salaries = []
    max_salaries = []
    
    while True and sequence<3:
        url = f"https://www.timesjobs.com/candidate/job-search.html?from=submit&actualTxtKeywords={keywords}&searchBy=0&rdoOperator=OR&searchType=personalizedSearch&txtLocation={location}&luceneResultSize=25&postWeek=60&txtKeywords=web%20dev&pDate=I&sequence={sequence}&startPage=1"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        job_titles = [job.text.strip() for job in soup.find_all("h2")]
        if not job_titles:
            break
        job_links = [a.get("href") for h2 in soup.find_all("h2") for a in h2.find_all("a")]
        companies = [company.text.strip().split("\r\n", 1)[0] for company in soup.find_all("h3", class_="joblist-comp-name")]
        dpls = [dpl.text.strip() for dpl in soup.find_all("ul", class_="top-jd-dtl clearfix")]
        
        experiences = []
        salaries = []
        locations = []
        
        for dpl in dpls:
            # Extract years of experience
            experience_match = re.search(r'(\d+\s*-\s*\d+)\s+yrs', dpl)
            if experience_match:
                experience = experience_match.group(1) + " years"
            else:
                experience = "N/A"
            experiences.append(experience)

            # Extract salary range
            salary_match = re.search(r'₹(.+?)\n', dpl)
            if salary_match:
                salary = salary_match.group(1)
            else:
                salary = "N/A"
            salaries.append(salary)

            # Extract locations
            locations_match = re.search(r'location_on\n(.+)', dpl)
            if locations_match:
                locations_list = re.findall(r'\w[\w\s/,-]+', locations_match.group(1))
                locations.append(str(locations_list).replace("[", "").replace("]", "").replace("\'", ""))
            else:
                locations.append("N/A")
        
        min_salary = [salary.split(' - ')[0].replace('Rs', '').strip() if salary != "N/A" else "N/A" for salary in salaries]
        max_salary = [salary.split(' - ')[1].replace('Lacs p.a.', '').strip() if salary != "N/A" else "N/A" for salary in salaries]
        
        df_temp = pd.DataFrame({"Job Title": job_titles[:-1],
                                "Company": companies,
                                "Experience": experiences,
                                "Min Salary (LPA)": min_salary,
                                "Max Salary (LPA)": max_salary,
                                "Location(s)": locations,
                                "Link": job_links})
        
        df = pd.concat([df, df_temp])
        
        sequence += 1
    
    return df.reset_index(drop=True)

def scrape_internshala(keywords, user_location):
    keywords = keywords.replace(" ","-").lower()
    user_location = "-in-"+user_location.replace(" ","-").lower()
    df = pd.DataFrame()
    sequence = 1
    job_links = []
    
    while True and sequence<2:
        url = f"https://internshala.com/jobs/{keywords}-jobs{user_location}/page-{sequence}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        job_titles = [job.text.strip() for job in soup.find_all("h3", class_="heading_4_5 profile")]
        if not job_titles:
            break
        job_links = ["https://internshala.com"+a.get("href") for h3 in soup.find_all("h3", class_="heading_4_5 profile") for a in h3.find_all("a")]
        companies = [company.text.strip() for company in soup.find_all("h4", class_="heading_6 company_name")]
        locations = [location.text.strip() for location in soup.find_all("p", id='location_names')]
        salaries = [salary.text.strip() for salary in soup.find_all("div", class_="item_body salary")]
        
        
        experiences = []
        for _ in salaries:
            experiences.append("Check link for info")
        
        min_salary = [salary.split('-')[0].replace('LPA', '').strip() for salary in salaries]
        max_salary = [salary.split('-')[1].replace('LPA', '').strip() if '-' in salary else "N/A" for salary in salaries]
        
        df_temp = pd.DataFrame({"Job Title": job_titles,
                                "Company": companies,
                                "Experience": experiences,
                                "Min Salary (LPA)": min_salary,
                                "Max Salary (LPA)": max_salary,
                                "Location(s)": locations,
                                "Link": job_links})
        
        df = pd.concat([df, df_temp])
        
        sequence += 1
        
    return df.reset_index(drop=True)

app = Flask(__name__)

# Load the CSV files
categories = pd.read_csv('categories.csv')
locations = pd.read_csv('locations.csv')

@app.route('/')
def index():
    return render_template('index.html', categories=categories.iloc[:,0].tolist(), locations=locations.iloc[:,0].tolist())

@app.route('/search', methods=['POST'])
def search():
    category = request.form['category']
    location = request.form['location']
    sort_by = request.form['sort'] if 'sort' in request.form else None
    filter = request.form['filter'] if 'filter' in request.form else None

    df1 = scrape_timesjob(category, location)
    df2 = scrape_internshala(category, location)
    df = pd.concat([df1, df2]).reset_index(drop=True)
    
    # Sort the dataframe by minimum salary or maximum salary based on the radio button selection
    if sort_by == 'min_salary':
        df = df.sort_values(by='Min Salary (LPA)', ascending=False)
    elif sort_by == 'max_salary':
        df = df.sort_values(by='Max Salary (LPA)', ascending=False)
    
    # Filter out rows with "N/A" minimum salary based on the checkbox selection
    if filter == "exclude_na":
        df = df[df['Min Salary (LPA)'] != 'N/A']

    df.iloc[:, -1] = df.iloc[:, -1].apply(lambda link: '<a href="{}" target="_blank">Click here</a>'.format(link))
    df = df.reset_index(drop=True)
    result = df.to_html(index=False, escape=False)
    return jsonify(df=result)

@app.route('/suggest_categories')
def suggest_categories():
    term = request.args.get('term')

    # Filter the categories that contain the search term
    suggestions = categories[categories['0'].str.lower().str.contains(term.lower())]['0'].tolist()

    return jsonify(suggestions)

@app.route('/suggest_locations')
def suggest_locations():
    term = request.args.get('term')

    # Filter the locations that contain the search term
    suggestions = locations[locations['0'].str.lower().str.contains(term.lower())]['0'].tolist()

    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
