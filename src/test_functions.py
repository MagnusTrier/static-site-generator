import unittest

from textnode import TextNode, TextType
from functions import BlockType, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html

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
        self.assertEqual(result, [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
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
        self.assertListEqual(
            [
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
                TextNode(' hello world', TextType.TEXT)
            ],
            new_nodes,
        )

    def test_split_link(self):
        node = TextNode(
            'this is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)',
            TextType.TEXT
        )

        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode('this is text with a link ', TextType.TEXT),
                TextNode('to boot dev', TextType.LINK, 'https://www.boot.dev'),
                TextNode(' and ', TextType.TEXT),
                TextNode('to youtube', TextType.LINK, 'https://www.youtube.com/@bootdotdev')
            ],
            new_nodes
        )

    def test_split_link_and_image(self):
        node = TextNode(
            'this has both a link [to somewhere](https://www.somewhere.com) and an image ![image](https://i.imgur.com/ree.png)',
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode('this has both a link ', TextType.TEXT),
                TextNode('to somewhere', TextType.LINK, 'https://www.somewhere.com'),
                TextNode(' and an image ![image](https://i.imgur.com/ree.png)', TextType.TEXT)
            ],
            new_nodes
        )

        new_nodes = split_nodes_image(new_nodes)
        self.assertListEqual(
            [
                TextNode('this has both a link ', TextType.TEXT),
                TextNode('to somewhere', TextType.LINK, 'https://www.somewhere.com'),
                TextNode(' and an image ', TextType.TEXT),
                TextNode('image', TextType.IMAGE, 'https://i.imgur.com/ree.png')
            ],
            new_nodes
        )

    def test_text_to_textnodes(self):
        test_string = 'This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)'

        nodes = text_to_textnodes(test_string)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes
        )
        
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""

        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
             [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type(self):
        test = block_to_block_type('### Heading')
        self.assertEqual(test, BlockType.HEADING)

        test = block_to_block_type(' ### Heading')
        self.assertEqual(test, BlockType.PARAGRAPH)

        test = block_to_block_type('``` this is valid code ```')
        self.assertEqual(test, BlockType.CODE)

        test = block_to_block_type('``` this is not``')
        self.assertEqual(test, BlockType.PARAGRAPH)

        test_string = '''
> REEEEEEEE
>re
>rrrrr
        '''
        blocks = markdown_to_blocks(test_string)
        test = block_to_block_type(blocks[0])
        self.assertEqual(test, BlockType.QUOTE)

        test_string = '''
- Valid UL
- Valid UL
        '''

        block = markdown_to_blocks(test_string)[0]
        test = block_to_block_type(block)
        self.assertEqual(test, BlockType.UNORDERED_LIST)

        test_string = '''
1. Valid OL
2. Valid Ol
3. Valid Ol
        '''

        block = markdown_to_blocks(test_string)[0]
        test = block_to_block_type(block)
        self.assertEqual(test, BlockType.ORDERED_LIST)

        test_string = '''
1. invalid OL
2. invalid Ol
2. invalid Ol
        '''

        block = markdown_to_blocks(test_string)[0]
        test = block_to_block_type(block)
        self.assertEqual(test, BlockType.PARAGRAPH)

    def test_markdown_to_html(self):
        md = '''
### This is a heading

## This is **also** _a_ [heading](https://www.ree.com)

# WQu

```
this is text that _should_ remain
the **same** even with inline stuff
```

>Hi
>there
> fellow
>coder

- Hi there
- This is a great list!

1. Hello **world**
2. World _ree_
3. `console.log('reee')`

reeee is just my favorite word in the 
whole wide world. I **could** just keep saying it on and on
and on and on
'''
        node = markdown_to_html(md)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
This is text that _should_ remain
the **same** even with inline stuff
    ```
    """

        node = markdown_to_html(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == '__main__':
    unittest.main()
