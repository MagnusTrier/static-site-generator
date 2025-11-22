import re

from htmlnode import LeafNode
from textnode import TextNode, TextType

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag = None, value = text_node.text)
        case TextType.BOLD:
            return LeafNode(tag = 'b', value = text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag = 'i', value = text_node.text)
        case TextType.CODE:
            return LeafNode(tag = 'code', value = text_node.text)
        case TextType.LINK:
            return LeafNode(tag = 'a', value = text_node.text, props = {
                'href': text_node.url
            })
        case TextType.IMAGE:
            return LeafNode(tag = 'img', value = '', props = {
                'src': text_node.url,
                'alt': text_node.text
            })
        case _:
            raise Exception('Invalid TextNode text_type')

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
        else:
            if old_node.text.count(delimiter) % 2 != 0:
                raise Exception(f'Old node has invalid markdown syntax unmatched delimiter: {delimiter}')

            sections = old_node.text.split(delimiter)
            for i, section in enumerate(sections):
                if section == '':
                    continue
                if i % 2 == 0:
                    new_nodes.append(TextNode(section, TextType.TEXT))
                else:
                    new_nodes.append(TextNode(section, text_type))

    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r'!\[([^\[\]]*)\]\(([^\(\)]*)\)', text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r'(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)', text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        matches = extract_markdown_images(old_node.text)
        if old_node.text_type is not TextType.TEXT or len(matches) == 0:
            new_nodes.append(old_node)
        else:
            text = old_node.text

            while len(matches) > 0:
                match = matches.pop(0)
                split_string = text.split(f'![{match[0]}]({match[1]})')
                if split_string[0] != '':
                    new_nodes.append(TextNode(split_string[0], TextType.TEXT))

                new_nodes.append(TextNode(match[0], TextType.IMAGE, match[1]))

                if len(split_string) >= 2:
                    if len(matches) == 0 and split_string[1] != '':
                        new_nodes.append(TextNode(split_string[1], TextType.TEXT))
                    else:
                        text = split_string[1]
     
    return new_nodes


