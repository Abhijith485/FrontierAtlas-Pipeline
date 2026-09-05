import pandas as pd

# Phase IV: Mock database of known canonical AI startups
CANONICAL_DB = {
    "openai inc": "OpenAI",
    "open ai": "OpenAI",
    "openai, inc.": "OpenAI",
    "anthropic pbc": "Anthropic",
    "anthropic inc": "Anthropic",
    "google llc": "Google",
    "google brain": "Google",
    "meta platforms": "Meta",
    "meta ai": "Meta",
    "hugging face inc": "Hugging Face"
}

def resolve_entity(raw_name):
    # Normalize: lowercase and strip whitespace
    clean_name = str(raw_name).lower().strip()
    return CANONICAL_DB.get(clean_name, raw_name)

def main():
    print("Running Entity Resolution Engine...")
    
    # Simulating messy data found in the wild
    messy_data = ["OpenAI, Inc.", "Open AI", "Anthropic PBC", "Google LLC", "Unknown AI Startup"]
    
    log_data = []
    for raw in messy_data:
        canonical = resolve_entity(raw)
        log_data.append({
            "Raw Extracted Name": raw,
            "Resolved Canonical Name": canonical
        })
        print(f"Mapped: '{raw}' -> '{canonical}'")
        
    # Save the mapping log for the Google Sheets submission
    df = pd.DataFrame(log_data)
    df.to_csv("entity_mapping_log.csv", index=False)
    print("\nSuccess! Saved to 'entity_mapping_log.csv'")

if __name__ == "__main__":
    main()