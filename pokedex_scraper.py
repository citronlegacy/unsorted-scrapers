#!/usr/bin/env python3
"""
Pokemon Bulbapedia Scraper
Fetches Pokemon data from Bulbapedia and formats it according to specifications.
"""

import requests
from bs4 import BeautifulSoup
import sys
import time


def fetch_pokemon_data(pokemon_name):
    """
    Fetch Pokemon data from Bulbapedia.
    
    Args:
        pokemon_name: Name of the Pokemon
        
    Returns:
        dict with 'name', 'url', 'title', 'japanese', 'pokedex_number'
    """
    # Handle special cases for Pokemon names with special characters
    # Mr. Mime needs to be Mr._Mime in the URL
    url_name = pokemon_name
    display_name = pokemon_name
    
    if pokemon_name.lower() == 'mrmime':
        url_name = 'Mr._Mime'
        display_name = 'Mr. Mime'
    
    # Construct URL
    url = f"https://bulbapedia.bulbagarden.net/wiki/{url_name}_(Pok%C3%A9mon)"
    
    try:
        # Fetch the page
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get the Pokemon's category/title from the infobox
        # Look for the infobox table which contains the category
        title = ''
        infobox = soup.find('table', class_='roundy')
        if infobox:
            # The category is typically in the first row in a span.explain
            # Look for the first row with Pokemon data
            for row in infobox.find_all('tr'):
                row_text = row.get_text(strip=True)
                # Look for row containing pokemon name (use display_name which has correct format) and "Pokémon"
                if display_name.replace(' ', '') in row_text.replace(' ', '') and 'Pokémon' in row_text:
                    # Find all span.explain elements - we need to pick the English category, not Japanese
                    explain_spans = row.find_all('span', class_='explain')
                    for explain_span in explain_spans:
                        span_text = explain_span.get_text(strip=True)
                        # Check if this span contains Latin characters (not Japanese)
                        # Japanese characters are in Unicode ranges: Hiragana, Katakana, Kanji
                        is_japanese = any(ord(char) > 0x3000 for char in span_text)
                        if not is_japanese and span_text:
                            # This is the English category
                            title = span_text
                            break
                    
                    # If no English span.explain found, try fallback
                    if not title:
                        # Find any span with "Pokémon" in it
                        for span in row.find_all('span'):
                            span_text = span.get_text(strip=True)
                            # Check if this is the category
                            if 'Pokémon' in span_text and span_text != display_name and len(span_text) < 50:
                                # Extract just the category name
                                title = span_text.replace(' Pokémon', '').replace('Pokémon', '')
                                break
                    if title:
                        break
        
        # Find the Pokedex number
        # Look for text containing "List of Pokémon by National Pokédex number"
        pokedex_number = None
        japanese_name = None
        
        # Find the table with National Pokedex info
        # The number is typically in a link or span near this text
        for link in soup.find_all('a'):
            if 'List_of_Pokémon_by_National_Pokédex_number' in link.get('href', ''):
                # Look for the number in nearby elements
                parent = link.find_parent('small')
                if parent:
                    # Find the span with the number
                    number_span = parent.find('span')
                    if number_span:
                        pokedex_number = number_span.get_text(strip=True)
                        # Also look for Japanese name in the same area
                        japanese_span = parent.find_all('span')
                        if len(japanese_span) > 1:
                            japanese_name = japanese_span[1].get_text(strip=True)
                break
        
        # Alternative method: look in the infobox
        if not pokedex_number:
            # Look for the number in roundy elements or specific spans
            infobox = soup.find('table', class_='roundy')
            if infobox:
                # Find all small tags that might contain the number
                for small in infobox.find_all('small'):
                    text = small.get_text()
                    if 'National' in text or 'List of Pokémon' in text:
                        spans = small.find_all('span')
                        if spans:
                            for span in spans:
                                span_text = span.get_text(strip=True)
                                if span_text.startswith('#') or span_text.isdigit():
                                    pokedex_number = span_text
                                elif not japanese_name and not span_text.startswith('#'):
                                    # Might be Japanese name
                                    japanese_name = span_text
        
        # If still not found, try another approach
        if not pokedex_number:
            # Look for pattern like "#0127" in the page
            for span in soup.find_all('span'):
                text = span.get_text(strip=True)
                if text.startswith('#0') and len(text) == 5:
                    pokedex_number = text
                    break
        
        # Get Japanese name from the page title or lang-ja spans
        if not japanese_name:
            ja_spans = soup.find_all('span', lang='ja')
            if ja_spans:
                japanese_name = ja_spans[0].get_text(strip=True)
        
        return {
            'name': display_name,
            'url': url,
            'title': title,
            'japanese': japanese_name or '',
            'pokedex_number': pokedex_number or ''
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {pokemon_name}: {e}", file=sys.stderr)
        return None


def format_output(data):
    """
    Format the Pokemon data according to the specification.
    
    Args:
        data: Dictionary with Pokemon information
        
    Returns:
        Formatted string
    """
    if not data:
        return None
    
    # Format: "Name: Title | Japanese (Pokedex #number)"
    final = f"{data['name']}: {data['title']} | {data['japanese']} (Pokedex {data['pokedex_number']})"
    
    output = f"{data['name']}\n"
    output += f"URL: {data['url']}\n"
    output += f"Final: {final}\n"
    
    return output


def process_input_file(input_file, output_file):
    """
    Process the input file and write results to output file.
    
    Args:
        input_file: Path to input file with Pokemon names
        output_file: Path to output file
    """
    try:
        with open(input_file, 'r') as f:
            pokemon_names = [line.strip() for line in f if line.strip()]
        
        results = []
        
        for i, pokemon_name in enumerate(pokemon_names, 1):
            print(f"Processing {i}/{len(pokemon_names)}: {pokemon_name}...")
            
            data = fetch_pokemon_data(pokemon_name)
            if data:
                formatted = format_output(data)
                if formatted:
                    results.append(formatted)
                    print(f"  ✓ Success: {data['title']}")
                else:
                    print(f"  ✗ Failed to format data")
            else:
                print(f"  ✗ Failed to fetch data")
            
            # Be polite to the server - add a small delay between requests
            if i < len(pokemon_names):
                time.sleep(1)
        
        # Write results to output file
        with open(output_file, 'w') as f:
            for result in results:
                f.write(result)
                f.write('\n')
        
        print(f"\n✓ Successfully processed {len(results)}/{len(pokemon_names)} Pokemon")
        print(f"✓ Results written to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python pokedex_scraper.py <input_file> [output_file]")
        print("\nExample:")
        print("  python pokedex_scraper.py pokedex_1129_input processed_output.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'processed_output.md'
    
    print(f"Pokemon Bulbapedia Scraper")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    process_input_file(input_file, output_file)


if __name__ == '__main__':
    main()
