import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import textwrap
import colorsys
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import os
import spacy
from collections import Counter

# Parse CSV data
events_df = pd.read_csv('Data/Dark_GD_Contest_Events')
edges_df = pd.read_csv('ed.csv')

# Convert dates to datetime objects for sorting and processing
events_df['Date'] = pd.to_datetime(events_df['Date'], format='mixed', dayfirst=True)

# Sort events by date
events_df = events_df.sort_values('Date')

# Reset the index after sorting
events_df = events_df.reset_index(drop=True)

# Convert to integers for edge processing
edges_df['Source'] = edges_df['Source'].astype(int)
edges_df['Target'] = edges_df['Target'].astype(int)

# Create a dictionary to store all unique edge types for each event
event_edge_types = {}

# Initialize counters for non-normal edge types
type_counters = {}

# Process edges to collect type information
for _, row in edges_df.iterrows():
    source_id = row['Source']
    target_id = row['Target']
    edge_type = row['Type']
    
    # If edge type is not "Normal", assign a number to it
    if edge_type != "Normal":
        if edge_type not in type_counters:
            type_counters[edge_type] = 0
        type_counters[edge_type] += 1
        numbered_edge_type = f"{edge_type} ({type_counters[edge_type]})"
    else:
        numbered_edge_type = edge_type
    
    # Store edge type for source event
    if source_id not in event_edge_types:
        event_edge_types[source_id] = set()
    event_edge_types[source_id].add(numbered_edge_type)
    
    # Store edge type for target event
    if target_id not in event_edge_types:
        event_edge_types[target_id] = set()
    event_edge_types[target_id].add(numbered_edge_type)

# Function to join unique edge types into a comma-separated string
def join_unique_edge_types(event_id):
    # Make sure we're comparing IDs of the same type
    try:
        # Try to convert event_id to int for comparison
        int_event_id = int(event_id)
        if int_event_id in event_edge_types and event_edge_types[int_event_id]:
            return ', '.join(sorted(event_edge_types[int_event_id]))
    except (ValueError, TypeError):
        # If conversion fails, try string comparison
        str_event_id = str(event_id)
        if str_event_id in event_edge_types and event_edge_types[str_event_id]:
            return ', '.join(sorted(event_edge_types[str_event_id]))
    return None

# Add a single Type column with all unique edge types
# First ensure ID is present in events_df
if 'ID' not in events_df.columns:
    print("Warning: 'ID' column not found in events dataframe. Looking for alternative ID columns.")
    # Try to find alternative ID columns
    id_candidates = [col for col in events_df.columns if 'id' in col.lower()]
    if id_candidates:
        print(f"Using '{id_candidates[0]}' as ID column.")
        events_df['ID'] = events_df[id_candidates[0]]
    else:
        print("No ID column found. Type information cannot be assigned.")
        events_df['Type'] = None

# Now apply the function to get edge types
if 'ID' in events_df.columns:
    events_df['Type'] = events_df['ID'].apply(join_unique_edge_types)
    # Count events with assigned types for verification
    type_count = events_df['Type'].notna().sum()
    print(f"Type information assigned to {type_count} events out of {len(events_df)} total events.")

# Define the main characters to track
main_characters = [
"Jonas Kahnwald / Adam", 
"Helge Doppler",
"Claudia Tiedemann",     
"Unknown", 
"Elisabeth Doppler", 
"Hannah Kahnwald / Hannah Nielsen",  
"Noah / Hanno Tauber", 
"H.G. Tannhaus", 
"Charlotte Doppler",
"Egon Tiedemann",  
"Martha Nielsen / Eve",
"Ulrich Nielsen", 
"Katharina Nielsen", 
"Mikkel Nielsen / Michael Kahnwald", 
"Bartosz Tiedemann", 
"Aleksander Tiedemann / Boris Niewald"
]

# Function to normalize character names by removing world indicators
def normalize_character_name(character):
    # Remove world indicators (J) or (M)
    if isinstance(character, str):
        return character.split('(')[0].strip()
    return character

# Function to check if a character is a main character and return the canonical name
def is_main_character(character):
    normalized_name = normalize_character_name(character)
    for main_char in main_characters:
        main_char_base = main_char.split('/')[0].strip()
        if normalized_name == main_char_base or normalized_name == main_char:
            return main_char
    return None

# Function to detect if a description mentions death
def contains_death_event(text):
    if not isinstance(text, str):
        return False
    
    death_terms = ["dies", "died", "killed", "kills", "murdered", "suicide", "death", 
                    "fatal", "passed away", "deceased", "dead"]
    
    for term in death_terms:
        if term in text.lower():
            return True
    return False

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

