import pandas as pd
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# --- AI Configuration ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in your .env file or environment variables.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("[+] Gemini AI configured successfully.")
except Exception as e:
    print(f"[!] ERROR: Failed to configure Gemini AI: {e}")
    exit()

def get_user_input(prompt: str) -> str:
    """Gets a non-empty input from the user."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("[!] Input cannot be empty. Please try again.")

def generate_test_plan(requirement: str) -> dict:
    """Uses AI to generate a structured test plan."""
    print("\n[*] Generating test plan from your requirement...")
    prompt = f"""
    As an expert QA Test Analyst, analyze the following user requirement and generate a structured test plan in JSON format.
    User Requirement: "{requirement}"
    Your response MUST be a single, valid JSON object with two top-level keys: "fields" (a list of strings) and "scenarios" (a list of objects with keys 'scenario_name', 'test_type', and 'description'), and nothing else.
    """
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        plan = json.loads(json_text)
        print(f"[+] Test plan generated with {len(plan['scenarios'])} scenarios.")
        return plan
    except Exception as e:
        print(f"[!] ERROR: Failed to generate or parse test plan: {e}")
        return None

def get_ideal_row_count(plan: dict) -> int:
    """Uses AI to determine the ideal number of rows to generate."""
    print("\n[*] Analyzing test plan to determine ideal row count...")
    prompt = f"""
    As a QA Lead, analyze the following test plan. Based on the number and variety of scenarios, determine the ideal number of test data rows to generate PER SCENARIO to achieve good test coverage without being excessive.

    Test Plan:
    {json.dumps(plan, indent=2)}

    Your response MUST be a single integer and nothing else. For example: 3
    """
    try:
        response = model.generate_content(prompt)
        ideal_count = int(response.text.strip())
        print(f"[*] AI suggests generating {ideal_count} rows per scenario.")
        return ideal_count
    except Exception as e:
        print(f"    [!] WARNING: Could not determine ideal row count, defaulting to 3. Error: {e}")
        return 3 # Fallback to a sensible default

def generate_data_for_plan(plan: dict, rows_per_scenario: int) -> pd.DataFrame:
    """Generates test data for each scenario in the test plan."""
    print("\n[*] Generating test data for each scenario...")
    all_test_data = []
    fields = plan.get("fields", [])

    for i, scenario in enumerate(plan["scenarios"]):
        scenario_name = scenario["scenario_name"]
        description = scenario["description"]
        test_type = scenario["test_type"]
        
        print(f"  - ({i+1}/{len(plan['scenarios'])}) Generating data for scenario: '{scenario_name}'")
        prompt = f"""
        Generate {rows_per_scenario} unique JSON objects of test data that precisely match the following test scenario.
        Scenario Description: "{description}"
        Each JSON object MUST contain exactly these keys: {json.dumps(fields)}.
        The values you generate for each key should be appropriate for the scenario.
        Your response MUST be a single, valid JSON array containing the {rows_per_scenario} objects, and nothing else.
        """
        try:
            response = model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            generated_rows = json.loads(json_text)
            for row in generated_rows:
                row['scenario_name'] = scenario_name
                row['test_type'] = test_type
            all_test_data.extend(generated_rows)
        except Exception as e:
            print(f"    [!] WARNING: Could not generate data for '{scenario_name}': {e}")
    
    print("[+] Test data generation complete.")
    return pd.DataFrame(all_test_data)

def main():
    """Main interactive loop."""
    print("--- AI-Powered Test Strategist ---")
    requirement = get_user_input("Enter your user requirement (e.g., 'a login form with email and password'):\n> ")
    
    test_plan = generate_test_plan(requirement)
    if not test_plan:
        return

    rows_input = get_user_input("\nHow many rows of data per scenario? (e.g., 5 or type 'ideal'): ")
    if rows_input.lower() in ['ideal', 'ai', 'auto']:
        rows_per_scenario = get_ideal_row_count(test_plan)
    else:
        try:
            rows_per_scenario = int(rows_input)
        except ValueError:
            print("[!] Invalid number, defaulting to 3.")
            rows_per_scenario = 3

    output_filename = get_user_input("Enter a base name for the output CSV file: ")
    if not output_filename.endswith('.csv'):
        output_filename += '.csv'

    df = generate_data_for_plan(test_plan, rows_per_scenario)

    if not df.empty:
        # 1. Save the complete file with scenario metadata
        full_report_filename = output_filename.replace('.csv', '_full_report.csv')
        cols_to_move = ['scenario_name', 'test_type']
        df_full = df[cols_to_move + [col for col in df.columns if col not in cols_to_move]]
        df_full.to_csv(full_report_filename, index=False)
        print(f"\n[+] Full report with scenarios saved to '{full_report_filename}'")

        # 2. Save the "data only" file for automation tools
        data_only_filename = output_filename.replace('.csv', '_data_only.csv')
        data_only_df = df.drop(columns=cols_to_move)
        data_only_df.to_csv(data_only_filename, index=False)
        print(f"[+] Clean data for automation saved to '{data_only_filename}'")

if __name__ == "__main__":
    main()
