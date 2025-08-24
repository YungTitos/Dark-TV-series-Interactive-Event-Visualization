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
import time

# Record start time for execution measurement
start_time = time.time()

# Load the data
events_df = pd.read_csv('Data/evPLUSPlusPlus.csv')
edges_df = pd.read_csv('Data/edges.csv')

main_characters = [
    "Jonas Kahnwald / Adam", 
    "Helge Doppler",
    "Claudia Tiedemann",
    "Ulrich Nielsen", 
    "Martha Nielsen / Eve",  
    "Elisabeth Doppler",
    "Unknown",  
    "Katharina Nielsen",
    "Charlotte Doppler",
    "Mikkel Nielsen / Michael Kahnwald", 
    "Noah / Hanno Tauber", 
    "Aleksander Tiedemann / Boris Niewald",
    "H.G. Tannhaus",
    "Egon Tiedemann",
    "Bartosz Tiedemann", 
    "Hannah Kahnwald / Hannah Nielsen"
    ]

# Convert dates to datetime objects for sorting and processing
events_df['Date'] = pd.to_datetime(events_df['Date'], format='mixed', dayfirst=True)

# Character color mapping for DARK
character_colors = {       
    "Jonas Kahnwald / Adam": "#92782d", # Yellow
    "Martha Nielsen / Eve": "#8c0048", # Purple
    "Claudia Tiedemann": "#7a0014", # Red  
    "Noah / Hanno Tauber": "#232930", # Brown 
    "Ulrich Nielsen": "#46606c", # Cyan   
    "Elisabeth Doppler": "#cb3608", # Orange
    "Hannah Kahnwald / Hannah Nielsen": "#640d00", # Dark Red 
    "Helge Doppler": "#2b5860", # Dark Teal  
    "Egon Tiedemann": "#615c46", # Olive Green 
    "Charlotte Doppler": "#422418", # Peru Brown 
    "H.G. Tannhaus": "#500c01", # Light Green              
    "Martha Nielsen": "#f032e6", # Magenta
    "Unknown": "#10313c", # Blue                                  
    "Mikkel Nielsen / Michael Kahnwald": "#802124", # Dark Pink 
    "Katharina Nielsen": "#53344d", # Pink   
    "Bartosz Tiedemann": "#7d5639", # Light Yellow               
    "Aleksander Tiedemann / Boris Niewald": "#0a5563" # Navy 
}

character_text_colors = {
    "Jonas Kahnwald / Adam": "black",
    "Martha Nielsen / Eve": "white", 
    "Claudia Tiedemann": "white",
    "Noah / Hanno Tauber": "white",
    "Ulrich Nielsen": "black",
    "Elisabeth Doppler": "black",
    "Hannah Kahnwald / Hannah Nielsen": "white",
    "Helge Doppler": "white",
    "Egon Tiedemann": "white",
    "Charlotte Doppler": "white",
    "H.G. Tannhaus": "black",
    "Martha Nielsen": "white",
    "Unknown": "white",
    "Mikkel Nielsen / Michael Kahnwald": "white",
    "Katharina Nielsen": "black",
    "Bartosz Tiedemann": "black",
    "Aleksander Tiedemann / Boris Niewald": "white"
}

# Function to wrap text for display in event squares
def wrap_event_text(text, width, max_lines=None):
    if not isinstance(text, str):
        return ""
    
    lines = []
    remaining_text = text
    
    while remaining_text and (max_lines is None or len(lines) < max_lines):
        # If remaining text fits in one line
        if len(remaining_text) <= width:
            lines.append(remaining_text)
            remaining_text = ""
        else:
            # Try to break at a space within the width
            space_pos = remaining_text[:width].rfind(' ')
            
            if space_pos != -1:
                # Break at space to preserve whole words
                lines.append(remaining_text[:space_pos])
                remaining_text = remaining_text[space_pos+1:]  # Skip the space
            else:
                # No space found, need to hyphenate a word
                lines.append(remaining_text[:width-2] + "-")
                remaining_text = remaining_text[width-2:]
    
    # If we still have text but hit max_lines, modify the last line with ellipsis
    if max_lines and len(lines) == max_lines and remaining_text:
        last_line = lines[-1]
        if len(last_line) > width - 3:
            lines[-1] = last_line[:width-4] + "..."
        else:
            lines[-1] += "..."

    # Use HTML line breaks with reduced line-height CSS for tighter spacing
    return "<br>".join(lines)

def extract_event_types_and_numbers(event_type_str):
    """
    Extract event types and their numbers from the Type column.
    Returns a list of tuples: [(event_type, number), ...]
    """
    import re
    
    if not isinstance(event_type_str, str):
        return []
    
    event_types = []
    
    # Split by comma to handle multiple event types
    parts = event_type_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        # Look for "Successful Time Travel" or "Succesfull Time Travel" (with typo)
        if "Successful Time Travel" in part or "Succesfull Time Travel" in part:
            # Extract number in parentheses
            match = re.search(r'\((\d+)\)', part)
            if match:
                number = int(match.group(1))
                event_types.append(("Successful Time Travel", number))
        
        # Look for "World Swap"
        elif "World Swap" in part:
            # Extract number in parentheses
            match = re.search(r'\((\d+)\)', part)
            if match:
                number = int(match.group(1))
                event_types.append(("World Swap", number))
    
    return event_types

def get_events_with_same_type_number(events_df, target_type, target_number):
    """
    Get all events that have the same event type and number.
    Returns a set of event indices.
    """
    matching_events = set()
    
    for idx, row in events_df.iterrows():
        event_types = extract_event_types_and_numbers(row['Type'])
        for event_type, number in event_types:
            if event_type == target_type and number == target_number:
                matching_events.add(idx)
                break
    
    return matching_events

def add_description_text(all_text_traces, x_position, char_position, description, is_important, rect_height, char, char_positions, event_rects, event_idx, expansion_info=None, is_death=False):
    """
    Add description text with possible rectangle expansion.
    expansion_info: dict with keys 'expand_above', 'expand_below', 'expanded_height'
    is_death: whether this is a death event (forces white text color)
    
    Creates text traces that are compatible with the button highlighting system.
    Each text trace gets a unique name and stores the event index for JavaScript access.
    """
    # Determine max_lines based on expansion_info
    if expansion_info is not None:
        if expansion_info.get('expand_above', False) and expansion_info.get('expand_below', False):
            max_lines = 13
        elif expansion_info.get('expand_above', False) or expansion_info.get('expand_below', False):
            max_lines = 8
        else:
            max_lines = 5
    else:
        max_lines = 4

    wrapped_desc = wrap_event_text(description, width=18, max_lines=max_lines)
    
    # Determine text color - white for all events except death events which are black
    if is_death:
        text_color = '#000000'  # Force black text for death events
    else:
        text_color = '#FFFFFF'  # White text for all other events

    # Use the center position directly
    adjusted_y_position = char_position

    # Create a unique and descriptive name for the text trace
    # Format: text_trace_{event_idx}_{char_name}_{x_position}
    trace_name = f'text_trace_{event_idx}_{char.replace(" ", "_").replace("/", "_")}_{x_position}'
    
    # Create the text trace with all necessary data for JavaScript interaction
    text_trace = go.Scatter(
        x=[x_position],
        y=[adjusted_y_position],
        mode='text',
        text=[wrapped_desc],
        textfont=dict(
            color=text_color,
            size=14
        ),
        hoverinfo='none',
        showlegend=False,
        name=trace_name,
        # Store comprehensive data for JavaScript:
        # [event_idx, character, x_position, original_color, is_death]
        customdata=[event_idx, char, x_position, text_color, is_death],
        # Add metadata as a custom property for easier access
        meta={
            'event_idx': event_idx,
            'character': char,
            'x_position': x_position,
            'original_color': text_color,
            'is_death': is_death,
            'trace_type': 'event_text'
        }
    )
    
    all_text_traces.append(text_trace)

# Function to normalize character names by removing world indicators
def normalize_character_name(character):
    # Remove world indicators (J) or (M)
    if isinstance(character, str):
        return character.split('(')[0].strip()
    return character

# Function to optimize description placement in merged events
def optimize_description_placement(event_group):
    """
    Organizes events to ensure no overlap in first main characters within a group.
    Events with the same first main character are moved to the next group.
    
    Returns: 
        - The first group of events with unique first main characters
        - The remaining events that should be added to the next group
    """
    # If only 0 or 1 events, no need to optimize
    if len(event_group) <= 1:
        return event_group, []
    
    # Extract date of the event group
    current_date = event_group[0][1]['Date'].strftime('%Y-%m-%d')
    
    # Create a dictionary to group events by first main character
    events_by_char = {}
    
    # Group events by their first main character
    for event_tuple in event_group:
        idx, event = event_tuple
        first_char = event.get('FirstMainCharacter', None)
        
        if first_char not in events_by_char:
            events_by_char[first_char] = []
        
        events_by_char[first_char].append(event_tuple)
    
    # Select only the first event for each character
    first_group = []
    remaining_events = []
    
    # Add one event per unique first main character to the first group
    for char, char_events in events_by_char.items():
        if char_events:  # If there are any events for this character
            first_group.append(char_events[0])
            # Add any additional events for this character to the remaining list
            remaining_events.extend(char_events[1:])
    
    # Return the first group with unique characters and the remaining events
    return first_group, remaining_events

