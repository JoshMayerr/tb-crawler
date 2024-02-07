import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote


def fetch_and_save_html(url, folder_path):
    """Fetch HTML content for a URL and save it to a specified folder."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx, 5xx
        # Simplify filename generation from the URL
        file_name = url.split('/')[-1] or "index.html"
        # Append '.html' if the file name doesn't end with it
        if not file_name.endswith('.html'):
            file_name += '.html'
        file_path = os.path.join(folder_path, file_name)

        # Conver the full html page into prettier HTML with important content only
        stripped_content = parse_raw_html(response.text)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(stripped_content)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")


def ensure_directory(path):
    """Ensure that a directory exists; if it doesn't, create it."""
    if not os.path.exists(path):
        os.makedirs(path)


def parse_raw_html(html_content):
    """
    Extracts text content from the <main> tag of an HTML page, including children tags with text.

    :param html_content: HTML content of the entire webpage as a string.
    :return: A string containing the HTML of children tags within <main> that have text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find('main')

    if not main_content:
        return "The <main> tag could not be found in the HTML content."

    tags_to_remove = ['script', 'style', 'img', 'form', 'svg']

    remove_tags_from_list(main_content, tags_to_remove)

    return str(main_content)


def remove_tags_from_list(soup, tag_names):
    """
    Recursively remove all tags from a hardcoded list of tag names from a BeautifulSoup object.

    :param soup: The BeautifulSoup object to modify.
    :param tag_names: A list of tag names to remove (e.g., ['script', 'style']).
    """
    for tag_name in tag_names:
        for tag in soup.find_all(tag_name):
            tag.decompose()


def process_sitemap(url, folder_path):
    """Process a sitemap, handling nested sitemaps."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='lxml')

    # Check for sitemap index file indicating nested sitemaps
    if soup.find_all('sitemap'):
        # This is a sitemap index file, process each nested sitemap
        sitemaps = soup.find_all('loc')
        for sitemap in sitemaps:
            process_sitemap(sitemap.text, folder_path)
    else:
        # This is a regular sitemap, fetch and save each page URL
        urls = soup.find_all('loc')
        for url in urls:
            print(f"Fetching: {url.text}")
            fetch_and_save_html(url.text, folder_path)


def fetch_from_sitemap(sitemap_url, folder_path):
    """Fetch pages from a sitemap URL, including nested sitemaps."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        os.rmdir(folder_path)
        os.makedirs(folder_path)
    process_sitemap(sitemap_url, folder_path)


# Example usage
# Example sitemap URL, replace as needed
sitemap_url = 'https://www.vox.com/sitemaps.xml'
output_folder = 'vox_crawled'  # Folder where HTML files will be saved

fetch_from_sitemap(sitemap_url, output_folder)


# file_path = 'testfile.html'

# # Open the file in read mode ('r') and specify the encoding
# with open(file_path, 'r', encoding='utf-8') as file:
#     html_page = file.read()

# # Now, html_content contains the HTML file's content as a string
# text = parse_raw_html(html_page)
# print(text)
