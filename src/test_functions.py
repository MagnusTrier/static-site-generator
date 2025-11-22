import unittest

from textnode import TextNode, TextType
from functions import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image

class TestFunctions(unittest.TestCase):
    def test_convert_text_to_html(self):
        node = TextNode('This is a text node', TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, 'This is a text node')

    def test_convert_bold_to_html(self):
        node = TextNode('this is a bold node', TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, 'b')
        self.assertEqual(html_node.to_html(), '<b>this is a bold node</b>')

    def test_convert_link_to_html(self):
        node = TextNode('this is a link', TextType.LINK, 'https://www.google.com')
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.to_html(), '<a>this is a link</a>')
        self.assertEqual(html_node.props_to_html(), ' href="https://www.google.com"')

    def test_convert_image_to_html(self):
        node = TextNode('my alt text', TextType.IMAGE, 'src/local/image.png')
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.to_html(), '<img></img>')
        self.assertEqual(html_node.props_to_html(), ' src="src/local/image.png" alt="my alt text"')

    def test_split_nodes_delimiter(self):
        node = TextNode('**bold** word', TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '**', TextType.BOLD)
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)

    def test_split_nodes_delimiter_multi_pass(self):
        node = TextNode('Hello world _ree_ and **wow**!!!', TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '_', TextType.ITALIC)
        new_nodes = split_nodes_delimiter(new_nodes, '**', TextType.BOLD)

        texts = [n.text for n in new_nodes]
        types = [n.text_type for n in new_nodes]
        
        self.assertEqual(texts, ['Hello world ', 'ree', ' and ', 'wow', '!!!'])
        self.assertEqual(types, [TextType.TEXT, TextType.ITALIC, TextType.TEXT, TextType.BOLD, TextType.TEXT])

    def test_extract_markdown_images(self):
        text = 'This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)'
        result = extract_markdown_images(text)
        print(result)
        self.assertEqual(result, [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        result = extract_markdown_links(text)
        print(result)
        self.assertEqual(result, [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        print(new_nodes)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
        node = TextNode(
            "![second image](https://i.imgur.com/3elNhQu.png) hello world",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        print(new_nodes)
        self.assertListEqual(
            [
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
                TextNode(' hello world', TextType.TEXT)
            ],
            new_nodes,
        )

if __name__ == '__main__':
    unittest.main()
