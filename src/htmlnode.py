class HTMLNode:
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is None:
            return ''

        html = ''
        for key, val in self.props.items():
            s = f' {key}="{val}"'
            html += s
        return html
    
    def __repr__(self):
        return f'HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})'

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props = None):
        super().__init__(tag = tag, value = value, props = props)

    def to_html(self):
        if self.value is None:
            raise ValueError('Leaf node has no value!')
        if self.tag is None:
            return self.value
        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = None):
        super().__init__(tag = tag, children = children, props = props)

    def to_html(self):
        if self.tag is None:
            raise ValueError('Parent node has no tag!')
        if self.children is None:
            raise ValueError('Parent has no children!')

        html = ''
        for child in self.children:
            html += child.to_html()

        return f'<{self.tag}>{html}</{self.tag}>'