def get_main_characters_nlp(row):
    description = row.get('Description', '')
    full_description = row.get('Full_Description', '')
    characters_str = row.get('Characters', '')
    
    # Initialize result with four None values
    main_characters_result = [None, None, None, None]
    
    # Get characters from the Characters column
    manual_characters = []
    if isinstance(characters_str, str):
        char_list = [c.strip() for c in characters_str.split(',')]
        for char in char_list:
            main_char = is_main_character(char)
            if main_char and main_char not in manual_characters:
                manual_characters.append(main_char)
    
    # Extract persons from description using spaCy
    description_characters = []
    if isinstance(description, str) and description:
        doc = nlp(description)
        # Get named entities that are people
        named_people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        # Get proper nouns as backup
        proper_nouns = [token.text for token in doc if token.pos_ == "PROPN"]
        
        # Combine potential name sources
        potential_names = named_people + proper_nouns
        
        # Match these to main characters
        for name in potential_names:
            main_char = is_main_character(name)
            if main_char and main_char not in description_characters:
                description_characters.append(main_char)
    
    # Do the same for full description if needed
    full_desc_characters = []
    if len(description_characters) < 4 and isinstance(full_description, str):
        doc = nlp(full_description)
        potential_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        potential_names += [token.text for token in doc if token.pos_ == "PROPN"]
        
        for name in potential_names:
            main_char = is_main_character(name)
            if main_char and main_char not in description_characters and main_char not in full_desc_characters:
                full_desc_characters.append(main_char)
    
    # Check if death is mentioned and identify who died
    is_death_event = contains_death_event(description)
    deceased_character = None
    
    if is_death_event and isinstance(description, str):
        # Try to identify who died from the description
        for char in description_characters:
            char_base = char.split('/')[0].strip()
            if any(term + " " + char_base in description.lower() for term in ["dies", "died", "killed", "murdered"]):
                deceased_character = char
                break
            elif any(char_base + " " + term in description.lower() for term in ["dies", "died", "is killed", "was killed", "commits suicide"]):
                deceased_character = char
                break
    
    # Prioritize characters in this order:
    # 1. Character who died (if death event)
    # 2. Characters from description
    # 3. Characters from full description
    # 4. Characters from the Characters column
    
    ranked_characters = []
    
    # 1. Add deceased character if found
    if deceased_character:
        ranked_characters.append(deceased_character)
    
    # 2. Add remaining characters from description
    for char in description_characters:
        if char not in ranked_characters:
            ranked_characters.append(char)
    
    # 3. Add characters from full description
    for char in full_desc_characters:
        if char not in ranked_characters:
            ranked_characters.append(char)
    
    # 4. Add remaining characters from manual_characters
    for char in manual_characters:
        if char not in ranked_characters:
            ranked_characters.append(char)
    
    # Assign the top four characters to the result
    for i in range(min(4, len(ranked_characters))):
        main_characters_result[i] = ranked_characters[i]
    
    return main_characters_result[0], main_characters_result[1], main_characters_result[2], main_characters_result[3]

# Apply the new function to get all four main characters
characters_df = events_df.apply(get_main_characters_nlp, axis=1, result_type='expand')
characters_df.columns = ['FirstMainCharacter', 'SecondMainCharacter', 'ThirdMainCharacter', 'FourthMainCharacter']

# Add the character columns to the events dataframe
events_df['FirstMainCharacter'] = characters_df['FirstMainCharacter']
events_df['SecondMainCharacter'] = characters_df['SecondMainCharacter']
events_df['ThirdMainCharacter'] = characters_df['ThirdMainCharacter']
events_df['FourthMainCharacter'] = characters_df['FourthMainCharacter']

# Dictionary mapping characters to their initial format
character_initials = {
    # Nielsen family with distinct abbreviations for same initials
    "Martha Nielsen": "M.",
    "Martha": "M.",
    #"Magnus Nielsen": "Mag.N.",
    "Mikkel Nielsen": "Mi.N.",
    "Michael Kahnwald": "M.K.",
    "Ulrich Nielsen": "U.N.",
    "Katharina Nielsen": "K.N.",
    "Katharina": "K.N.",
    
    # Characters with variations by age
    "Noah": "N.",  
    "Hanno Tauber": "H.T.",  
    "Claudia Tiedemann": "C.Ti.",
    "Claudia": "C.T.",
    "Jonas Kahnwald": "J.",
    "Jonas": "J.",
    "J.K.": "J.",
    "Adam": "A.",  
    "Eve ": "E.",   
    "Elisabeth Doppler": "E.D.",
    "Hannah Kahnwald": "H.K.",
    "Hannah Nielsen": "H.N.",
    "Hannah": "H.N.",
    "Helge Doppler": "H.D.",
    "Helge": "H.D.",
    "Egon Tiedemann": "E.Ti.",
    "Egon": "E.Ti.",
    "Charlotte Doppler": "C.D.",
    "Charlotte": "C.D.",
    "H.G. Tannhaus": "H.G.T.",
    "Tannhaus": "T.",
    #"Silja Tiedemann": "S.T.",
    "Bartosz Tiedemann": "B.Ti.",
    "Bartosz": "B.Ti.",
    "Boris Niewald": "B.N.",
    "Unknown": "Un.",
    "Aleksander Tiedemann / Boris Niewald": "A.Ti.",
    "Aleksander Tiedemann": "A.Ti.",
    "Aleksander": "A.Ti."
}

# Create mapping of first names to their full initials
first_name_to_initials = {}
for full_name, initials in character_initials.items():
    first_name = full_name.split(' ')[0]
    if first_name not in first_name_to_initials:
        first_name_to_initials[first_name] = initials