def add_interactive_buttons(all_hover_traces, x_position, char_position, event, event_idx, rect_width, rect_height, events_df):
    """
    Add circular buttons for Successful Time Travel and World Swap events.
    Buttons are positioned on the right side of the rectangle border.
    Only adds buttons if there are matching events with the same type and number.
    """
    # Extract event types and numbers from the event
    event_types = extract_event_types_and_numbers(event.get('Type', ''))
    
    if not event_types:
        return  # No buttons to add
    
    # Helper function to find destination date for time travel
    def get_destination_date(current_event_idx, event_type, number):
        matching_events = get_events_with_same_type_number(events_df, event_type, number)
        matching_events.discard(current_event_idx)  # Remove current event
        
        if matching_events:
            # Get the first matching event (destination)
            dest_event_idx = next(iter(matching_events))
            dest_event = events_df.iloc[dest_event_idx]
            return dest_event['Date'].strftime('%d/%m/%Y')
        return None
    
    # Filter event types to only include those with matching events
    valid_event_types = []
    for event_type, number in event_types:
        matching_events = get_events_with_same_type_number(events_df, event_type, number)
        if len(matching_events) > 1:  # Only add button if there are multiple matching events
            valid_event_types.append((event_type, number))
    
    if not valid_event_types:
        return  # No valid buttons to add
    
    button_radius = 0.18  # Increased button radius for bigger buttons
    button_spacing = 1  # Increased spacing between buttons when there are multiple
    
    # Calculate base button position (right side of rectangle, tight on border)
    button_x = x_position + rect_width  # Position exactly on the right border
    
    # If there are multiple buttons, position them vertically centered around the rectangle center
    if len(valid_event_types) == 1:
        button_y_positions = [char_position]
    else:  # 2 buttons
        offset = button_spacing / 2
        button_y_positions = [char_position - offset, char_position + offset]
    
    for idx, (event_type, number) in enumerate(valid_event_types):
        if idx >= len(button_y_positions):
            break  # Safety check
            
        button_y = button_y_positions[idx]
        
        # Determine button color and emoji based on event type
        if event_type == "Successful Time Travel":
            button_color = "#4CAF50"  # Green
            button_emoji = "⏰"  # Clock emoji - better represents time travel
        elif event_type == "World Swap":
            button_color = "#2196F3"  # Blue
            button_emoji = "🌍"  # World emoji
        else:
            continue  # Skip unknown event types
        
        # Get destination date for hover text
        destination_date = get_destination_date(event_idx, event_type, number)
        if destination_date:
            hover_text = f'{event_type}<br>Destination: {destination_date}<br>Click to highlight related events'
        else:
            hover_text = f'{event_type}<br>Click to highlight related events'
        
        # Create unique button ID for JavaScript interaction
        button_id = f"btn_{event_type.replace(' ', '_')}_{number}_{event_idx}_{idx}"
        
        # Add circular button as a scatter trace with custom hover and click functionality
        button_trace = go.Scatter(
            x=[button_x],
            y=[button_y],
            mode='markers+text',
            marker=dict(
                size=button_radius * 100,  # Convert to marker size
                color=button_color,
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            text=[button_emoji],
            textfont=dict(color='white', size=16),  # Larger size for emoji
            hoverinfo='text',
            hovertext=hover_text,
            showlegend=False,
            # Store button metadata for JavaScript
            customdata=[event_type, number, event_idx, x_position, char_position],
            name=button_id
        )
        
        all_hover_traces.append(button_trace)

def create_dark_timeline_grid(character_spacing=1.0, event_spacing=1.0, rect_width=0.8, rect_height=0.4, 
                             show_non_participants=True, asymmetric_expansion=False):
    """
    Create a timeline grid visualization with configurable spacing.
    
    Parameters:
    - character_spacing: Vertical spacing between characters (default=1.0)
    - event_spacing: Horizontal spacing between events (default=1.0)
    - rect_width: Width of event rectangles (default=0.8)
    - rect_height: Height of event rectangles (default=0.4)
    - show_non_participants: Whether to show rectangles for non-participating characters (default=True)
    - asymmetric_expansion: When True, adjacent rectangles with text expand asymmetrically (one above only, one below only) (default=False)
    """
    # Create figure with custom size
    fig = go.Figure()
    
    # Set up character positions with configurable spacing
    char_positions = {char: i * character_spacing for i, char in enumerate(main_characters)}
    
    # Corner radius for rectangles
    corner_radius = 0.15  # Slightly reduced to match new proportions
    
    # Collect all shapes for batch processing
    all_shapes = []
    expanded_shapes = []  # For shapes that should be on top
    all_text_traces = []
    all_hover_traces = []
    
    # Pre-populate date_colors with alternating colors for each unique date
    # This ensures the dictionary is filled before processing events
    date_strings = [d.strftime('%d-%m-%Y') for d in events_df['Date']]
    unique_dates = []
    date_colors = {}
    # Start with initial pattern
    use_alternate_pattern = False
    
    for date_str in date_strings:
        if date_str not in unique_dates:
            unique_dates.append(date_str)
            
            # Determine default color based on current pattern
            if not use_alternate_pattern:
                default_color = "#151B23" if len(unique_dates) % 2 == 1 else "#152323"
            else:
                default_color = "#152323" if len(unique_dates) % 2 == 1 else "#151B23"
            
            # Override colors for specific dates and switch pattern
            if date_str == "21-06-1921":
                date_colors[date_str] = "#151B23"
                use_alternate_pattern = True  # Switch pattern after this date
            elif date_str == "01-01-2021":
                date_colors[date_str] = "#152323"
                use_alternate_pattern = False  # Switch pattern after this date
            else:
                date_colors[date_str] = default_color
    
    # Group consecutive events with the same date
    merged_events = []
    current_group = []
    current_date = None
    
    # Pre-process events to identify groups with the same date
    for i, (_, event) in enumerate(events_df.iterrows()):
        event_date = event['Date'].strftime('%Y-%m-%d')
        
        if current_date == event_date and len(current_group) < 5:
            current_group.append((i, event))
        else:
            if current_group:
                merged_events.append(current_group)
            current_group = [(i, event)]
            current_date = event_date
    
    # Add the last group
    if current_group:
        merged_events.append(current_group)
    
    # Description placement optimization
    
    # Keep track of event rectangles for overlap checking
    event_rects = {}  # {(char, x_position): (y0, y1)}
    
    # Helper function to add non-participant rectangles
    def add_non_participant_rectangles(non_participants, x_position, date_str):
        """Add background rectangles for characters not involved in an event."""
        # Get the date-based background color
        date_bg_color = date_colors.get(date_str, "#151B23")
        
        for char in non_participants:
            if char in char_positions:
                # Use the date-based color directly
                color = date_bg_color
                
                # Define coordinates for the rectangle
                x0 = x_position - rect_width
                y0 = char_positions[char] - rect_height/2
                x1 = x_position + rect_width
                y1 = char_positions[char] + rect_height/2
                
                # Create SVG path for rounded rectangle
                path = (f'M {x0+corner_radius} {y0} L {x1-corner_radius} {y0} ' 
                        f'Q {x1} {y0} {x1} {y0+corner_radius} L {x1} {y1-corner_radius} ' 
                        f'Q {x1} {y1} {x1-corner_radius} {y1} L {x0+corner_radius} {y1} ' 
                        f'Q {x0} {y1} {x0} {y1-corner_radius} L {x0} {y0+corner_radius} ' 
                        f'Q {x0} {y0} {x0+corner_radius} {y0} Z')
                
                # Add the shape
                all_shapes.append(
                    dict(
                        type="path",
                        path=path,
                        fillcolor=color,
                        opacity=1.0,
                        line_width=0,
                        xref="x",
                        yref="y",
                        layer="below"  # Keep non-participants on the "below" layer
                    )
                )

    # Process each merged event group
    output_position = 0
    overflow_events = []  # Store events that need to be moved to the next date

    # Create a new list to hold all processed event groups
    processed_merged_events = []

    # First pass: optimize description placement and collect overflow events
    for event_group in merged_events:
        # Add any overflow events from the previous group
        if overflow_events:
            event_group = overflow_events + event_group
            overflow_events = []
        
        # Check if we need to limit the group size due to overlapping descriptions
        event_group, remaining = optimize_description_placement(event_group)
        processed_merged_events.append(event_group)
        
        # Store remaining events for the next date group
        overflow_events = remaining

    # Add any final overflow events as a new group
    if overflow_events:
        processed_merged_events.append(overflow_events)

    # Replace the original merged_events with the processed version
    merged_events = processed_merged_events

    # Now process the event groups as normal
    for event_group in merged_events:
        # Check if we need to limit the group size due to overlapping descriptions
        event_group, limited = optimize_description_placement(event_group)

        # If it's a single event, process normally
        if len(event_group) == 1:
            i, event = event_group[0]
            
            # Use output_position for x-coordinate
            x_position = output_position * event_spacing
            
            event_date = event['Date'].strftime('%Y-%m-%d')
            event_desc = event['FormattedDescription']  # Raw description for hover info
            
            # Check if description hits max_lines - only calculate this once
            desc = event['FormattedDescription']
            test_wrap = wrap_event_text(desc, width=16, max_lines=3)
            hit_max_lines = test_wrap.count("<br>") >= 2 and "..." in test_wrap
            
            # Find all involved main characters - improved matching
            event_chars = []
            if isinstance(event['Characters'], str):
                for char in [c.strip() for c in event['Characters'].split(',')]:
                    normalized = normalize_character_name(char)
                    for main_char in main_characters:
                        main_normalized = normalize_character_name(main_char)
                        if normalized in main_normalized or main_normalized in normalized:
                            event_chars.append(main_char)
                            break
            
            # Make sure FirstMainCharacter is included if present
            if event['FirstMainCharacter'] and event['FirstMainCharacter'] not in event_chars:
                event_chars.append(event['FirstMainCharacter'])

            event_chars = list(set(event_chars))  # Remove duplicates
            
            # Determine if we need expansion/contraction for single events
            expansions_single = {}
            contractions_single = {}
            
            if hit_max_lines:
                main_char = event['FirstMainCharacter']
                if main_char in event_chars:
                    # Find character positions relative to main_char
                    char_positions_list = [(char, pos) for char, pos in char_positions.items()]
                    char_positions_list.sort(key=lambda x: x[1])
                    char_to_idx = {char: idx for idx, (char, _) in enumerate(char_positions_list)}
                    
                    main_char_idx = char_to_idx.get(main_char, -1)
                    if main_char_idx >= 0:
                        # Check adjacent characters for activity
                        above_is_active = False
                        below_is_active = False
                        char_above = None
                        char_below = None
                        
                        if main_char_idx > 0:
                            char_above = char_positions_list[main_char_idx-1][0]
                            above_is_active = char_above in event_chars
                        
                        if main_char_idx < len(char_positions_list) - 1:
                            char_below = char_positions_list[main_char_idx+1][0]
                            below_is_active = char_below in event_chars
                        
                        # Check if adjacent characters have text (are FirstMainCharacter of any event)
                        char_above_has_text = False
                        char_below_has_text = False
                        if asymmetric_expansion:
                            # For now, assume adjacent characters don't have text in single events
                            # This logic primarily applies to merged events where multiple events have text
                            char_above_has_text = False
                            char_below_has_text = False
                        
                        # Apply expansion and contraction logic
                        if not above_is_active and not below_is_active:
                            # Expand both directions
                            expansions_single[main_char] = {
                                'expand_above': True,
                                'expand_below': True,
                                'expanded_height': rect_height * 2
                            }
                        elif not above_is_active and below_is_active:
                            # Check for asymmetric expansion condition
                            if asymmetric_expansion and char_below_has_text:
                                # Current rectangle has text and below rectangle has text, expand above only
                                expansions_single[main_char] = {
                                    'expand_above': True,
                                    'expand_below': False,
                                    'expand_below_extra': False,
                                    'expanded_height': rect_height * 1.5
                                }
                                # Don't contract the below character since it also has text
                            else:
                                # Expand above, contract below - extend slightly into contracted space
                                expansions_single[main_char] = {
                                    'expand_above': True,
                                    'expand_below': False,
                                    'expand_below_extra': True,  # Flag to extend into contracted space
                                    'expanded_height': rect_height * 1.5
                                }
                                if char_below and not char_below_has_text:
                                    contractions_single[char_below] = {
                                        'contract_above': True,
                                        'contract_below': False,
                                        'contracted_height': rect_height * 0.4  # Made smaller
                                    }
                        elif above_is_active and not below_is_active:
                            # Check for asymmetric expansion condition
                            if asymmetric_expansion and char_above_has_text:
                                # Current rectangle has text and above rectangle has text, expand below only
                                expansions_single[main_char] = {
                                    'expand_above': False,
                                    'expand_below': True,
                                    'expand_above_extra': False,
                                    'expanded_height': rect_height * 1.5
                                }
                                # Don't contract the above character since it also has text
                            else:
                                # Expand below, contract above - extend slightly into contracted space
                                expansions_single[main_char] = {
                                    'expand_above': False,
                                    'expand_below': True,
                                    'expand_above_extra': True,  # Flag to extend into contracted space
                                    'expanded_height': rect_height * 1.5
                                }
                                if char_above and not char_above_has_text:
                                    contractions_single[char_above] = {
                                        'contract_above': False,
                                        'contract_below': True,
                                        'contracted_height': rect_height * 0.4  # Made smaller
                                    }
                        else:
                            # Both neighbors active, expand moderately and contract neighbors more
                            expansions_single[main_char] = {
                                'expand_above': True,
                                'expand_below': True,
                                'expand_above_extra': True,  # Extend into contracted space above
                                'expand_below_extra': True,  # Extend into contracted space below
                                'expanded_height': rect_height * 0.9  # Contract to 90%
                            }
                            if char_above:
                                contractions_single[char_above] = {
                                    'contract_above': False,
                                    'contract_below': True,
                                    'contracted_height': rect_height * 0.3  # Made much smaller
                                }
                            if char_below:
                                contractions_single[char_below] = {
                                    'contract_above': True,
                                    'contract_below': False,
                                    'contracted_height': rect_height * 0.3  # Made much smaller
                                }
            
            # For each character involved in this event
            for char in event_chars:
                if char in char_positions:
                    # Check if the event is a death event (handle both string and boolean values)
                    death_value = event.get('Death', False)
                    is_death = death_value == True or death_value == 'True'
                    
                    # Check if the event is important
                    is_important = event.get('Important Trigger', False)
                    
                    if is_death:
                        color = "#868686"  # Gray color for death events
                    else:
                        base_color = character_colors.get(char, "#FFFFFF")  # Normal Color
                        if is_important:
                            # Make the color dimmer for important events
                            # Convert hex to RGB, reduce brightness, convert back to hex
                            hex_color = base_color.lstrip('#')
                            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                            # Reduce brightness by 30%
                            dimmed_rgb = tuple(int(c * 0.7) for c in rgb)
                            color = '#%02x%02x%02x' % dimmed_rgb
                        else:
                            color = base_color  

                    # Define coordinates for the rectangle using incremental positioning
                    x0 = x_position - rect_width
                    y0 = char_positions[char] - rect_height/2
                    x1 = x_position + rect_width
                    y1 = char_positions[char] + rect_height/2

                    # Apply expansion/contraction logic
                    expansion_info = None
                    if char in expansions_single:
                        expansion = expansions_single[char]
                        expansion_info = expansion
                        if expansion['expand_above'] and expansion['expand_below']:
                            # Check if we need to extend into contracted spaces
                            if expansion.get('expand_above_extra', False) and expansion.get('expand_below_extra', False):
                                # Both neighbors active - make rectangle smaller instead of extending
                                y0 = char_positions[char] - rect_height * 0.85  # Smaller rectangle
                                y1 = char_positions[char] + rect_height * 0.85  # Smaller rectangle
                            else:
                                y0 = char_positions[char] - rect_height
                                y1 = char_positions[char] + rect_height
                        elif expansion['expand_above']:
                            y0 = char_positions[char] - rect_height
                            # Check if we should extend into contracted space below
                            if expansion.get('expand_below_extra', False):
                                y1 = char_positions[char] + rect_height/2 + rect_height/3  # Made longer
                            else:
                                y1 = char_positions[char] + rect_height/2
                        elif expansion['expand_below']:
                            # Check if we should extend into contracted space above
                            if expansion.get('expand_above_extra', False):
                                y0 = char_positions[char] - rect_height/2 - rect_height/3  # Made longer
                            else:
                                y0 = char_positions[char] - rect_height/2
                            y1 = char_positions[char] + rect_height
                    elif char in contractions_single:
                        contraction = contractions_single[char]
                        expansion_info = contraction  # Pass contraction info as expansion_info for text positioning
                        if contraction['contract_above'] and contraction['contract_below']:
                            y0 = char_positions[char] - rect_height/8  # Made much smaller
                            y1 = char_positions[char] + rect_height/8  # Made much smaller
                        elif contraction['contract_above']:
                            y0 = char_positions[char] - rect_height/8  # Made much shorter
                            y1 = char_positions[char] + rect_height/2
                        elif contraction['contract_below']:
                            y0 = char_positions[char] - rect_height/2
                            y1 = char_positions[char] + rect_height/8  # Made much shorter
                    
                    # Create SVG path for rounded rectangle
                    path = (f'M {x0+corner_radius} {y0} L {x1-corner_radius} {y0} ' 
                        f'Q {x1} {y0} {x1} {y0+corner_radius} L {x1} {y1-corner_radius} ' 
                        f'Q {x1} {y1} {x1-corner_radius} {y1} L {x0+corner_radius} {y1} ' 
                        f'Q {x0} {y1} {x0} {y1-corner_radius} L {x0} {y0+corner_radius} ' 
                        f'Q {x0} {y0} {x0+corner_radius} {y0} Z')
                    
                    # Add the shape without any border
                    shape_to_add = dict(
                        type="path",
                        path=path,
                        fillcolor=color,
                        opacity=1.0,
                        line=dict(width=0),                            xref="x",
                        yref="y",
                        layer="between"
                    )

                    if char in expansions_single:
                        expanded_shapes.append(shape_to_add)
                    elif char in contractions_single:
                        all_shapes.append(shape_to_add)
                    else:
                        all_shapes.append(shape_to_add)

                    # Register this rectangle for overlap checking
                    event_rects[(char, x_position)] = (y0, y1)

                    # Only add description text for the FirstMainCharacter
                    if char == event['FirstMainCharacter']:
                        # Calculate the actual center of the rectangle for text positioning
                        rect_center_y = (y0 + y1) / 2
                        add_description_text(
                            all_text_traces, 
                            x_position, 
                            rect_center_y,  # Use actual rectangle center instead of char_position
                            event_desc, 
                            event.get('Important Trigger', False),
                            rect_height,  # Always pass standard height
                            char,
                            char_positions,
                            event_rects,
                            i,
                            expansion_info if (hit_max_lines and char in expansions_single) else None,
                            is_death  # Pass death information
                        )

                    # Collect hover information trace data for THIS specific character's rectangle
                    # Wrap the description and characters for better vertical display
                    wrapped_description = wrap_event_text(event.get('Full_Description', event_desc), width=50)
                    wrapped_characters = wrap_event_text(event.get('Characters', 'N/A'), width=40)
                    
                    # Get character color for hover background
                    char_color = character_colors.get(char, "#FFFFFF")
                    
                    # For death events, override with grey background and white text
                    if is_death:
                        char_color = "#868686"  # Grey background for death events (same as rectangle color)
                        text_color = "white"
                        # Add skull emoji after the main character name for death events
                        skull_emoji = "                                              💀"
                        hovertemplate = f'<b style="color:{text_color}; text-align: center;">%{{customdata[0]}}{skull_emoji}</b><br><span style="color:{text_color}; text-align: center;">%{{customdata[1]}}</span><br><br><span style="color:{text_color}; text-align: center;">%{{customdata[2]}}</span><br><br><i style="color:{text_color}; text-align: center;">Characters:<br>%{{customdata[3]}}</i><extra></extra>'
                    else:
                        # Calculate text color based on background brightness for normal events
                        text_color = 'black' if np.mean([int(char_color[i:i+2], 16) for i in (1, 3, 5)]) > 128 else 'white'
                        # Add star emoji after the main character name for normal events
                        star_emoji = "                                              ⭐"
                        hovertemplate = f'<b style="color:{text_color}">%{{customdata[0]}}{star_emoji}</b><br><span style="color:{text_color}">%{{customdata[1]}}</span><br><br><span style="color:{text_color}">%{{customdata[2]}}</span><br><br><i style="color:{text_color}">Characters:<br>%{{customdata[3]}}</i><extra></extra>'
                    
                    all_hover_traces.append(
                        go.Scatter(
                            x=[x_position],
                            y=[char_positions[char]],
                            mode='markers',
                            marker=dict(
                                opacity=0,
                                size=10,
                            ),
                            hoverinfo='all',
                            customdata=[[event.get('FirstMainCharacter', 'N/A'), event_date, wrapped_description, wrapped_characters]],
                            hovertemplate=hovertemplate,
                            hoverlabel=dict(bgcolor=char_color, bordercolor="white", font=dict(color=text_color)),
                            showlegend=False
                        )
                    )
            
            # Add interactive buttons for this single event (positioned at the center of the rectangle)
            add_interactive_buttons(all_hover_traces, x_position, char_positions[event['FirstMainCharacter']], event, i, rect_width, rect_height, events_df)
            
            # Add rectangles for characters NOT involved in this event
            if show_non_participants:
                non_participants = [char for char in main_characters if char not in event_chars and char in char_positions]
                event_date_str = event['Date'].strftime('%d-%m-%Y')
                add_non_participant_rectangles(non_participants, x_position, event_date_str)
                
        else:
            # This is a merged group of 2-3 events with the same date
            x_position = output_position * event_spacing
            
            # Get all characters involved in any of the events in the group
            all_chars_involved = set()
            event_date = None
            
            # Indicator colors for events in the group
            indicator_colors = ["#FF0000", "#0000FF", "#00FF00", "#800080", "#FFFFFF", "#FFA500"]  # red, blue, green, purple, white, orange
            # Create a dictionary to track which events each character participates in
            char_event_participation = {}
            
            # Dictionary to store description assignments - each first main character gets its event's description
            assigned_descriptions = {}

            # First, determine character participation for each event in the group
            for idx, (_, event) in enumerate(event_group):
                if idx < len(indicator_colors):  # Only support up to 6 events
                    event_chars = []
                    # Extract characters from the 'Characters' field
                    if isinstance(event['Characters'], str):
                        for char in [c.strip() for c in event['Characters'].split(',')]:
                            normalized = normalize_character_name(char)
                            for main_char in main_characters:
                                main_normalized = normalize_character_name(main_char)
                                if normalized in main_normalized or main_normalized in normalized:
                                    event_chars.append(main_char)
                                    break
                    
                    # Add main characters explicitly mentioned
                    for field in ['FirstMainCharacter', 'SecondMainCharacter', 'ThirdMainCharacter', 'FourthMainCharacter']:
                        if field in event and event[field]:
                            if event[field] not in event_chars:
                                event_chars.append(event[field])
                    
                    # Record participation for each character
                    for char in event_chars:
                        if char not in char_event_participation:
                            char_event_participation[char] = []
                        char_event_participation[char].append(idx)

            # Process each event in the group to collect all characters involved and assign descriptions
            for idx, (original_event_idx, event) in enumerate(event_group):
                event_date = event['Date'].strftime('%Y-%m-%d')
                
                # Collect characters
                event_chars = []
                if isinstance(event['Characters'], str):
                    for char in [c.strip() for c in event['Characters'].split(',')]:
                        normalized = normalize_character_name(char)
                        for main_char in main_characters:
                            main_normalized = normalize_character_name(main_char)
                            if normalized in main_normalized or main_normalized in normalized:
                                event_chars.append(main_char)
                                break
                
                # Make sure FirstMainCharacter is included if present
                if event['FirstMainCharacter'] and event['FirstMainCharacter'] not in event_chars:
                    event_chars.append(event['FirstMainCharacter'])
                
                # Remove duplicates and add to the set of all involved characters
                event_chars = list(set(event_chars))
                all_chars_involved.update(event_chars)
                
                # Assign description to the event's first main character
                if event['FormattedDescription'] and event['FirstMainCharacter']:
                    # If this character already has a description, don't overwrite it
                    if event['FirstMainCharacter'] not in assigned_descriptions:
                        death_value = event.get('Death', False)
                        is_death = death_value == True or death_value == 'True'
                        assigned_descriptions[event['FirstMainCharacter']] = {
                            "desc": event['FormattedDescription'],
                            "event_idx": original_event_idx,  # Use the original event index from dataframe
                            "important": event.get('Important Trigger', False),
                            "death": is_death
                        }
            
            # Check which descriptions need expansion
            desc_expansion_needed = {}
            for char, desc_info in assigned_descriptions.items():
                test_wrap = wrap_event_text(desc_info['desc'], width=16, max_lines=3)
                hit_max_lines = test_wrap.count("<br>") >= 2 and "..." in test_wrap
                desc_expansion_needed[char] = hit_max_lines
            
            # Find character vertical neighbors (who is above and below each character)
            char_positions_list = [(char, pos) for char, pos in char_positions.items()]
            char_positions_list.sort(key=lambda x: x[1])  # Sort by vertical position
            
            # Create a mapping of character to their position in the sorted list
            char_to_idx = {char: idx for idx, (char, _) in enumerate(char_positions_list)}
            
            # Determine expansion possibilities and contractions for adjacent characters
            expansions = {}
            contractions = {}
            
            for char in assigned_descriptions:
                if desc_expansion_needed.get(char, False):
                    char_idx = char_to_idx.get(char, -1)
                    if char_idx >= 0:
                        # Check if characters above and below are active (in all_chars_involved)
                        above_is_active = False
                        below_is_active = False
                        char_above = None
                        char_below = None
                        
                        # Check character above
                        if char_idx > 0:
                            char_above = char_positions_list[char_idx-1][0]
                            above_is_active = char_above in all_chars_involved
                        
                        # Check character below
                        if char_idx < len(char_positions_list) - 1:
                            char_below = char_positions_list[char_idx+1][0]
                            below_is_active = char_below in all_chars_involved
                        
                        # Check if adjacent characters have text (are in assigned_descriptions)
                        char_above_has_text = char_above in assigned_descriptions if char_above else False
                        char_below_has_text = char_below in assigned_descriptions if char_below else False
                        
                        # Apply expansion rules and set up contractions for adjacent active characters
                        if not above_is_active and not below_is_active:
                            # Expand both directions (no active neighbors to contract)
                            expansions[char] = {
                                'expand_above': True,
                                'expand_below': True,
                                'expanded_height': rect_height * 2
                            }
                        elif not above_is_active and below_is_active:
                            # Check for asymmetric expansion condition
                            if asymmetric_expansion and char_below_has_text:
                                # Current rectangle has text and below rectangle has text, expand above only
                                expansions[char] = {
                                    'expand_above': True,
                                    'expand_below': False,
                                    'expand_below_extra': False,
                                    'expanded_height': rect_height * 1.5
                                }
                                # Don't contract the below character since it also has text
                            else:
                                # Expand only above, contract character below - extend slightly into contracted space
                                expansions[char] = {
                                    'expand_above': True,
                                    'expand_below': False,
                                    'expand_below_extra': True,  # Flag to extend into contracted space
                                    'expanded_height': rect_height * 1.5
                                }
                                if char_below and not char_below_has_text:
                                    contractions[char_below] = {
                                        'contract_above': True,
                                        'contract_below': False,
                                        'contracted_height': rect_height * 0.4  # Made smaller
                                    }
                        elif above_is_active and not below_is_active:
                            # Check for asymmetric expansion condition
                            if asymmetric_expansion and char_above_has_text:
                                # Current rectangle has text and above rectangle has text, expand below only
                                expansions[char] = {
                                    'expand_above': False,
                                    'expand_below': True,
                                    'expand_above_extra': False,
                                    'expanded_height': rect_height * 1.5
                                }
                                # Don't contract the above character since it also has text
                            else:
                                # Expand only below, contract character above - extend slightly into contracted space
                                expansions[char] = {
                                    'expand_above': False,
                                    'expand_below': True,
                                    'expand_above_extra': True,  # Flag to extend into contracted space
                                    'expanded_height': rect_height * 1.5
                                }
                                if char_above and not char_above_has_text:
                                    contractions[char_above] = {
                                        'contract_above': False,
                                        'contract_below': True,
                                        'contracted_height': rect_height * 0.4  # Made smaller
                                    }
                        else:
                            # Both neighbors active
                            if asymmetric_expansion and (char_above_has_text or char_below_has_text):
                                # Special case: if both neighbors have text, apply asymmetric expansion
                                if char_above_has_text and char_below_has_text:
                                    # Both neighbors have text - use character position to determine direction
                                    # Upper character expands above only, lower character expands below only
                                    if char_idx % 2 == 0:  # Even index: expand above only
                                        expansions[char] = {
                                            'expand_above': True,
                                            'expand_below': False,
                                            'expand_above_extra': False,
                                            'expanded_height': rect_height * 1.5
                                        }
                                    else:  # Odd index: expand below only
                                        expansions[char] = {
                                            'expand_above': False,
                                            'expand_below': True,
                                            'expand_below_extra': False,
                                            'expanded_height': rect_height * 1.5
                                        }
                                elif char_above_has_text:
                                    # Only above neighbor has text, expand below only
                                    expansions[char] = {
                                        'expand_above': False,
                                        'expand_below': True,
                                        'expand_below_extra': False,
                                        'expanded_height': rect_height * 1.5
                                    }
                                    # Contract the below neighbor since it doesn't have text
                                    if char_below:
                                        contractions[char_below] = {
                                            'contract_above': True,
                                            'contract_below': False,
                                            'contracted_height': rect_height * 0.3
                                        }
                                elif char_below_has_text:
                                    # Only below neighbor has text, expand above only
                                    expansions[char] = {
                                        'expand_above': True,
                                        'expand_below': False,
                                        'expand_above_extra': False,
                                        'expanded_height': rect_height * 1.5
                                    }
                                    # Contract the above neighbor since it doesn't have text
                                    if char_above:
                                        contractions[char_above] = {
                                            'contract_above': False,
                                            'contract_below': True,
                                            'contracted_height': rect_height * 0.3
                                        }
                            else:
                                # Both neighbors active, expand moderately and contract both neighbors more
                                expansions[char] = {
                                    'expand_above': True,
                                    'expand_below': True,
                                    'expand_above_extra': True,  # Extend into contracted space above
                                    'expand_below_extra': True,  # Extend into contracted space below
                                    'expanded_height': rect_height * 0.9  # Contract to 90%
                                }
                                if char_above and not char_above_has_text:
                                    contractions[char_above] = {
                                        'contract_above': False,
                                        'contract_below': True,
                                        'contracted_height': rect_height * 0.3  # Made much smaller
                                    }
                                if char_below and not char_below_has_text:
                                    contractions[char_below] = {
                                        'contract_above': True,
                                        'contract_below': False,
                                        'contracted_height': rect_height * 0.3  # Made much smaller
                                    }
            
            # Loop through all characters to create shapes
            for char in main_characters:
                if char in char_positions:
                    # If character is involved in any event of the group
                    if char in all_chars_involved:
                        # Check if any event in the group is a death event involving this character
                        is_death_event = False
                        is_important_event = False
                        for _, event in event_group:
                            death_value = event.get('Death', False)
                            is_death = death_value == True or death_value == 'True'
                            if is_death and char == event['FirstMainCharacter']:
                                is_death_event = True
                                break
                            # Check if this character is involved in an important event
                            if char == event['FirstMainCharacter'] and event.get('Important Trigger', False):
                                is_important_event = True
                        
                        if is_death_event:
                            color = "#868686"  # Gray color for death events
                        else:
                            base_color = character_colors.get(char, "#FFFFFF")  # Normal Color
                            if is_important_event:
                                # Make the color dimmer for important events
                                # Convert hex to RGB, reduce brightness, convert back to hex
                                hex_color = base_color.lstrip('#')
                                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                                # Reduce brightness by 30%
                                dimmed_rgb = tuple(int(c * 0.7) for c in rgb)
                                color = '#%02x%02x%02x' % dimmed_rgb
                            else:
                                color = base_color
                        
                        # Define coordinates for the rectangle
                        x0 = x_position - rect_width
                        y0 = char_positions[char] - rect_height/2
                        x1 = x_position + rect_width
                        y1 = char_positions[char] + rect_height/2
                        
                        # Apply expansion if this character has a description needing expansion
                        if char in expansions:
                            expansion = expansions[char]
                            if expansion['expand_above'] and expansion['expand_below']:
                                # Check if we need to extend into contracted spaces
                                if expansion.get('expand_above_extra', False) and expansion.get('expand_below_extra', False):
                                    # Both neighbors active - make rectangle smaller instead of extending
                                    y0 = char_positions[char] - rect_height * 0.85  # Smaller rectangle
                                    y1 = char_positions[char] + rect_height * 0.85  # Smaller rectangle
                                else:
                                    y0 = char_positions[char] - rect_height
                                    y1 = char_positions[char] + rect_height
                            elif expansion['expand_above']:
                                y0 = char_positions[char] - rect_height
                                # Check if we should extend into contracted space below
                                if expansion.get('expand_below_extra', False):
                                    y1 = char_positions[char] + rect_height/2 + rect_height/3  # Made longer
                                else:
                                    y1 = char_positions[char] + rect_height/2
                            elif expansion['expand_below']:
                                # Check if we should extend into contracted space above
                                if expansion.get('expand_above_extra', False):
                                    y0 = char_positions[char] - rect_height/2 - rect_height/3  # Made longer
                                else:
                                    y0 = char_positions[char] - rect_height/2
                                y1 = char_positions[char] + rect_height
                        
                        # Apply contraction if this character needs to be contracted due to adjacent expansion
                        elif char in contractions:
                            contraction = contractions[char]
                            if contraction['contract_above'] and contraction['contract_below']:
                                # Contract from both sides (though this case might not occur in practice)
                                y0 = char_positions[char] - rect_height/8  # Made much smaller
                                y1 = char_positions[char] + rect_height/8  # Made much smaller
                            elif contraction['contract_above']:
                                # Contract from above (neighbor below is expanding)
                                y0 = char_positions[char] - rect_height/8  # Made much shorter
                                y1 = char_positions[char] + rect_height/2
                            elif contraction['contract_below']:
                                # Contract from below (neighbor above is expanding)
                                y0 = char_positions[char] - rect_height/2
                                y1 = char_positions[char] + rect_height/8  # Made much shorter
                        
                        # Create SVG path for rounded rectangle
                        path = (f'M {x0+corner_radius} {y0} L {x1-corner_radius} {y0} ' 
                            f'Q {x1} {y0} {x1} {y0+corner_radius} L {x1} {y1-corner_radius} ' 
                            f'Q {x1} {y1} {x1-corner_radius} {y1} L {x0+corner_radius} {y1} ' 
                            f'Q {x0} {y1} {x0} {y1-corner_radius} L {x0} {y0+corner_radius} ' 
                            f'Q {x0} {y0} {x0+corner_radius} {y0} Z')
                        
                        # Add the shape without any border
                        shape_to_add = dict(
                            type="path",
                            path=path,
                            fillcolor=color,
                            opacity=1.0,
                            line=dict(width=0),  # No border
                            xref="x",
                            yref="y",
                            layer="between"  # Changed from "above" to "between" for participants
                        )

                        if char in expansions:
                            expanded_shapes.append(shape_to_add)
                        elif char in contractions:
                            # Contracted shapes should also be on the "between" layer but not necessarily above expanded ones
                            all_shapes.append(shape_to_add)
                        else:
                            all_shapes.append(shape_to_add)
                        
                        # Add corner coverings for character participation in multiple events
                        if char in char_event_participation:
                            # Define corner positions mapping to specific events in the group (up to 4 events max)
                            # Each corner position corresponds to a specific event index in the group
                            corner_event_mapping = [
                                ('top_left', x0, y0, 0),        # Event 0 -> Top left
                                ('top_right', x1, y0, 1),       # Event 1 -> Top right
                                ('bottom_left', x0, y1, 2),     # Event 2 -> Bottom left
                                ('bottom_right', x1, y1, 3),    # Event 3 -> Bottom right
                                ('left_line', x0, (y0+y1)/2, 4),   # Event 4 -> Left line
                                ('right_line', x1, (y0+y1)/2, 5)   # Event 5 -> Right line
                            ]

                            # Silver color for corner coverings
                            corner_color = "rgba(192, 192, 192, 0.9)"  # Bright silver with slight transparency
                            background_color = '#111111' # Plot background color
                            border_width = 0.12 # Width of the indicator border

                            # Add corner coverings for each event this character participates in
                            # Now we check which specific events the character participates in and show the corresponding corners
                            for event_idx in char_event_participation[char]:
                                # Find the corner position for this specific event
                                corner_mapping = None
                                for corner_name, corner_x, corner_y, mapped_event_idx in corner_event_mapping:
                                    if mapped_event_idx == event_idx:
                                        corner_mapping = (corner_name, corner_x, corner_y)
                                        break
                                
                                if corner_mapping:  # Only show if we have a valid corner mapping for this event
                                    corner_name, corner_x, corner_y = corner_mapping

                                    # Path for the silver indicator
                                    indicator_path = ""

                                    # Standardized indicator dimensions for slim consistent lines
                                    indicator_length = border_width * 1.8  # Length of the arms extending from corner
                                    line_thickness = border_width * 0.6  # Consistent thickness for all indicators - increased width
                                    
                                    if corner_name == 'top_left':
                                        # Top-left corner indicator - slim L-shape following rectangle contour
                                        # Outer path for the L-shape
                                        outer_path = f"M {corner_x} {corner_y + corner_radius + indicator_length} L {corner_x} {corner_y + corner_radius} Q {corner_x} {corner_y} {corner_x + corner_radius} {corner_y} L {corner_x + corner_radius + indicator_length} {corner_y}"
                                        # Inner path (inset by line_thickness)
                                        inner_path = f"L {corner_x + corner_radius + indicator_length} {corner_y + line_thickness} L {corner_x + corner_radius} {corner_y + line_thickness} Q {corner_x + line_thickness} {corner_y + line_thickness} {corner_x + line_thickness} {corner_y + corner_radius} L {corner_x + line_thickness} {corner_y + corner_radius + indicator_length} Z"
                                        indicator_path = outer_path + inner_path
                                    elif corner_name == 'top_right':
                                        # Top-right corner indicator - slim L-shape following rectangle contour
                                        outer_path = f"M {corner_x - corner_radius - indicator_length} {corner_y} L {corner_x - corner_radius} {corner_y} Q {corner_x} {corner_y} {corner_x} {corner_y + corner_radius} L {corner_x} {corner_y + corner_radius + indicator_length}"
                                        inner_path = f"L {corner_x - line_thickness} {corner_y + corner_radius + indicator_length} L {corner_x - line_thickness} {corner_y + corner_radius} Q {corner_x - line_thickness} {corner_y + line_thickness} {corner_x - corner_radius} {corner_y + line_thickness} L {corner_x - corner_radius - indicator_length} {corner_y + line_thickness} Z"
                                        indicator_path = outer_path + inner_path
                                    elif corner_name == 'bottom_left':
                                        # Bottom-left corner indicator - slim L-shape following rectangle contour
                                        outer_path = f"M {corner_x + corner_radius + indicator_length} {corner_y} L {corner_x + corner_radius} {corner_y} Q {corner_x} {corner_y} {corner_x} {corner_y - corner_radius} L {corner_x} {corner_y - corner_radius - indicator_length}"
                                        inner_path = f"L {corner_x + line_thickness} {corner_y - corner_radius - indicator_length} L {corner_x + line_thickness} {corner_y - corner_radius} Q {corner_x + line_thickness} {corner_y - line_thickness} {corner_x + corner_radius} {corner_y - line_thickness} L {corner_x + corner_radius + indicator_length} {corner_y - line_thickness} Z"
                                        indicator_path = outer_path + inner_path
                                    elif corner_name == 'bottom_right':
                                        # Bottom-right corner indicator - slim L-shape following rectangle contour
                                        outer_path = f"M {corner_x} {corner_y - corner_radius - indicator_length} L {corner_x} {corner_y - corner_radius} Q {corner_x} {corner_y} {corner_x - corner_radius} {corner_y} L {corner_x - corner_radius - indicator_length} {corner_y}"
                                        inner_path = f"L {corner_x - corner_radius - indicator_length} {corner_y - line_thickness} L {corner_x - corner_radius} {corner_y - line_thickness} Q {corner_x - line_thickness} {corner_y - line_thickness} {corner_x - line_thickness} {corner_y - corner_radius} L {corner_x - line_thickness} {corner_y - corner_radius - indicator_length} Z"
                                        indicator_path = outer_path + inner_path
                                    elif corner_name == 'left_line':
                                        # Left side vertical line indicator - slimmer thickness
                                        line_length = rect_height * 0.35  # Slightly shorter for better proportion
                                        line_top = corner_y - line_length/2
                                        line_bottom = corner_y + line_length/2
                                        vertical_line_thickness = line_thickness * 0.5  # Make vertical lines slimmer
                                        indicator_path = f"M {corner_x} {line_top} L {corner_x + vertical_line_thickness} {line_top} L {corner_x + vertical_line_thickness} {line_bottom} L {corner_x} {line_bottom} Z"
                                    elif corner_name == 'right_line':
                                        # Right side vertical line indicator - slimmer thickness
                                        line_length = rect_height * 0.35  # Slightly shorter for better proportion
                                        line_top = corner_y - line_length/2
                                        line_bottom = corner_y + line_length/2
                                        vertical_line_thickness = line_thickness * 0.5  # Make vertical lines slimmer
                                        indicator_path = f"M {corner_x - vertical_line_thickness} {line_top} L {corner_x} {line_top} L {corner_x} {line_bottom} L {corner_x - vertical_line_thickness} {line_bottom} Z"

                                    # Add the indicator shape
                                    all_shapes.append(
                                        dict(
                                            type="path",
                                            path=indicator_path,
                                            fillcolor=corner_color,
                                            opacity=1.0,
                                            line=dict(width=0.5, color=background_color),  # Add thin border with background color
                                            xref="x",
                                            yref="y",
                                            layer="above"  # Place indicator on top
                                        )
                                    )
                        
                        # Add description text if this character has been assigned a description
                        if char in assigned_descriptions:
                            desc_info = assigned_descriptions[char]
                            expansion_info = expansions.get(char, None)
                            # Calculate the actual center of the rectangle for text positioning
                            rect_center_y = (y0 + y1) / 2
                            add_description_text(
                                all_text_traces, 
                                x_position, 
                                rect_center_y,  # Use actual rectangle center instead of char_position
                                desc_info["desc"], 
                                desc_info["important"],
                                rect_height,
                                char,
                                char_positions,
                                event_rects,
                                desc_info["event_idx"],  # Use the stored original event index
                                expansion_info,
                                desc_info["death"]  # Pass death information
                            )
                        
                        # Add hover info for this character showing all events they're involved in
                        # Collect all events this character participates in
                        char_events = []
                        char_event_ids = []  # Track event IDs to avoid duplicates
                        for event_idx, event in event_group:
                            # Check if this character is involved in this specific event
                            event_chars = []
                            if isinstance(event['Characters'], str):
                                for char_name in [c.strip() for c in event['Characters'].split(',')]:
                                    normalized = normalize_character_name(char_name)
                                    main_normalized = normalize_character_name(char)
                                    if normalized in main_normalized or main_normalized in normalized:
                                        if event_idx not in char_event_ids:
                                            char_events.append(event)
                                            char_event_ids.append(event_idx)
                                        break
                            
                            # Also check if they're the FirstMainCharacter
                            if event.get('FirstMainCharacter') == char:
                                if event_idx not in char_event_ids:
                                    char_events.append(event)
                                    char_event_ids.append(event_idx)
                        
                        # Create a single hover trace for this character with all their events
                        if char_events:
                            # For multiple events, show the most relevant one (first main character event if available)
                            primary_event = None
                            for event in char_events:
                                if event.get('FirstMainCharacter') == char:
                                    primary_event = event
                                    break
                            if primary_event is None:
                                primary_event = char_events[0]
                            
                            hover_desc = primary_event.get('Full_Description', primary_event.get('FormattedDescription', ''))
                            hover_date = primary_event['Date'].strftime('%Y-%m-%d')
                            
                            # Check if this is a death event
                            death_value = primary_event.get('Death', False)
                            is_death = death_value == True or death_value == 'True'
                            
                            # Wrap the description and characters for better vertical display
                            wrapped_description = wrap_event_text(hover_desc, width=50)
                            wrapped_characters = wrap_event_text(primary_event.get('Characters', 'N/A'), width=40)
                            
                            # Get character color for hover background
                            char_color = character_colors.get(char, "#FFFFFF")
                            
                            # For death events, override with grey background and white text
                            if is_death:
                                char_color = "#868686"  # Grey background for death events (same as rectangle color)
                                text_color = "white"
                                # Add skull emoji after the main character name for death events
                                skull_emoji = "                                                                             💀"
                                hovertemplate = f'<b style="color:{text_color}; text-align: center;">%{{customdata[0]}}{skull_emoji}</b><br><span style="color:{text_color}; text-align: center;">%{{customdata[1]}}</span><br><br><span style="color:{text_color}; text-align: center;">%{{customdata[2]}}</span><br><br><i style="color:{text_color}; text-align: center;">Characters:<br>%{{customdata[3]}}</i><extra></extra>'
                            else:
                                # Calculate text color based on background brightness for normal events
                                text_color = 'black' if np.mean([int(char_color[i:i+2], 16) for i in (1, 3, 5)]) > 128 else 'white'
                                # Add star emoji after the main character name for normal events
                                star_emoji = "                                                                             ⭐"
                                hovertemplate = f'<b style="color:{text_color}">%{{customdata[0]}}{star_emoji}</b><br><span style="color:{text_color}">%{{customdata[1]}}</span><br><br><span style="color:{text_color}">%{{customdata[2]}}</span><br><br><i style="color:{text_color}">Characters:<br>%{{customdata[3]}}</i><extra></extra>'
                            
                            all_hover_traces.append(
                                go.Scatter(
                                    x=[x_position],
                                    y=[char_positions[char]],
                                    mode='markers',
                                    marker=dict(
                                        opacity=0,
                                        size=10,
                                    ),
                                    hoverinfo='all',
                                    customdata=[[primary_event.get('FirstMainCharacter', 'N/A'), hover_date, wrapped_description, wrapped_characters]],
                                    hovertemplate=hovertemplate,
                                    hoverlabel=dict(bgcolor=char_color, bordercolor="white", font=dict(color=text_color)),
                                    showlegend=False
                                )
                            )
                    
                    # Handle non-participants
                    elif show_non_participants:
                        event_date_str = event_group[0][1]['Date'].strftime('%d-%m-%Y')
                        add_non_participant_rectangles([char], x_position, event_date_str)
        
        # Add interactive buttons for merged events
        for idx, (event_idx, event) in enumerate(event_group):
            # Position buttons relative to the first main character of each event
            if event.get('FirstMainCharacter') and event['FirstMainCharacter'] in char_positions:
                char_position = char_positions[event['FirstMainCharacter']]
                add_interactive_buttons(all_hover_traces, x_position, char_position, event, event_idx, rect_width, rect_height, events_df)
        
        # Increment output_position for the next event or merged group
        # --- Add horizontal slit for world indicator here ---
        world_colors = {
            "Jonas": "#f9b405", #Gold
            "Martha": "#9803f6", #Purple
            "Origin": "#032ff6", #Blue
            "Origin (End)": "#032ff6", #Blue
        }
        
        # Determine world for this group (handle both single and merged events)
        if len(event_group) > 1 and 'World' in event_group[0][1]:
            world = event_group[0][1]['World']
        else:
            world = event_group[0][1].get('World', None)
        
        x_pos = output_position * event_spacing
        slit_y = len(main_characters) * character_spacing + 0.5  # Position below the plot area but within visible range
        slit_width = rect_width * 1.2
        slit_height = 0.2  # Height for the rounded rectangle
        
        # Create coordinates for the world indicator
        x0 = x_pos - slit_width + 0.15
        x1 = x_pos + slit_width - 0.15
        y0 = slit_y - slit_height/2
        y1 = slit_y + slit_height/2
        
        # Check for mixed world scenarios (e.g., "Jonas/Martha", "Martha/Jonas")
        if world and "/" in world:
            # Split the world names
            world_parts = [w.strip() for w in world.split("/")]
            if len(world_parts) == 2:
                first_world = world_parts[0]
                second_world = world_parts[1]
                first_color = world_colors.get(first_world, "#FFFFFF")
                second_color = world_colors.get(second_world, "#FFFFFF")
                
                # Create left half with first world color
                x_mid = (x0 + x1) / 2
                left_path = (f'M {x0+corner_radius} {y0} L {x_mid} {y0} ' 
                            f'L {x_mid} {y1} L {x0+corner_radius} {y1} ' 
                            f'Q {x0} {y1} {x0} {y1-corner_radius} L {x0} {y0+corner_radius} ' 
                            f'Q {x0} {y0} {x0+corner_radius} {y0} Z')
                
                all_shapes.append(
                    dict(
                        type="path",
                        path=left_path,
                        fillcolor=first_color,
                        opacity=1.0,
                        line=dict(width=0),
                        xref="x",
                        yref="y",
                        layer="above"
                    )
                )
                
                # Create right half with second world color
                right_path = (f'M {x_mid} {y0} L {x1-corner_radius} {y0} ' 
                             f'Q {x1} {y0} {x1} {y0+corner_radius} L {x1} {y1-corner_radius} ' 
                             f'Q {x1} {y1} {x1-corner_radius} {y1} L {x_mid} {y1} ' 
                             f'L {x_mid} {y0} Z')
                
                all_shapes.append(
                    dict(
                        type="path",
                        path=right_path,
                        fillcolor=second_color,
                        opacity=1.0,
                        line=dict(width=0),
                        xref="x",
                        yref="y",
                        layer="above"
                    )
                )
            else:
                # Fallback for unexpected format - use single color
                world_color = world_colors.get(world, "#FFFFFF")
                path = (f'M {x0+corner_radius} {y0} L {x1-corner_radius} {y0} ' 
                       f'Q {x1} {y0} {x1} {y0+corner_radius} L {x1} {y1-corner_radius} ' 
                       f'Q {x1} {y1} {x1-corner_radius} {y1} L {x0+corner_radius} {y1} ' 
                       f'Q {x0} {y1} {x0} {y1-corner_radius} L {x0} {y0+corner_radius} ' 
                       f'Q {x0} {y0} {x0+corner_radius} {y0} Z')
                
                all_shapes.append(
                    dict(
                        type="path",
                        path=path,
                        fillcolor=world_color,
                        opacity=1.0,
                        line=dict(width=0),
                        xref="x",
                        yref="y",
                        layer="above"
                    )
                )
        else:
            # Single world scenario - use original logic
            world_color = world_colors.get(world, "#FFFFFF")
            path = (f'M {x0+corner_radius} {y0} L {x1-corner_radius} {y0} ' 
                   f'Q {x1} {y0} {x1} {y0+corner_radius} L {x1} {y1-corner_radius} ' 
                   f'Q {x1} {y1} {x1-corner_radius} {y1} L {x0+corner_radius} {y1} ' 
                   f'Q {x0} {y1} {x0} {y1-corner_radius} L {x0} {y0+corner_radius} ' 
                   f'Q {x0} {y0} {x0+corner_radius} {y0} Z')
            
            all_shapes.append(
                dict(
                    type="path",
                    path=path,
                    fillcolor=world_color,
                    opacity=1.0,
                    line=dict(width=0),
                    xref="x",
                    yref="y",
                    layer="above"
                )
            )
        output_position += 1

    # Add all shapes to the figure in a single operation
    # Non-expanded shapes first
    for shape in all_shapes:
        fig.add_shape(shape)
    
    # Then expanded shapes, so they are drawn on top
    for shape in expanded_shapes:
        fig.add_shape(shape)

    # Add all traces to the figure
    for trace in all_text_traces:
        fig.add_trace(trace)
    
    for trace in all_hover_traces:
        fig.add_trace(trace)
    
    # Calculate max positions for proper axis limits
    # Use output_position instead of len(events_df) to account for merged events
    max_x = output_position * event_spacing
    total_char_space = len(main_characters) * character_spacing
    
    # Calculate dead space in data coordinates (approximately 600px converted to data units)
    # Assuming roughly 100 pixels per data unit, 600px ≈ 6 data units
    dead_space_data_units = 6.0
    
    # Add background image to cover the entire plot area with extension
    fig.add_layout_image(
        dict(
            source="C:/Users/User/Desktop/CurrentVersion/bgimplusplus.png",
            xref="x",
            yref="y",
            x=-6,  # Extended even further left to ensure full coverage
            y=-dead_space_data_units - 2,  # Start from below the dead space area
            sizex=max_x + 12,  # Cover more width (6 units on each side for full coverage)
            sizey=total_char_space + dead_space_data_units + 6,  # Cover from dead space to bottom of plot
            sizing="stretch",  # Force the image to stretch to fill the entire specified area
            opacity=1.0,
            layer="below"
        )
    )

    # Calculate the figure height to make the plot area exactly 1600px
    # The plot area height should be 1600px, so we calculate figure height accordingly
    target_plot_height = 1600  # Target height for the plot area in pixels
    dead_space_top = 600  # Additional dead space at the top in pixels
    figure_height = target_plot_height + dead_space_top  # Set figure height to achieve 1600px plot area + dead space

    # Format character names with line breaks at the "/" and add extra line break between names
    formatted_character_names = [" " for _ in main_characters]  # Empty y-axis labels
    
    # Add character labels as rectangles
    label_width = 2  # Width for character name labels
    for char, y_pos in char_positions.items():
        color = character_colors.get(char, "#FFFFFF")
        
        all_shapes.append(
            dict(
                type="rect",
                x0=-label_width, x1=0,
                y0=y_pos - rect_height / 2, y1=y_pos + rect_height / 2,
                fillcolor=color,
                line=dict(color="black", width=2),
                xref="x", yref="y",
                layer="above"
            )
        )
        
        # Create character label text trace with proper naming and data structure
        char_label_trace = go.Scatter(
            x=[-label_width / 2],
            y=[char_positions[char]],
            mode='text',
            text=[char],
            textfont=dict(color='white', size=8),
            hoverinfo='none',
            showlegend=False,
            name=f'character_label_{char.replace(" ", "_").replace("/", "_")}',
            # Use -1 as event_idx to indicate character label
            # Format: [event_idx, character, x_position, original_color, is_character_label]
            customdata=[-1, char, -label_width / 2, 'white', True],
            # Add metadata for easier JavaScript access
            meta={
                'event_idx': -1,
                'character': char,
                'x_position': -label_width / 2,
                'original_color': 'white',
                'trace_type': 'character_label'
            }
        )
        
        all_text_traces.append(char_label_trace)
    
    # Create unique date labels for x-axis - use position instead of index
    unique_dates = []
    unique_positions = []
    unique_years = []
    year_positions = []
    last_year = None

    # Iterate through the merged events to find unique dates and their positions
    output_position = 0  # Reset output_position for date positioning
    for event_group in merged_events:
        # Use the first event in the group to determine the date
        first_event = event_group[0][1]
        date_obj = first_event['Date']
        date_str = date_obj.strftime('%d-%m-%Y')
        current_year = date_obj.year

        # Check if the date is already added
        if date_str not in unique_dates:
            # Format the date based on whether it's the first date of the year
            if current_year != last_year:
                formatted_date = date_obj.strftime('%d/%m/%Y')  # Full format for the first date of the year
                last_year = current_year
            else:
                formatted_date = date_obj.strftime('%d/%m')  # Only day-month for subsequent dates in the same year

            unique_dates.append(formatted_date)
            unique_positions.append(output_position * event_spacing)  # Use the output position for positioning

        # Increment output_position for the next event or merged group
        output_position += 1

    # Add all shapes to the figure in a single operation
    fig.update_layout(
        width=16380,
        height=figure_height,  # Dynamic height based on character spacing
        plot_bgcolor='#000000',  # Black background color as base
        paper_bgcolor='#000000',  # Black background color as base
        margin=dict(l=0, r=0, t=0, b=0),  # No margins - let plot area handle the full space
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[-2, max_x + 1],  # Add more padding on the right to ensure dates show
            tickvals=unique_positions,  # Show positions of unique dates
            ticktext=unique_dates,      # Show formatted unique date labels
            tickfont=dict(color='#FFFFFF', size=14),  # Explicit white color and larger size
            side='bottom',  # Ensure dates appear at the bottom
            showticklabels=True  # Explicitly show tick labels
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[total_char_space + 1, -dead_space_data_units],  # Extended range to show world indicators
            tickvals=[ i * character_spacing for i in range(len(main_characters))],
            ticktext=formatted_character_names,
            tickfont=dict(color='white', size=16),
            autorange=False,  # Disable autorange to maintain our custom range
            fixedrange=True,  # Prevent zooming to ensure dead space remains visible
            side='left',  # Ensure character names appear on the left
            showticklabels=True  # Explicitly show tick labels
        )
    )
    
    # Add click events to the button traces for interactive functionality
    # This will be handled via custom JavaScript when the HTML is generated
    for trace in all_hover_traces:
        if hasattr(trace, 'name') and trace.name and trace.name.startswith('btn_'):
            # Add custom data for JavaScript interaction
            if not hasattr(trace, 'customdata') or trace.customdata is None:
                trace.customdata = []
    
    return fig

