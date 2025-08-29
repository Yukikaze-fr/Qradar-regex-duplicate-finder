import argparse
import json
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from itertools import groupby
from typing import Iterator


def find_node(func) -> Iterator[dict]:
    def ret(name, path, *args, **kwargs):
        root = ET.parse(path).getroot()
        for child in root.findall(name):
            yield func(child)
        
    return ret


@find_node
def take_regexes(node: Element):
    return {'ap_id': node.find('ap_id').text,
            'regex': node.find('regex').text,
            'username': node.find('username').text}


@find_node
def take_property(node: Element):
    return {'id': node.find('id').text,
            'name': node.find('propertyname').text,
            'username': node.find('username').text}


def final_output(file):
    keyfunc = lambda x: x.get('regex')
    properties = list(take_property('ariel_regex_property', file))
    unhonest = {
        k: group 
        for k, g 
        in groupby(sorted(take_regexes('ariel_property_expression', file), key=keyfunc), keyfunc) 
        if len(group:=list(g))>1
    }
    for v in unhonest.values():
        for d in v:
            d.update({
                "ap": [p.get("name") for p in properties if p.get("id") == d.get("ap_id")][0]
            })
    return [
        {k: list(set(item.get("ap") for item in group))} 
        for k, group in unhonest.items() 
        if len(set(item.get("ap") for item in group)) > 1
    ]

def main():
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='It does nothing useful actually',
        epilog='Try reading the help!!!',
        add_help=False
    )
    parser.add_argument("filenames", nargs="+", help="One or more XML files")
    args = parser.parse_args()

    for file in args.filenames:
        print(f"Processing {file}...")
        print(json.dumps(final_output(file), indent=4))

main()

