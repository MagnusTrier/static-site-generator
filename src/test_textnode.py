import unittest

from textnode import TextNode, TextType

class TetsTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode('This is a text node', TextType.BOLD)
        node2 = TextNode('This is a text node', TextType.BOLD)
        self.assertEqual(node, node2)

        node3 = TextNode('This is a text node?', TextType.BOLD)
        self.assertNotEqual(node, node3)

        node4 = TextNode('This is a text node', TextType.IMAGE)
        self.assertNotEqual(node, node4)

        node5 = TextNode('This is a text node', TextType.IMAGE, 'random_url')
        self.assertNotEqual(node4, node5)

if __name__ == '__main__':
    unittest.main()