# Run the visualization
if __name__ == "__main__":
    # Create visualization with configurable spacing parameters
    fig = create_dark_timeline_grid(
        character_spacing=2.5,    # Increased spacing between characters
        event_spacing=1.5,      # Adjust horizontal spacing between events
        rect_width=0.7,        # Adjust rectangle width
        rect_height=2.4,        # Adjusted rectangle height to match character spacing
        show_non_participants=True,  # Set to False to disable non-participant rectangles
        asymmetric_expansion=True     # Enable asymmetric expansion for adjacent rectangles with text
    )
    
    # Save as interactive HTML with custom JavaScript for button functionality
    # Configure to completely remove all toolbar functionality and interactions
    config = {
        'displayModeBar': False,  # This removes the entire toolbar
        'displaylogo': False,
        'staticPlot': False,  # Keep interactivity for hover and clicks
        'scrollZoom': False,  # Disable scroll zoom
        'doubleClick': False,  # Disable double-click zoom
        'showTips': False,  # Disable tips
        'showAxisDragHandles': False,  # Disable axis drag handles
        'showAxisRangeEntryBoxes': False,  # Disable axis range entry boxes
        'dragmode': False,  # Disable all drag modes (zoom, pan, etc.)
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'timeline',
            'height': 1200,
            'width': 12288,
            'scale': 1
        }
    }
    
    html_string = pio.to_html(fig, include_plotlyjs=True, config=config)
    
    # Add CSS to ensure no gray overlay from HTML/body elements and force white dates
    css_injection = """
    <style>
    body, html {
        background-color: transparent !important;
        background: transparent !important;
    }
    .plotly-graph-div {
        background-color: transparent !important;
        background: transparent !important;
    }
    .main-svg {
        background-color: transparent !important;
        background: transparent !important;
    }
    /* Force white color for date labels */
    .xtick text {
        fill: white !important;
        color: white !important;
    }
    .xaxis .tick text {
        fill: white !important;
        color: white !important;
    }
    </style>
    """
    
    # Inject CSS into the HTML
    html_string = html_string.replace('<head>', '<head>' + css_injection)
    
    # Create simple event data mapping for JavaScript
    all_events_data = []
    shape_to_event_mapping = []  # Maps shape index to event info
    
    # Process events to create mapping
    shape_index = 0
    for idx, row in events_df.iterrows():
        event_data = {
            'event_idx': idx,
            'type': row.get('Type', ''),
            'characters': row.get('Characters', ''),
            'first_main_character': row.get('FirstMainCharacter', ''),
            'date': row['Date'].strftime('%Y-%m-%d') if pd.notnull(row['Date']) else ''
        }
        all_events_data.append(event_data)
        
        # Add shape mapping info for this event
        # Note: This is a simplified mapping - in reality, each event can have multiple shapes
        # We'll need to enhance this in the JavaScript side
        shape_to_event_mapping.append({
            'event_idx': idx,
            'event_type': row.get('Type', ''),
            'shape_start_index': shape_index  # Will be updated when we know actual count
        })
    
    # Convert to JavaScript format
    import json
    all_events_js = json.dumps(all_events_data)
    
    # Add custom JavaScript for button click handling
    custom_js = f"""
    <script>
    // Event data injected from Python
    var allEventsData = {all_events_js};
    
    document.addEventListener('DOMContentLoaded', function() {{
        var graphDiv = document.getElementsByClassName('plotly-graph-div')[0];
        
        // Store original properties for reset functionality
        var originalShapeProperties = {{}};
        var originalTraceProperties = {{}};
        var removedTextTraces = [];  // Store removed text traces for restoration
        var removedTextIndices = [];  // Track which indices were removed
        var isHighlightActive = false;
        var currentHighlightType = null;
        var currentHighlightNumber = null;
        
        // Function to check if an event's Type contains the target pattern
        function eventContainsType(eventType, targetType, targetNumber) {{
            if (!eventType) return false;
            
            // Handle both exact matches and typos
            var patterns = [];
            if (targetType === "Successful Time Travel") {{
                patterns = [
                    "Successful Time Travel (" + targetNumber + ")",
                    "Succesfull Time Travel (" + targetNumber + ")"
                ];
            }} else if (targetType === "World Swap") {{
                patterns = [
                    "World Swap (" + targetNumber + ")"
                ];
            }} else {{
                patterns = [targetType + " (" + targetNumber + ")"];
            }}
            
            for (var pattern of patterns) {{
                if (eventType.includes(pattern)) {{
                    return true;
                }}
            }}
            return false;
        }}
        
        // Function to get all event indices that contain the target type
        function getMatchingEventIndices(targetType, targetNumber) {{
            var matchingIndices = [];
            for (var i = 0; i < allEventsData.length; i++) {{
                if (eventContainsType(allEventsData[i].type, targetType, targetNumber)) {{
                    matchingIndices.push(allEventsData[i].event_idx);
                }}
            }}
            return matchingIndices;
        }}
        
        // Function to get positions of events that should stay bright
        function getPositionsToKeepBright(targetType, targetNumber) {{
            var brightPositions = [];
            var data = graphDiv.data;
            var matchingEventIndices = getMatchingEventIndices(targetType, targetNumber);
            
            // Only go through button traces to find exact matching events
            for (var i = 0; i < data.length; i++) {{
                var trace = data[i];
                if (trace.name && trace.name.startsWith('btn_') && trace.customdata) {{
                    var eventIdx = trace.customdata[2]; // Event index from button
                    var eventX = trace.customdata[3];   // X position of event
                    var eventY = trace.customdata[4];   // Y position of event
                    var buttonEventType = trace.customdata[0]; // Button's event type
                    var buttonEventNumber = trace.customdata[1]; // Button's event number
                    
                    // Only include if this button is for the exact same type and number we're highlighting
                    if (buttonEventType === targetType && buttonEventNumber === targetNumber && matchingEventIndices.includes(eventIdx)) {{
                        brightPositions.push({{
                            x: eventX,
                            y: eventY,
                            eventIdx: eventIdx
                        }});
                    }}
                }}
            }}
            
            return brightPositions;
        }}
        
        // Function to restore all removed text traces
        function restoreAllTextTraces() {{
            if (removedTextTraces.length > 0) {{
                // Add back all the removed traces at their original positions
                var tracesToAdd = [];
                var addIndices = [];
                
                for (var i = 0; i < removedTextTraces.length; i++) {{
                    tracesToAdd.push(removedTextTraces[i]);
                    addIndices.push(removedTextIndices[i]);
                }}
                
                // Add traces back to the plot
                Plotly.addTraces(graphDiv, tracesToAdd, addIndices);
                
                // Clear the storage arrays
                removedTextTraces = [];
                removedTextIndices = [];
            }}
        }}
        
        // Function to reset all highlighting and restore text visibility
        function resetHighlight() {{
            if (!isHighlightActive) return;
            
            isHighlightActive = false;
            currentHighlightType = null;
            currentHighlightNumber = null;
            
            // Restore all removed text traces first
            restoreAllTextTraces();
            
            // Restore original shape properties
            var layout = graphDiv.layout;
            var updateShapes = [];
            
            if (layout.shapes) {{
                for (var i = 0; i < layout.shapes.length; i++) {{
                    var shape = JSON.parse(JSON.stringify(layout.shapes[i]));
                    shape.opacity = originalShapeProperties[i].opacity;
                    shape.fillcolor = originalShapeProperties[i].fillcolor;
                    updateShapes.push(shape);
                }}
            }}
            
            // Restore trace properties for non-text traces
            var updateData = [];
            var data = graphDiv.data;
            
            for (var i = 0; i < data.length; i++) {{
                var trace = data[i];
                var newTrace = {{}};
                
                // Only update non-text traces (buttons, hover traces, etc.)
                if (!trace.mode || !trace.mode.includes('text')) {{
                    newTrace.opacity = originalTraceProperties[i] ? originalTraceProperties[i].opacity : 1.0;
                    if (originalTraceProperties[i] && originalTraceProperties[i].marker) {{
                        newTrace.marker = JSON.parse(JSON.stringify(originalTraceProperties[i].marker));
                    }}
                }} else {{
                    // For text traces, keep them as they are (already restored above)
                    newTrace.opacity = 1.0;
                }}
                
                updateData.push(newTrace);
            }}
            
            // Apply updates
            Plotly.update(graphDiv, updateData, {{shapes: updateShapes}});
        }}
        
        // Main highlighting function with improved text handling
        function highlightMatchingEvents(targetType, targetNumber) {{
            if (isHighlightActive && currentHighlightType === targetType && currentHighlightNumber === targetNumber) {{
                resetHighlight();
                return;
            }}
            
            // Store original properties if not already stored
            if (!isHighlightActive) {{
                var layout = graphDiv.layout;
                var data = graphDiv.data;
                
                // Store original shape properties
                if (layout.shapes) {{
                    for (var i = 0; i < layout.shapes.length; i++) {{
                        originalShapeProperties[i] = {{
                            opacity: layout.shapes[i].opacity || 1.0,
                            fillcolor: layout.shapes[i].fillcolor
                        }};
                    }}
                }}
                
                // Store original trace properties
                for (var i = 0; i < data.length; i++) {{
                    originalTraceProperties[i] = {{
                        opacity: data[i].opacity || 1.0,
                        marker: data[i].marker ? JSON.parse(JSON.stringify(data[i].marker)) : undefined,
                        textfont: data[i].textfont ? JSON.parse(JSON.stringify(data[i].textfont)) : undefined
                    }};
                }}
            }}
            
            isHighlightActive = true;
            currentHighlightType = targetType;
            currentHighlightNumber = targetNumber;
            
            // Get positions and indices
            var brightPositions = getPositionsToKeepBright(targetType, targetNumber);
            var matchingEventIndices = getMatchingEventIndices(targetType, targetNumber);
            
            // Update shapes (rectangles and paths)
            var layout = graphDiv.layout;
            var updateShapes = [];
            
            if (layout.shapes) {{
                for (var i = 0; i < layout.shapes.length; i++) {{
                    var shape = JSON.parse(JSON.stringify(layout.shapes[i]));
                    var shouldStayBright = false;
                    
                    // Extract shape position
                    var shapeX = null;
                    var shapeY = null;
                    
                    if (shape.type === 'rect') {{
                        shapeX = (shape.x0 + shape.x1) / 2;
                        shapeY = (shape.y0 + shape.y1) / 2;
                    }} else if (shape.path) {{
                        // Extract coordinates from SVG path
                        var pathMatch = shape.path.match(/M\\s*([\\d\\.\\-]+)\\s*([\\d\\.\\-]+)/);
                        if (pathMatch) {{
                            var allMatches = shape.path.match(/([\\d\\.\\-]+)/g);
                            if (allMatches && allMatches.length >= 4) {{
                                var yCoords = [];
                                for (var j = 1; j < allMatches.length; j += 2) {{
                                    yCoords.push(parseFloat(allMatches[j]));
                                }}
                                if (yCoords.length > 0) {{
                                    var minY = Math.min(...yCoords);
                                    var maxY = Math.max(...yCoords);
                                    shapeY = (minY + maxY) / 2;
                                    
                                    var xCoords = [];
                                    for (var j = 0; j < allMatches.length; j += 2) {{
                                        xCoords.push(parseFloat(allMatches[j]));
                                    }}
                                    if (xCoords.length > 0) {{
                                        var minX = Math.min(...xCoords);
                                        var maxX = Math.max(...xCoords);
                                        shapeX = (minX + maxX) / 2;
                                    }}
                                }}
                            }}
                        }}
                    }}
                    
                    // Check if this shape should stay bright
                    if (shapeX !== null && shapeY !== null) {{
                        // Always keep world indicators bright (they have layer="above")
                        if (shape.layer === "above") {{
                            shouldStayBright = true;
                        }} else {{
                            // Only dim event rectangles - check against event positions
                            for (var pos of brightPositions) {{
                                if (Math.abs(shapeX - pos.x) < 0.1 && Math.abs(shapeY - pos.y) < 1.5) {{
                                    shouldStayBright = true;
                                    break;
                                }}
                            }}
                        }}
                    }}
                    
                    if (shouldStayBright) {{
                        shape.opacity = originalShapeProperties[i].opacity;
                        shape.fillcolor = originalShapeProperties[i].fillcolor;
                    }} else {{
                        shape.opacity = 0.15;
                    }}
                    
                    updateShapes.push(shape);
                }}
            }}
            
            // First, restore any previously removed text traces
            restoreAllTextTraces();
            
            // Update traces with text removal approach
            var data = graphDiv.data;
            var updateData = [];
            var tracesToRemove = []; // Indices of text traces to remove
            
            for (var i = 0; i < data.length; i++) {{
                var trace = data[i];
                var newTrace = {{}};
                
                // Handle button traces
                if (trace.name && trace.name.startsWith('btn_') && trace.customdata) {{
                    var eventType = trace.customdata[0];
                    var eventNumber = trace.customdata[1];
                    
                    if (eventType === targetType && eventNumber === targetNumber) {{
                        newTrace.opacity = 1.0;
                        if (trace.marker) {{
                            newTrace.marker = JSON.parse(JSON.stringify(trace.marker));
                            newTrace.marker.opacity = 1.0;
                        }}
                    }} else {{
                        newTrace.opacity = 0.3;
                        if (trace.marker) {{
                            newTrace.marker = JSON.parse(JSON.stringify(trace.marker));
                            newTrace.marker.opacity = 0.3;
                        }}
                    }}
                }} else {{
                    // Handle text and other traces
                    var isTextTrace = trace.mode && trace.mode.includes('text');
                    
                    if (isTextTrace) {{
                        // Character labels always stay visible
                        if (trace.name && trace.name.startsWith('character_label_')) {{
                            newTrace.opacity = 1.0;
                            if (originalTraceProperties[i].textfont) {{
                                newTrace.textfont = JSON.parse(JSON.stringify(originalTraceProperties[i].textfont));
                            }}
                        }} 
                        // Event text traces - check if they belong to matching events
                        else if (trace.name && trace.name.startsWith('text_trace_') && trace.customdata) {{
                            var textEventIdx = trace.customdata[0];
                            
                            if (!matchingEventIndices.includes(textEventIdx)) {{
                                // Mark this text trace for removal
                                tracesToRemove.push(i);
                                // Skip adding update data for traces to be removed
                                continue;
                            }} else {{
                                // Keep matching text visible with original styling
                                var originalColor = trace.customdata[3];
                                newTrace.opacity = 1.0;
                                newTrace.textfont = {{
                                    color: originalColor,
                                    size: (originalTraceProperties[i].textfont && originalTraceProperties[i].textfont.size) || 14
                                }};
                            }}
                        }} else {{
                            // Other text traces - keep original
                            newTrace.opacity = originalTraceProperties[i].opacity;
                            if (originalTraceProperties[i].textfont) {{
                                newTrace.textfont = JSON.parse(JSON.stringify(originalTraceProperties[i].textfont));
                            }}
                        }}
                    }} else {{
                        // Non-text traces (hover traces, etc.)
                        var shouldKeepVisible = false;
                        
                        // Check if this hover trace is related to a matching event
                        if (trace.customdata && trace.customdata.length > 0) {{
                            for (var pos of brightPositions) {{
                                if (trace.x && trace.y && trace.x.length > 0 && trace.y.length > 0) {{
                                    if (Math.abs(trace.x[0] - pos.x) < 0.1 && Math.abs(trace.y[0] - pos.y) < 1.5) {{
                                        shouldKeepVisible = true;
                                        break;
                                    }}
                                }}
                            }}
                        }}
                        
                        newTrace.opacity = shouldKeepVisible ? 1.0 : 0.15;
                    }}
                }}
                
                updateData.push(newTrace);
            }}
            
            // Apply updates to remaining traces first
            Plotly.update(graphDiv, updateData, {{shapes: updateShapes}});
            
            // Now remove the non-matching text traces
            if (tracesToRemove.length > 0) {{
                // Store the traces before removing them, in reverse order to maintain indices
                tracesToRemove.sort((a, b) => b - a); // Sort in descending order
                
                for (var idx of tracesToRemove) {{
                    removedTextTraces.push(JSON.parse(JSON.stringify(data[idx])));
                    removedTextIndices.push(idx);
                }}
                
                // Remove traces (in descending order to maintain correct indices)
                Plotly.deleteTraces(graphDiv, tracesToRemove);
            }}
        }}
        
        // Add click event listener
        graphDiv.on('plotly_click', function(data) {{
            var point = data.points[0];
            var trace = graphDiv.data[point.curveNumber];
            
            // Check if clicked point is a button
            if (trace.name && trace.name.startsWith('btn_') && trace.customdata) {{
                var eventType = trace.customdata[0];
                var eventNumber = trace.customdata[1];
                
                highlightMatchingEvents(eventType, eventNumber);
            }}
        }});
        
        // Add double-click to reset
        graphDiv.on('plotly_doubleclick', function() {{
            resetHighlight();
        }});
    }});
    </script>
    """
    
    # Insert the custom JavaScript before the closing body tag
    html_string = html_string.replace('</body>', custom_js + '</body>')
    
    # Write the modified HTML
    with open("Results/fckbksfrnocap.html", "w", encoding="utf-8") as f:
        f.write(html_string)

    # Save as high-resolution image - height now scales with character spacing
    pio.write_image(fig, "Results/fckbksfrnocap.png", 
                   width=12288, height=1200, scale=1)
    

    print("Visualization created successfully!")
    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")