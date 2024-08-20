import re

def extract_markdown_images(text):
    # Regular expression to match Markdown images
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    # Find all matches in the text
    matches = re.findall(image_pattern, text)
    # Return as a list of tuples
    return matches

def extract_markdown_links(text):
    # Regular expression to match Markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    # Find all matches in the text
    matches = re.findall(link_pattern, text)
    # Return as a list of tuples
    return matches