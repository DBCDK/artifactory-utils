#!/usr/bin/env python3

# Copyright Dansk Bibliotekscenter a/s. Licensed under GPLv3
# See license text at https://opensource.dbc.dk/licenses/gpl-3.0

import base64
import getpass
import json
import sys
import urllib.request

import base_args

class TagsListerException(Exception):
    pass

def setup_args():
    parser = base_args.setup_args()
    parser.add_argument("repository", help="docker repository and image "
        "name, in the form \"docker-io.dbc.dk/io-react.\"")
    return parser.parse_args()

def open_page(url, headers={}):
    request = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(request)

def get_auth_header(username, password, encoding="utf8"):
    b64_auth = base64.b64encode("{}:{}".format(username, password).encode(
        encoding))
    return {"Authorization": b64_auth}

def get_tags_list(base_url, repo_key, image_name, headers):
    url = "{}/api/docker/{}/v2/{}/tags/list".format(base_url, repo_key,
        image_name)
    tags_page = open_page(url, headers)
    tags_json = json.loads(tags_page.read().decode("utf8"))
    if "tags" not in tags_json:
        raise TagsListerException("key \"tags\" not found in reponse json:\n{}"
            .format(json.dumps(tags_json, indent=4, sort_keys=True)))
    return tags_json["tags"]

def get_tag_max(tags, prefix=""):
    try:
        filtered_tags = [t for t in tags if t.startswith(prefix)]
        m = max(int(t[len(prefix):]) for t in filtered_tags)
        return prefix + str(m)
    except ValueError as e:
        raise TagsListerException("error getting highest tag value from "
            "tags\n{}\nwith prefix \"{}\":\n{}".format(str(tags), prefix, e))

def split_repo_name(repo_name):
    try:
        repository, image_name = repo_name.split("/")
        repo_key = repository.split(".")[0]
        return (repo_key, image_name)
    except ValueError as e:
        raise TagsListerException("error getting repository and image name, "
            "should be of form docker-io.dbc.dk/io-react ({})".format(e))

def main():
    args = setup_args()
    if args.password is None:
        args.password = getpass.getpass("password: ")
    try:
        repo_key, image_name = split_repo_name(args.repository)
        headers = get_auth_header(args.user, args.password)
        tags = get_tags_list(args.base_url, repo_key, image_name, headers)
        print(get_tag_max(tags, args.tag_prefix))
    except TagsListerException as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
