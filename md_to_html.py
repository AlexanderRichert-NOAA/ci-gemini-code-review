#!/usr/bin/env python3

import markdown
import sys

file_name = sys.argv[1]
output_name = sys.argv[2]

with open(file_name, "r") as file:
  md_review = file.read()

html_review = markdown.markdown(md_review)

with open(output_name, "w") as output_file:
  output_file.write(html_review)
