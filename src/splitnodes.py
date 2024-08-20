from extraction import extract_markdown_images, extract_markdown_links
from textnode import TextNode

def text_to_textnodes(text):
    nodes = [TextNode(text, text_type_text)]
    nodes = split_nodes_delimiter(nodes, "**", text_type_bold)
    nodes = split_nodes_delimiter(nodes, "*", text_type_italic)
    nodes = split_nodes_delimiter(nodes, "`", text_type_code)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != "text":
            new_nodes.append(node)
            continue

        segments = node.text.split(delimiter)
        if len(segments) == 1:
            new_nodes.append(node)
            continue

        for i, segment in enumerate(segments):
            if i % 2 == 0:
                new_nodes.append(TextNode(segment, "text"))
            else:
                new_nodes.append(TextNode(segment, text_type))

            if len(segments) % 2 == 0:
                raise ValueError("Invalid syntax: Unmatched delimiter")
            
    return new_nodes

text_type_text = "text"
text_type_code = "code"
text_type_bold = "bold"
text_type_italic = "italic"

def split_nodes_image(old_nodes):
    new_nodes= []

    for node in old_nodes:
        if node.text_type != "text":
            new_nodes.append(node)
            continue

        text = node.text
        images = extract_markdown_images(text)
        if not images:
            new_nodes.append(node)
            continue

        last_pos = 0
        for alt_text, url in images:
            image_markdown = f"![{alt_text}]({url})"
            pos = text.find(image_markdown, last_pos)
            if pos != 1:
                if pos > last_pos:
                    new_nodes.append(TextNode(text[last_pos:pos], "text"))
                new_nodes.append(TextNode(alt_text, "image", url))
                last_pos = pos + len(image_markdown)

        if last_pos < len(text):
            new_nodes.append(TextNode(text[last_pos:], "text"))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != "text":
            new_nodes.append(node)
            continue
        
        text = node.text
        links = extract_markdown_links(text)
        if not links:
            new_nodes.append(node)
            continue
        
        last_pos = 0
        for anchor_text, url in links:
            link_markdown = f"[{anchor_text}]({url})"
            pos = text.find(link_markdown, last_pos)
            if pos != -1:
                if pos > last_pos:
                    new_nodes.append(TextNode(text[last_pos:pos], "text"))
                new_nodes.append(TextNode(anchor_text, "link", url))
                last_pos = pos + len(link_markdown)
        
        if last_pos < len(text):
            new_nodes.append(TextNode(text[last_pos:], "text"))
    
    return new_nodes
