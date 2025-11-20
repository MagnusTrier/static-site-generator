import unittest

from textnode import TextNode, TextType
from functions import text_node_to_html_node

class TestFunctions(unittest.TestCase):
    def test_convert_text_to_html(self):
        node = TextNode('This is a text node', TextType.TEXT)
        html_node = text_node_to_html_node(node)
        print(html_node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, 'This is a text node')

    def test_convert_bold_to_html(self):
        node = TextNode('this is a bold node', TextType.BOLD)
        html_node = text_node_to_html_node(node)
        print(html_node)
        self.assertEqual(html_node.tag, 'b')
        self.assertEqual(html_node.to_html(), '<b>this is a bold node</b>')

    def test_convert_link_to_html(self):
        node = TextNode('this is a link', TextType.LINK, 'https://www.google.com')
        html_node = text_node_to_html_node(node)
        print(html_node)
        self.assertEqual(html_node.to_html(), '<a>this is a link</a>')
        self.assertEqual(html_node.props_to_html(), ' href="https://www.google.com"')

    def test_convert_image_to_html(self):
        node = TextNode('my alt text', TextType.IMAGE, 'src/local/image.png')
        html_node = text_node_to_html_node(node)
        print(html_node)
        self.assertEqual(html_node.to_html(), '<img></img>')
        self.assertEqual(html_node.props_to_html(), ' src="src/local/image.png" alt="my alt text"')

if __name__ == '__main__':
    unittest.main()
