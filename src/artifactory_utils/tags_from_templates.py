#!/usr/bin/env python3

# Copyright Dansk Bibliotekscenter a/s. Licensed under GPLv3
# See license text at https://opensource.dbc.dk/licenses/gpl-3.0

import argparse
import fnmatch
import getpass
import os
import re
import sys

from . import base_args
from . import docker_tags_lister

json_image_key_re = re.compile("[\"\']image[\"\']:\s*[\"\']([^\"\']+)[\"\']")
yaml_image_key_re = re.compile("image:\s*(.+)")

class NoImageFoundException(Exception):
    pass

class NoTagVariableFoundException(Exception):
    pass

def setup_args():
    parser = base_args.setup_args()
    parser.add_argument("path", help="path to template file or directory "
        "of template files from which to get image tags",
        action=base_args.PathArg, nargs="+")
    parser.add_argument("-o", "--output", help="file to write output to",
        type=argparse.FileType("a"), default=sys.stdout)
    parser.add_argument("--exclude", help="pattern for files to exclude, "
        "accepts * and ? as wildcards")
    parser.add_argument("--include", help="pattern for files to include, "
        "accepts * and ? as wildcards")
    return parser.parse_args()

def get_image_from_file(path):
    with open(path) as fp:
        content = fp.read()
        image = json_image_key_re.search(content)
        if image is not None:
            return image.groups()[0]
        image = yaml_image_key_re.search(content)
        if image is not None:
            return image.groups()[0]
    raise NoImageFoundException("no image found in {}".format(path))

def split_image_name(name):
    image, tag = name.split(":")
    if tag[:2] != "${" or tag[-1] != "}":
        raise NoTagVariableFoundException("no tag variable found in {}"
            .format(name))
    tag = tag.lstrip("${").rstrip("}")
    return image, tag

def get_tag(path, args):
    name = get_image_from_file(path)
    image, variable = split_image_name(name)
    repo_key, image_name = docker_tags_lister.split_repo_name(
        image)
    headers = docker_tags_lister.get_auth_header(args.user, args.password)
    tags = docker_tags_lister.get_tags_list(args.base_url, repo_key,
        image_name, headers)
    tag = docker_tags_lister.get_tag_max(tags, args.tag_prefix)
    return variable, tag

def traverse_directory(path, args):
    tag_dict = {}
    for root, _, files in os.walk(path):
        for filename in files:
            f_path = os.path.join(root, filename)
            if (args.exclude is not None and fnmatch.fnmatch(
                    f_path, args.exclude)) or (args.include
                    is not None and not fnmatch.fnmatch(f_path,
                    args.include)):
                continue
            try:
                variable, tag = get_tag(f_path, args)
                if variable not in tag_dict:
                    tag_dict[variable] = tag
            except (docker_tags_lister.TagsListerException,
                    NoImageFoundException, NoTagVariableFoundException) as e:
                print(e, file=sys.stderr)
    for variable, tag in tag_dict.items():
        args.output.write("{}={}\n".format(variable, tag))

def main():
    args = setup_args()
    if args.password is None:
        args.password = getpass.getpass("password: ")
    for path in args.path:
        if os.path.isdir(path):
            traverse_directory(path, args)
        elif os.path.isfile(path):
            try:
                variable, tag = get_tag(path, args)
                args.output.write("{}={}\n".format(variable, tag))
            except (docker_tags_lister.TagsListerException,
                    NoImageFoundException, NoTagVariableFoundException) as e:
                print(e, file=sys.stderr)
        else:
            print("unknown type of file {}".format(path), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
