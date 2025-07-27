# AI-Powered Test Strategist

A Python-based command-line tool that transforms high-level user requirements into comprehensive test plans and ready-to-use test data using the power of Google's Gemini AI.

This project bridges the gap between product requirements and QA testing by automating the most time-consuming parts of the test design process: creating scenarios and generating data.

## Key Features

-   **AI-Driven Test Planning:** Provide a simple requirement (e.g., "a login form"), and the tool generates a complete test plan with positive, negative, and edge case scenarios.
-   **Context-Aware Data Generation:** For each scenario in the plan, the AI generates specific, relevant test data rows.
-   **Intelligent Row Count:** Let the AI decide the optimal number of test data rows needed for good coverage by simply typing 'ideal'.
-   **Dual File Output:** Automatically generates two CSV files:
    1.  A **full report** with test data and scenario metadata for analysis.
    2.  A **clean data-only file**, perfectly formatted for use in automation tools like Postman or Bruno.
-   **Interactive CLI:** A user-friendly, interactive command-line interface guides you through the entire process.

## Demo

*(It is highly recommended to record a short GIF or video of the tool in action and embed it here. A tool like Giphy Capture or Kap is great for this.)*

![Demo GIF Placeholder](https://via.placeholder.com/800x400.png?text=Showcase+A+GIF+Of+Your+Tool+Here)

## 🛠️ Tech Stack

-   **Language:** Python 3
-   **AI Model:** Google Gemini
-   **Core Libraries:**
    -   `google-generativeai` for interacting with the Gemini API.
    -   `pandas` for structuring and saving data.
    -   `python-dotenv` for secure management of API keys.

## Setup and Usage

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/Amuthan07/AI_Powered_Test_Strategist]
cd AI_Powered_Test_Strategist
```

### 2. Create a Virtual Environment (Recommended)

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

First, create a `requirements.txt` file by running this command in your terminal. This file lists all the libraries your project needs.

```bash
pip freeze > requirements.txt
```

Now, anyone (including you on a new machine) can install the required packages easily:

```bash
pip install -r requirements.txt
```

### 4. Set Up Your API Key

Create a file named `.env` in the root of the project directory and add your Gemini API key to it:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Script

Now you're all set! Run the tool with the following command:

```bash
python test_strategist.py
```

The script will then guide you through the interactive prompts to generate your test plan and data.