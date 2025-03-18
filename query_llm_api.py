#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(
                    prog='query_gemini.py',
                    description='Query various LLM APIs')

parser.add_argument("query_filename", type=str, help="Path to file containing query text")
parser.add_argument("output_filename", type=str, help="Path to output file")
parser.add_argument("--backend", choices=("gemini-2.0", "mistral", "gh-gpt-4o", "gh-phi-4"), default="gemini-2.0", help="LLM to use")
apikey_group = parser.add_mutually_exclusive_group(required=True)
apikey_group.add_argument("-k", "--key-variable", help="Name of env variable containing API key")
apikey_group.add_argument("-f", "--key-file", help="Path to file containing API key")

args = parser.parse_args()

import json
import os
import re
import requests

if args.query_filename:
  with open(args.query_filename, "r") as f:
    query_text = f.read()

if args.key_variable:
  api_key = os.getenv(args.key_variable, '')
else:
  with open(args.key_file, "r") as key_file:
    api_key = key_file.read().strip()

assert len(api_key)>1, "ERROR: Zero-length API key detected"

if args.backend=="gemini-2.0":
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
  params = {'key': api_key,}
  headers = {'Content-Type': 'application/json',}
  json_send = {'contents': [{'parts': [{'text': query_text,},],},],}
  response = requests.post(url, params=params, headers=headers, json=json_send)
  assert response.status_code==200, f"ERROR: Request failed (status code not 200; was {response.status_code})"
  review = json.loads(response.content.decode())["candidates"][0]["content"]["parts"][0]["text"]
elif args.backend=="mistral":
  url = "https://api.mistral.ai/v1/chat/completions"
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {api_key}',
  }
  json_send = {"model": "mistral-large-latest", "messages": [{"role": "user", "content": query_text}]}
  response = requests.post(url, headers=headers, json=json_send)
  assert response.status_code==200, f"ERROR: Request failed (status code not 200; was {response.status_code})"
  review = json.loads(response.content.decode())["choices"][0]["message"]["content"]
elif args.backend.startswith("gh"):
  url = "https://models.inference.ai.azure.com/chat/completions"
  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
  }
  json_send = {
    "messages": [
      {
        "role": "user",
        "content": query_text,
      }
    ],
    "model": re.sub("^gh-", "", args.backend),
  }
  response = requests.post(url, headers=headers, json=json_send)
  assert response.status_code==200, f"ERROR: Request failed (status code not 200; was {response.status_code})"
  review = json.loads(response.content.decode())["choices"][0]["message"]["content"]

with open(args.output_filename, "w") as output_file:
  output_file.write(review)
