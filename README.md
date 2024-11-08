Python Survey Data Processing Application
This project is a backend web application built with Python using the Sanic framework. The application processes survey data, calculates statistical summaries, stores the results in a database, and generates insights based on the survey answers. It also includes a CI/CD pipeline for automated testing and quality assurance.

Features
Survey Data Processing: Processes survey data and calculates statistical summaries (mean, median, standard deviation).
Statistical Insights: Analyzes survey responses and generates insights like overall_analysis, cat_dog, fur_value, and tail_value.
Data Storage: Stores processed survey results and calculated statistics in a NoSQL database (choose your preferred DB).
Asynchronous Operations: Ensures efficient asynchronous data processing and storage.
CI/CD Pipeline: Configured with GitHub Actions to automatically run unit tests and enforce test coverage.
Error Handling & Logging: Robust error handling and detailed logging for easy debugging.
Prerequisites
Before you begin, ensure you have the following installed:

Python 3.7+
Git
pip (Python package installer)
Optional Tools
Docker (for containerization)
Virtual environment tools (e.g., venv or virtualenv)
Setup
1. Clone the repository:
bash
Copy code
git clone <repository_url>
cd <project_directory>
2. Create a virtual environment:
If you're using venv (replace educhamp with your preferred name):

bash
Copy code
python -m venv educhamp
source educhamp/bin/activate  # For Linux/Mac
educhamp\Scripts\activate  # For Windows
3. Install dependencies:
bash
Copy code
pip install -r requirements.txt
4. Set up the database:
Ensure that the database connection is configured correctly in your app folder. This may require setting environment variables or configuring a .env file.

5. Run the application:
bash
Copy code
python app/main.py
This will start the Sanic server, and you can access the API at http://127.0.0.1:8000.

Running Tests
To run the unit tests:

bash
Copy code
pytest
This will run all the unit tests in the tests directory.

Test Coverage:
The application has been set up with automated testing, and the CI/CD pipeline ensures that the tests are run automatically with at least 80% coverage.

CI/CD
This project is integrated with GitHub Actions for continuous integration and delivery. The pipeline is configured to automatically run the unit tests on every push to the main branch and ensure that the code meets quality standards.

To trigger the CI/CD pipeline:
Push your code to the main branch.
GitHub Actions will automatically run the workflow defined in .github/workflows/ci.yml.
Folder Structure
app/: Contains the backend application files.
tests/: Contains test files to ensure the application functions correctly.
.github/: Contains the CI/CD pipeline configuration files.
requirements.txt: Lists the required Python packages for the project.
.gitignore: Specifies files and directories to ignore in Git version control.