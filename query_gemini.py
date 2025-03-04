#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(
                    prog='query_gemini.py',
                    description='Query Gemini API')

parser.add_argument("query_filename", type=str, help="Path to file containing query text")
parser.add_argument("output_filename", type=str, help="Path to output file")
apikey_group = parser.add_mutually_exclusive_group(required=True)
apikey_group.add_argument("-k", "--key-variable", help="Name of env variable containing API key")
apikey_group.add_argument("-f", "--key-file", help="Path to file containing API key")

args = parser.parse_args()

import json
import os
import requests

if args.query_filename:
  with open(args.query_filename, "r") as f:
    query_text = f.read()

if args.key_variable:
  api_key = os.getenv(args.key_variable, '')
else:
  with open(args.key_file, "r") as key_file:
    api_key = key_file.read().strip()

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
params = {'key': api_key,}
headers = {'Content-Type': 'application/json',}
json_send = {'contents': [{'parts': [{'text': query_text,},],},],}

response = requests.post(url, params=params, headers=headers, json=json_send)

review = json.loads(response.content.decode())["candidates"][0]["content"]["parts"][0]["text"]

with open(args.output_filename, "w") as output_file:
  output_file.write(review)
