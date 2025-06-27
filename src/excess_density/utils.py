import json
import re


def parse_jsonc(jsonc_str):
    # Remove single-line comments (//)
    jsonc_str = re.sub(r"//.*", "", jsonc_str)
    # Remove multi-line comments (/* */)
    jsonc_str = re.sub(r"/\*.*?\*/", "", jsonc_str, flags=re.DOTALL)
    return json.loads(jsonc_str)
