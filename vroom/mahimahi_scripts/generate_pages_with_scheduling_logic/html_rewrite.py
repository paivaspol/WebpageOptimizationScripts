from bs4 import BeautifulSoup
import subprocess
import sys
import os
# pip install beautifulsoup4 and html5lib

html_file = sys.argv[1]
new_html_file = sys.argv[2]
top_level_url = sys.argv[3]

# read in inline script to add throughput HTML
inline_script = ''
with open('get_urls.js') as f:
    for line in f:
        inline_script += line

small_inline_script = ''
with open('get_unimportant_urls.js') as f:
    for line in f:
        small_inline_script += line

# code to remove itself from html
inline_script += "\n// remove wrappers immediately after defining callbacks/wrappers\nvar t = document.getElementById(\"fetch_unimportant\");\nt.parentNode.removeChild(t);"

temp_file_name = "temp.js"
temp_file_rewrite = "temp_rewrite.js"

soup = BeautifulSoup(open(html_file), "html5lib")

# add top-level url to all HTML tags
for html in soup.find_all('html'):
    html['top_url'] = top_level_url
#    new_script = soup.new_tag('script')
#    new_script.string = inline_script
#    new_script['id'] = "fetch_unimportant"
#    html.first().insert_after(new_script)

# add inline script before each existing script tag
for script in soup.find_all('script'):
    new_script = soup.new_tag('script')
    new_script.string = small_inline_script
    new_script['id'] = "fetch_unimportant"
    script.insert_before(new_script)

new_script = soup.new_tag('script')
new_script.string = inline_script
new_script['id'] = "fetch_unimportant"
soup.find().insert(0,new_script)


file1=open(new_html_file,"w")
file1.write(str(soup))
file1.close()
