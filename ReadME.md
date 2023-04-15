# Job Compatibility FInder - Job Scraper
This project is a job scraper that asks the user to enter a job category and preferred location. Then, it scrapes two job websites ([Internshala] and [TimesJob]) using the given data. The scraped job postings are displayed in a user-friendly Flask UI. The goal of this project is to provide a quick and easy way for users to search for job postings based on their preferred job category and location.

### _Steps_
1. Run ```virtualenv venv``` to create a python virtual environment.
2. Run ```venv\Scripts\activate``` on windows or ```source ./venv/bin/activate``` on linux to activate the created virtual environment.
3. Run ```pip install Flask``` to install flask.
4. Keep the file structure as provided:
```
path/
|--static/
|  |--css/
|  |  |--cssfile.css
|  |--js/
|  |  |--jsfile.js
|--templates/
|  |--htmlfile.html
|--app.py
```
5. Run the ```app.py``` file

### _Requirements_
1. Python3
2. Flask

### Disclaimer
The data displayed in this project is scraped from Internshala and Timesjob. We do not own the data nor are we affiliated with the respective websites in any way. The data is provided solely for informational purposes and we do not endorse or validate the accuracy of the data. We do not have any control over the data or how it is used by third parties. We respect the terms of use, robots.txt files, and any other guidelines or restrictions that are in place to protect the websites' data. We do not encourage or condone any unauthorized access to the websites or their data. Users of this project should use the data at their own risk and discretion.

[//]: #
[Internshala]: <https://internshala.com/>
[TimesJob]: <https://www.timesjobs.com/>