# Function to replace character names in descriptions with their initials
def replace_with_character_initials(description):
    if not isinstance(description, str):
        return ""
    
    result = description
    
    # Define age variations and their abbreviations
    age_variations = ["Teen", "Adult", "Old", "teen", "adult", "old", "young", "Young"]
    age_abbreviations = {"Teen": "t.", "Adult": "a.", "Adults": "ads.", "Old": "o.", "teen": "t.", "Teens": "ts", "young": "y.", "old": "o.", "adult": "a.", "Young": "y."}
    
    # First, create a list of character names to check
    all_character_names = []
    
    # Add full names from character_initials dictionary
    for char_name in character_initials.keys():
        all_character_names.append(char_name)
    
    # Add only primary character names from main_characters list
    for character in main_characters:
        # Take only the first name (before any '/')
        primary_name = character.split('/')[0].strip()
        if primary_name not in all_character_names:
            all_character_names.append(primary_name)
    
    # Sort by length (descending) to avoid partial matches
    all_character_names = sorted(all_character_names, key=len, reverse=True)
    
    # First, replace full names with age variations
    for age in age_variations:
        for char_name in all_character_names:
            age_char = f"{age} {char_name}"
            if age_char in result:
                # Get the appropriate initials
                initials = None
                
                # Check if the character name exactly matches a key in character_initials
                if char_name in character_initials:
                    initials = character_initials[char_name]
                else:
                    # Look for partial matches
                    for full_name, init in character_initials.items():
                        if char_name in full_name or full_name in char_name:
                            initials = init
                            break
                
                if initials:
                    age_prefix = age_abbreviations[age]  # T., A., or O.
                    result = result.replace(age_char, f"{age_prefix}{initials}")
    
    # Replace standalone age variations
    for age, abbreviation in age_abbreviations.items():
        # Replace only whole words (with word boundaries)
        i = 0
        while i < len(result):
            # Check if there's a match at the current position
            if i + len(age) <= len(result) and result[i:i+len(age)] == age:
                # Check if it's a standalone word
                is_beginning = (i == 0)
                has_nonalpha_before = False if is_beginning else not result[i-1].isalpha()
                
                is_end = (i + len(age) == len(result))
                has_nonalpha_after = False if is_end else not result[i+len(age)].isalpha()
                
                if (is_beginning or has_nonalpha_before) and (is_end or has_nonalpha_after):
                    # Replace the age with its abbreviation
                    result = result[:i] + abbreviation + result[i+len(age):]
                    # Skip ahead to avoid processing the replacement
                    i += len(abbreviation)
                    continue
            
            i += 1
    
    # Next, replace full names without age variations
    for char_name in all_character_names:
        if char_name in result:
            # Get the appropriate initials
            initials = None
            
            # Check if the character name exactly matches a key in character_initials
            if char_name in character_initials:
                initials = character_initials[char_name]
            else:
                # Look for partial matches
                for full_name, init in character_initials.items():
                    if char_name in full_name or full_name in char_name:
                        initials = init
                        break
            
            if initials:
                result = result.replace(char_name, initials)
    
    # Finally, replace first names only
    for first_name, initials in first_name_to_initials.items():
        # Only replace first names that are standalone words (not part of other words)
        i = 0
        while i < len(result):
            # Check if there's a match at the current position
            if i + len(first_name) <= len(result) and result[i:i+len(first_name)] == first_name:
                # Check if it's a standalone word: either at the beginning or not preceded by a letter
                is_beginning = (i == 0)
                has_nonalpha_before = False if is_beginning else not result[i-1].isalpha()
                
                # Check if it's at the end or followed by a non-alphabetic character
                is_end = (i + len(first_name) == len(result))
                has_nonalpha_after = False if is_end else not result[i+len(first_name)].isalpha()
                
                if (is_beginning or has_nonalpha_before) and (is_end or has_nonalpha_after):
                    # Check if this position is part of an already replaced text
                    skip = False
                    for age in age_variations:
                        age_prefix = age[0] + "."
                        if i >= len(age_prefix) and result[i-len(age_prefix):i] == age_prefix:
                            skip = True
                            break
                    
                    if not skip:
                        # Replace the name with initials
                        result = result[:i] + initials + result[i+len(first_name):]
                        # Skip ahead to avoid processing the replacement
                        i += len(initials)
                        continue
            
            i += 1
    
    return result

# Create a new column with the formatted descriptions
events_df['FormattedDescription'] = events_df['Description'].apply(replace_with_character_initials)

# Filter out events with no main characters
events_df = events_df[events_df['FirstMainCharacter'].notna()]

# Reset the index after filtering
events_df.reset_index(drop=True, inplace=True)

# Remove ID and Ids merged columns
columns_to_drop = ['ID', 'IDs_merged']
events_df = events_df.drop(columns=[col for col in columns_to_drop if col in events_df.columns])

# Export the filtered events dataframe to CSV for reference
events_csv_path = "evPLUS.csv"
events_df.to_csv(events_csv_path, index=False)
print(f"Events data exported to {events_csv_path}")