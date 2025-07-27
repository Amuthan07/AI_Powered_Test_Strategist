import pandas as pd
from faker import Faker
import random
import os
import google.generativeai as genai

# --- AI Configuration ---
try:
    # Configure the Gemini API key from your environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[!] WARNING: GEMINI_API_KEY environment variable not set. 'ai_text' type will be disabled.")
        gemini_enabled = False
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        gemini_enabled = True
except Exception as e:
    print(f"[!] WARNING: Could not configure Gemini AI. 'ai_text' type will be disabled. Error: {e}")
    gemini_enabled = False


# Initialize Faker
fake = Faker('en_IN')

def generate_ai_content(prompt: str) -> str:
    """Generates content using the Gemini AI based on a prompt."""
    if not gemini_enabled:
        return "AI_DISABLED"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[!] ERROR: AI generation failed: {e}")
        return "AI_GENERATION_ERROR"


# --- core engine for generating different data types ---
TYPE_GENERATORS = {
    "name": {"positive": fake.name, "negative": lambda: random.choice(["", "Name123", "A"*201])},
    "email": {"positive": fake.safe_email, "negative": lambda: "not-an-email"},
    "password": {"positive": lambda: fake.password(length=12), "negative": lambda: "123"},
    "integer": {"positive": fake.random_int, "negative": lambda: random.choice([-1, 999.9, "abc"])},
    "date": {"positive": fake.date, "negative": lambda: "2025-99-99"},
    "uuid": {"positive": fake.uuid4, "negative": lambda: "not-a-uuid"},
    # new AI-powered type. It only has a 'positive' case, as 'negative' is context-dependent.
    "ai_text": {"positive": generate_ai_content, "negative": lambda: "INVALID_AI_PROMPT"},
}


def get_user_input(prompt, type_converter=str, validation=lambda x: True):
    """A helper function to get and validate user input."""
    while True:
        try:
            value = type_converter(input(prompt))
            if validation(value):
                return value
            else:
                print("[!] Invalid input, please try again.")
        except ValueError:
            print("[!] Invalid input, please enter the correct type.")

def build_schema_interactively():
    """Guides the user to build a schema dictionary interactively."""
    print("--- Interactive Schema Builder ---")
    num_fields = get_user_input("How many fields do you want to define? ", int, lambda x: x > 0)
    
    available_types = list(TYPE_GENERATORS.keys())
    print("\nAvailable data types:")
    for i, t in enumerate(available_types, 1):
        print(f"  {i}. {t}")

    fields = {}
    for i in range(num_fields):
        print(f"\n--- Defining Field #{i+1} ---")
        field_name = get_user_input("Enter the name for this field: ")
        
        type_choice_prompt = f"Choose a data type for '{field_name}' (enter number 1-{len(available_types)}): "
        type_index = get_user_input(type_choice_prompt, int, lambda x: 1 <= x <= len(available_types))
        
        field_type = available_types[type_index - 1]
        fields[field_name] = {'type': field_type}

        # If the user chooses 'ai_text', ask for the context prompt
        if field_type == 'ai_text':
            if not gemini_enabled:
                print("Cannot use 'ai_text' as Gemini is not configured. Skipping.")
                continue
            ai_prompt = get_user_input("  > Enter the AI context prompt for this field: ")
            fields[field_name]['prompt'] = ai_prompt

        print(f"[+] Field '{field_name}' set to type '{field_type}'.")

    return {'fields': fields}

def generate_data(schema, num_rows, test_type):
    """Generates test data based on a schema and test type."""
    fields = schema.get('fields', {})
    data = []
    print(f"\n[*] Generating {num_rows} '{test_type}' records...")
    for i in range(num_rows):
        print(f"  - Generating row {i+1}/{num_rows}")
        record = {}
        for field_name, field_config in fields.items():
            field_type = field_config.get('type')
            current_case = test_type if test_type != 'mixed' else random.choice(['positive', 'negative'])
            
            generator_map = TYPE_GENERATORS.get(field_type, {})
            generator_func = generator_map.get(current_case)
            
            if generator_func:
                if field_type == 'ai_text':
                    # Pass the saved prompt to the AI generator
                    prompt = field_config.get('prompt', 'generate random text')
                    record[field_name] = generator_func(prompt)
                else:
                    record[field_name] = generator_func()
            else:
                record[field_name] = f"NO_GENERATOR_FOR_{field_type}_{current_case}"
        data.append(record)
    return pd.DataFrame(data)

def main():
    """Main interactive loop."""
    schema = build_schema_interactively()

    print("\n--- Generation Options ---")
    num_rows = get_user_input("How many rows of data do you want to generate? ", int, lambda x: x > 0)
    test_type_prompt = "Choose test type (1: positive, 2: negative, 3: mixed): "
    test_type_choice = get_user_input(test_type_prompt, int, lambda x: x in [1, 2, 3])
    test_type_map = {1: 'positive', 2: 'negative', 3: 'mixed'}
    test_type = test_type_map[test_type_choice]
    output_filename = get_user_input("Enter a name for the output CSV file: ")
    if not output_filename.endswith('.csv'):
        output_filename += '.csv'

    df = generate_data(schema, num_rows, test_type)

    if not df.empty:
        df.to_csv(output_filename, index=False)
        print(f"\n[+] Success! Data saved to '{output_filename}'")

if __name__ == "__main__":
    main()
