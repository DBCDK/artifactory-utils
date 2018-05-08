#!/usr/bin/env python3

# Copyright Dansk Bibliotekscenter a/s. Licensed under GPLv3
# See license text at https://opensource.dbc.dk/licenses/gpl-3.0

import argparse

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url",
        default="https://artifactory.dbc.dk/artifactory")
    parser.add_argument("-u", "--user", required=True)
    parser.add_argument("-p", "--password")
    parser.add_argument("--tag-prefix", default="",
        help="filter docker tags with this prefix")
    return parser
