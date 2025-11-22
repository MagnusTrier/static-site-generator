import os, shutil
import sys

from functions import markdown_to_html


def copy_item(source_path, item_name, target_path):
    full_source_path = os.path.join(source_path, item_name)
    full_target_path = os.path.join(target_path, item_name)

    if os.path.isfile(full_source_path):
        shutil.copy(full_source_path, full_target_path)
    else:
        if not os.path.exists(full_target_path):
            os.mkdir(full_target_path)

        for item in os.listdir(full_source_path):
            copy_item(full_source_path, item, full_target_path)

def initiate_directory_copy(source_dir, target_dir):
    current = '.'
    full_source_path = os.path.abspath(os.path.join(current, source_dir))
    full_target_path = os.path.abspath(os.path.join(current, target_dir))

    if not os.path.exists(full_source_path):
        raise Exception('Source directory does not exist')

    if os.path.exists(full_target_path):
        shutil.rmtree(full_target_path)

    os.mkdir(target_dir)

    for item in os.listdir(full_source_path):
        copy_item(full_source_path, item, full_target_path)

    print(os.listdir(full_target_path))

def extract_title(markdown):
    lines = markdown.split('\n')
    for l in lines:
        if l.startswith('# '):
            ree = l.replace('#', '')
            ree = ree.strip()
            return ree
    raise Exception('No header was found')

def generate_page(from_path, template_path, dest_path, basepath):
    print(f'Generating page from {from_path} to {dest_path} using {template_path}')

    from_file = open(from_path, 'r')
    md = from_file.read()
    from_file.close()

    template_file = open(template_path)
    template = template_file.read()
    template_file.close()

    title = extract_title(md)
    html_nodes = markdown_to_html(md)
    html = html_nodes.to_html()

    content = template.replace('{{ Title }}', title)
    content = content.replace('{{ Content }}', html)
    content = content.replace('href="/', f'href="{basepath}')
    content = content.replace('src="/', f'src="{basepath}')

    target_file = open(dest_path, 'w')
    target_file.write(content)
    target_file.close()
 
def generate_page_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        destination_path = os.path.join(dest_dir_path, item)
        if os.path.isfile(item_path):
            print(item_path, 'is a file')
            generate_page(item_path, template_path, destination_path.replace('.md', '.html'), basepath)
        else:
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)
            generate_page_recursive(item_path, template_path, destination_path, basepath)



def main():
    print(sys.argv[1])
    initiate_directory_copy('static', 'docs')
    generate_page_recursive(
        './content', 
        'template.html', 
        './docs', 
        f'{sys.argv[1] if sys.argv and sys.argv[1] else '/'}'
    )

if __name__ == '__main__':
    main()

