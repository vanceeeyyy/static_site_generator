import unittest

from extraction import extract_markdown_images, extract_markdown_links
from splitnodes import split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import (TextNode, 
    text_type_text, 
    text_type_bold,
    text_type_italic,
    text_type_code,
    text_type_image,
    text_type_link,
    text_node_to_html_node
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", text_type_text)
        node2 = TextNode("This is a text node", text_type_text)
        self.assertEqual(node, node2)

    def test_eq_false(self):
        node = TextNode("This is a text node", text_type_text)
        node2 = TextNode("This is a text node", text_type_bold)
        self.assertNotEqual(node, node2)

    def test_eq_false2(self):
        node = TextNode("This is a text node", text_type_text)
        node2 = TextNode("This is a text node2", text_type_text)
        self.assertNotEqual(node, node2)

    def test_eq_url(self):
        node = TextNode("This is a text node", text_type_italic, "https://www.boot.dev")
        node2 = TextNode(
            "This is a text node", text_type_italic, "https://www.boot.dev"
        )
        self.assertEqual(node, node2)

    def test_repr(self):
        node = TextNode("This is a text node", text_type_text, "https://www.boot.dev")
        self.assertEqual(
            "TextNode(This is a text node, text, https://www.boot.dev)", repr(node)
        )

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", text_type_text)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is an image", text_type_image, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev", "alt": "This is an image"},
        )

    def test_bold(self):
        node = TextNode("This is bold", text_type_bold)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold")

    def test_split_code(self):
        node = TextNode("This is text with a `code block` word", text_type_text)
        result = split_nodes_delimiter([node], "`", text_type_code)
        expected = [
            TextNode("This is text with a ", text_type_text),
            TextNode("code block", text_type_code),
            TextNode(" word", text_type_text),
        ]
        self.assertEqual(result, expected)
    
    def test_split_bold(self):
        node = TextNode("This is text with **bold text** in it", text_type_text)
        result = split_nodes_delimiter([node], "**", text_type_bold)
        expected = [
            TextNode("This is text with ", text_type_text),
            TextNode("bold text", text_type_bold),
            TextNode(" in it", text_type_text),
        ]
        self.assertEqual(result, expected)
    
    def test_split_italic(self):
        node = TextNode("Here is some *italic text* for testing", text_type_text)
        result = split_nodes_delimiter([node], "*", text_type_italic)
        expected = [
            TextNode("Here is some ", text_type_text),
            TextNode("italic text", text_type_italic),
            TextNode(" for testing", text_type_text),
        ]
        self.assertEqual(result, expected)
    
    def test_unmatched_delimiter(self):
        node = TextNode("This has an unmatched `delimiter", text_type_text)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", text_type_code)
    
    def test_no_delimiter(self):
        node = TextNode("No delimiter here", text_type_text)
        result = split_nodes_delimiter([node], "`", text_type_code)
        expected = [node]
        self.assertEqual(result, expected)
    
    def test_multiple_delimiters(self):
        node = TextNode("Text with `inline code` and **bold** text", text_type_text)
        result = split_nodes_delimiter([node], "`", text_type_code)
        result = split_nodes_delimiter(result, "**", text_type_bold)
        expected = [
            TextNode("Text with ", text_type_text),
            TextNode("inline code", text_type_code),
            TextNode(" and ", text_type_text),
            TextNode("bold", text_type_bold),
            TextNode(" text", text_type_text),
        ]
        self.assertEqual(result, expected)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev)"
        )
        self.assertListEqual(
            [
                ("link", "https://boot.dev"),
                ("another link", "https://blog.boot.dev"),
            ],
            matches,
        )

    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with an image ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
            "text"
        )
        result = split_nodes_image([node])
        expected = [
            TextNode("This is text with an image ", "text"),
            TextNode("rick roll", "image", "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" and ", "text"),
            TextNode("obi wan", "image", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]
        self.assertEqual(result, expected)
    
    def test_split_nodes_link(self):
        node = TextNode(
            "Here is a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            "text"
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("Here is a link ", "text"),
            TextNode("to boot dev", "link", "https://www.boot.dev"),
            TextNode(" and ", "text"),
            TextNode("to youtube", "link", "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_image_no_images(self):
        node = TextNode(
            "No images here, just text.",
            "text"
        )
        result = split_nodes_image([node])
        expected = [node]
        self.assertEqual(result, expected)
    
    def test_split_nodes_link_no_links(self):
        node = TextNode(
            "No links here, just text.",
            "text"
        )
        result = split_nodes_link([node])
        expected = [node]
        self.assertEqual(result, expected)
    
    def test_split_nodes_image_multiple_images(self):
        node = TextNode(
            "Multiple images: ![img1](url1) and ![img2](url2).",
            "text"
        )
        result = split_nodes_image([node])
        expected = [
            TextNode("Multiple images: ", "text"),
            TextNode("img1", "image", "url1"),
            TextNode(" and ", "text"),
            TextNode("img2", "image", "url2"),
            TextNode(".", "text"),
        ]
        self.assertEqual(result, expected)
    
    def test_split_nodes_link_multiple_links(self):
        node = TextNode(
            "Multiple links: [link1](url1) and [link2](url2).",
            "text"
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("Multiple links: ", "text"),
            TextNode("link1", "link", "url1"),
            TextNode(" and ", "text"),
            TextNode("link2", "link", "url2"),
            TextNode(".", "text"),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes(self):
        nodes = text_to_textnodes(
            "This is **text** with an *italic* word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", text_type_text),
                TextNode("text", text_type_bold),
                TextNode(" with an ", text_type_text),
                TextNode("italic", text_type_italic),
                TextNode(" word and a ", text_type_text),
                TextNode("code block", text_type_code),
                TextNode(" and an ", text_type_text),
                TextNode("image", text_type_image, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", text_type_text),
                TextNode("link", text_type_link, "https://boot.dev"),
            ],
            nodes,
        )

if __name__ == "__main__":
    unittest.main()
