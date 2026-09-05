from google import genai
import json

# Initialize the Gemini client with your key
client = genai.Client(api_key="AQ.Ab8RN6L2_51pJEnUmNJBiHtoDmBgXiBbdH-O5FG0DG3D4rINfw")

def extract_startup_data(raw_html_text):
    """Uses Gemini to extract structured startup data from messy text."""
    
    prompt = f"""
    You are an expert data extraction algorithm. 
    Analyze the following raw text scraped from a website and extract the startup's details.
    
    If you cannot find a piece of information, return null for that field.
    Respond ONLY with a valid JSON object matching this exact schema:
    {{
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "content": {{
            "entityName": "Canonical Name of the Startup",
            "data": {{
                "employeeCount": Integer
            }}
        }}
    }}
    
    Raw Text to Analyze:
    {raw_html_text}
    """
    
    try:
        print("Sending data to Gemini LLM...")
        # UPGRADED TO 3.6-FLASH
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        
        # Strip markdown formatting markers if present
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1]
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("\n", 1)[0]
            
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"LLM Extraction failed: {e}")
        return None

# --- Test the Engine ---
if __name__ == "__main__":
    messy_website_text = """
    Welcome to the official page for Anthropic! We are an AI safety and research company based in San Francisco. 
    Our team recently grew to over 300 employees dedicated to building reliable, interpretable, and steerable AI systems.
    """
    
    print("Testing LLM Extraction Engine...")
    result = extract_startup_data(messy_website_text)
    
    if result:
        print("\n--- AI Structured Output ---")
        print(json.dumps(result, indent=4))