import re
from enum import Enum


from htmlnode import LeafNode, ParentNode
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

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        matches = extract_markdown_links(old_node.text)
        if old_node.text_type is not TextType.TEXT or len(matches) == 0:
            new_nodes.append(old_node)
        else:
            text = old_node.text

            while len(matches) > 0:
                match = matches.pop(0)
                split_string = text.split(f'[{match[0]}]({match[1]})')
                if split_string[0] != '':
                    new_nodes.append(TextNode(split_string[0], TextType.TEXT))

                new_nodes.append(TextNode(match[0], TextType.LINK, match[1]))

                if len(split_string) >= 2:
                    if len(matches) == 0 and split_string[1] != '':
                        new_nodes.append(TextNode(split_string[1], TextType.TEXT))
                    else:
                        text = split_string[1]
     
    return new_nodes

def text_to_textnodes(text):
    new_nodes = [TextNode(text, TextType.TEXT)]

    # process bold
    new_nodes = split_nodes_delimiter(new_nodes, '**', TextType.BOLD)

    # process italic
    new_nodes = split_nodes_delimiter(new_nodes, '_', TextType.ITALIC)

    # process code
    new_nodes = split_nodes_delimiter(new_nodes, '`', TextType.CODE)

    # process link
    new_nodes = split_nodes_link(new_nodes)

    # process image
    new_nodes = split_nodes_image(new_nodes)

    return new_nodes

def markdown_to_blocks(markdown):
    raw = markdown.split('\n\n')
    blocks = []
    for b in raw:
        stripped = b.strip()
        if stripped != '':
            blocks.append(stripped)
    return blocks

class BlockType(Enum):
    PARAGRAPH = 'paragraph'
    HEADING = 'heading'
    CODE = 'code'
    QUOTE = 'quote'
    UNORDERED_LIST = 'unordered_list'
    ORDERED_LIST = 'ordered_list'

def block_to_block_type(block):
    if re.match('^#+? .', block) is not None:
        return BlockType.HEADING
    if block.startswith('```') and block.endswith('```'):
        return BlockType.CODE
    
    lines = block.split('\n')
    isQuote = [re.match('^>', l) is not None for l in lines]
    if len(lines) == sum(isQuote):
        return BlockType.QUOTE

    isUL = [re.match('^- ', l) is not None for l in lines]
    if len(lines) == sum(isUL):
        return BlockType.UNORDERED_LIST

    isOL = [re.match(r'^\d. ', l) is not None for l in lines]
    if len(lines) == sum(isOL):
        num = 0
        for l in lines:
            if int(l[0]) == num + 1:
                num += 1
                continue
            else:
                return BlockType.PARAGRAPH
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)

    children = []
    for node in text_nodes:
        children.append(text_node_to_html_node(node))

    return children

def markdown_to_html(markdown):
    blocks = markdown_to_blocks(markdown)
    
    new_nodes = []

    for block in blocks:
        match block_to_block_type(block):
            case BlockType.PARAGRAPH:
                children = text_to_children(block.replace('\n', ' '))
                new_nodes.append(
                    ParentNode(
                        'p',
                        children
                    )
                )
            case BlockType.HEADING:
                count = block.count('#')
                new_string = block.strip(r'^#+? ')

                children = text_to_children(new_string)
                parent = ParentNode(f'h{count}', children)
                new_nodes.append(parent)

            case BlockType.CODE:
                lines = block.split('\n')
                inner_lines = lines[1:-1]
                new = '\n'.join(inner_lines) + '\n'
                new_nodes.append(
                    ParentNode( 'pre', [ LeafNode( 'code', new) ])
                )

            case BlockType.QUOTE:
                lines = block.split('\n')
                block_children = []

                for l in lines:
                    new_string = l.strip('>')
                    new_string = new_string.strip()
                    children = text_to_children(new_string)
                    block_children.extend(children)

                block_parent = ParentNode('blockquote', block_children)
                new_nodes.append(block_parent)

            case BlockType.UNORDERED_LIST:
                lines = block.split('\n')
                block_children = []

                for l in lines:
                    new_string = l.strip('- ')
                    children = text_to_children(new_string)
                    parent = ParentNode('li', children)
                    block_children.append(parent)

                block_parent = ParentNode('ul', block_children)
                new_nodes.append(block_parent)

            case BlockType.ORDERED_LIST:
                lines = block.split('\n')
                block_children = []

                for l in lines:
                    new_string = l[3:]
                    children = text_to_children(new_string)
                    parent = ParentNode('li', children)
                    block_children.append(parent)

                block_parent = ParentNode('ol', block_children)
                new_nodes.append(block_parent)

            case _:
                raise Exception('Something went wrong when determining block_type')
    return ParentNode('div', new_nodes)
