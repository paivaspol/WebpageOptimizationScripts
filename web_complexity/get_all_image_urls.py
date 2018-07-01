from bs4 import BeautifulSoup
from argparse import ArgumentParser

def Main():
    with open(args.html_filename, 'r') as input_file:
        html = input_file.read()
    soup = BeautifulSoup(html, 'html5lib')
    all_imgs = soup.find_all('img')
    for img in all_imgs:
        print(img['src'])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('html_filename')
    args = parser.parse_args()
    Main()
