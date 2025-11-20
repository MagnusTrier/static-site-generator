from textnode import TextNode, TextType

def main():
    new = TextNode('hello world this is a link!', TextType.LINK, 'https://youtube.com')
    print(new)

if __name__ == '__main__':
    main()

