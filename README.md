# Dark TV Series Interactive Event Visualization

An interactive timeline visualization that maps character participation in events throughout the Dark TV series universe, spanning from 1888 to 2053.

## 🎯 Overview

This project visualizes the complex temporal relationships and character interactions within the Dark TV series through an interactive grid-based timeline. The visualization displays characters along the Y-axis and dates along the X-axis, providing a linear progression of events while maintaining clarity on character participation patterns.

## 📊 What It Shows

The visualization reveals:
- **Character Event Participation**: How different characters are involved in events across the timeline
- **Temporal Relationships**: The linear progression of events from 1888 to 2053
- **Character Interaction Patterns**: Visual indicators showing which characters participate in the same events
- **Event Clustering**: How events are grouped by date and character involvement
- **Narrative Flow**: The chronological development of the series' complex storyline

## 🗃️ Data Processing

The dataset was processed using Python libraries including:
- **Pandas & NumPy**: For data manipulation and analysis
- **spaCy**: For natural language processing to identify character mentions
- **Plotly**: For interactive visualization generation

### Event Merging Strategy
Due to space constraints from the competition submission requirements, events were strategically merged based on:
- Minimal incoming or outgoing edges in the event network
- Event nature (excluding major deaths or pivotal plot points from merging)
- Character overlap and temporal proximity

### Description Processing
Event descriptions were:
- Summarized using large language models (LLMs) with human oversight
- Formatted using character initials to maximize space efficiency
- Analyzed using NLP to identify primary character involvement

## 🎨 Visual Design

### Character Representation
Each character is represented by a unique color carefully chosen based on their most iconic or frequently worn clothing in the series, particularly during pivotal moments.

### Event Indicators
Instead of displaying full descriptions for every character, the timeline uses:
- **Discrete markers** on rectangle corners and sides to indicate character involvement
- **Dynamic rectangle sizing** - descriptions cause rectangles to expand while non-participant rectangles may be reduced
- **Asymmetric expansion** - adjacent rectangles with text expand in complementary directions to avoid overlap

### Interactive Features
- **Hover tooltips** with detailed event information
- **Character-specific coloring** for immediate recognition
- **Zoom and pan functionality** for detailed exploration
- **World indicators** showing different timeline universes (Jonas, Martha, Origin)

## 🖥️ Technical Implementation

The project consists of:
- **Data Processing Pipeline** (`DataManipulation.py`): Cleans and processes the raw event data
- **Visualization Engine** (`Visualization.py`): Generates the interactive Plotly timeline
- **Web Interface** (`Website/`): Provides an elegant front-end with Dark-themed animations

### Key Features
- **Responsive Design**: Adapts to different screen sizes
- **Performance Optimization**: Efficient rendering of large datasets
- **Cross-browser Compatibility**: Works across modern web browsers
- **Accessibility**: Designed with dark theme and clear visual hierarchy

## 🚀 Usage

1. **View the Visualization**: Open the web interface to explore the timeline
2. **Navigate Events**: Use zoom and pan controls to focus on specific time periods
3. **Explore Characters**: Hover over rectangles to see detailed event information
4. **Analyze Patterns**: Observe character participation patterns across the timeline

## 📁 Project Structure
├── Visualization/ 
│ ├── Visualization.py # Main visualization generator 
│ ├── DataManipulation.py # Data processing pipeline 
│ ├── Visualization.html            # Interactive timeline view
│ └── Visualization.png             # Static timeline image
├── Website/ 
│ ├── index.html # Web interface 
│ ├── style.css # Dark-themed styling 
│ └── script.js # Interactive functionality 



## 🎬 About Dark TV Series

The visualization captures the intricate temporal mechanics of Dark, a German science fiction thriller that explores time travel, causal loops, and interconnected family histories across multiple generations and parallel worlds.

---

*"The question isn't how, the question is when."* - Dark TV Series
