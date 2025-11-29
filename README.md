# Pokemon Bulbapedia Scraper

Automated tool to fetch Pokemon data from Bulbapedia and format it according to specifications.

## Features

- Fetches Pokemon category/title from Bulbapedia
- Extracts Pokedex number and Japanese name
- Formats output in a consistent format
- Processes multiple Pokemon from an input file
- Includes polite rate limiting to avoid overwhelming the server

## Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Make sure virtual environment is activated first
source venv/bin/activate

python pokedex_scraper.py <input_file> [output_file]
```

### Example

```bash
python pokedex_scraper.py pokedex_1129_input processed_output.md
```

If no output file is specified, it defaults to `processed_output.md`.

## Input Format

The input file should contain one Pokemon name per line:

```
Pinsir
Voltorb
Weedle
```

## Output Format

For each Pokemon, the output will be:

```
Name
URL: https://bulbapedia.bulbagarden.net/wiki/Name_(Pokémon)
Final: Name: Category | Japanese (Pokedex #number)

```

### Example Output

```
Pinsir
URL: https://bulbapedia.bulbagarden.net/wiki/Pinsir_(Pok%C3%A9mon)
Final: Pinsir: Stag Beetle | カイロス (Pokedex #0127)

Voltorb
URL: https://bulbapedia.bulbagarden.net/wiki/Voltorb_(Pok%C3%A9mon)
Final: Voltorb: Ball | ビリリダマ (Pokedex #0100)
```

## How It Works

1. Reads Pokemon names from the input file
2. For each Pokemon:
   - Constructs the Bulbapedia URL
   - Fetches the page content
   - Extracts the category from `span.explain`
   - Finds the Pokedex number near "List of Pokémon by National Pokédex number"
   - Extracts the Japanese name
3. Formats the data according to the specification
4. Writes all results to the output file

## Notes

- The script includes a 1-second delay between requests to be respectful to the Bulbapedia servers
- Error handling is included for network issues and parsing failures
- Progress is displayed in the console during processing

## Dependencies

- `requests`: For HTTP requests
- `beautifulsoup4`: For HTML parsing

## Troubleshooting

If you encounter issues:

1. Make sure you have an active internet connection
2. Verify that the Pokemon names are spelled correctly
3. Check that Bulbapedia is accessible (not blocked by firewall)
4. Ensure dependencies are installed: `pip install -r requirements.txt`
