import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode(props = {'href': 'https://www.google.com'})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com"')

        node2 = HTMLNode(props = {'1': 'this is 1', '2': 'this is 2'})
        self.assertEqual(node2.props_to_html(), ' 1="this is 1" 2="this is 2"')

        node3 = HTMLNode()
        self.assertEqual(node3.props_to_html(), '')

        leaf_node = LeafNode(None, 'hello')
        self.assertEqual(leaf_node.to_html(), 'hello')

        leaf_node2 = LeafNode('p', 'do we even use <p> things?')
        self.assertEqual(leaf_node2.to_html(), '<p>do we even use <p> things?</p>')

    def test_to_html_with_children(self):
        child_node = LeafNode('span', 'child')
        parent_node = ParentNode('div', [child_node])
        self.assertEqual(parent_node.to_html(), '<div><span>child</span></div>')

    def test_to_html_with_multiple_children(self):
        parent_node = ParentNode(
            'div',
            [
                LeafNode('img', 'i am an img'),
                LeafNode('span', 'child 2'),
                LeafNode('p', 'i am useless :(')
            ]
        )
        self.assertEqual(parent_node.to_html(), '<div><img>i am an img</img><span>child 2</span><p>i am useless :(</p></div>')

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode('b', 'grandchild')
        child_node = ParentNode('span', [grandchild_node])
        parent_node = ParentNode('div', [child_node])
        self.assertEqual(
            parent_node.to_html(),
            '<div><span><b>grandchild</b></span></div>'
        )



if __name__ == '__main__':
    unittest.main()
