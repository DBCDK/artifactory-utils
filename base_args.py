#!/usr/bin/env python3

# Copyright Dansk Bibliotekscenter a/s. Licensed under GPLv3
# See license text at https://opensource.dbc.dk/licenses/gpl-3.0

import argparse
import os

class PathArg(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        paths = [values] if self.nargs is None else values
        for path in paths:
            if not os.path.exists(path):
                raise argparse.ArgumentError(self, "not a valid path: {}"
                    .format(path))
        setattr(namespace, self.dest, paths)

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url",
        default="https://artifactory.dbc.dk/artifactory")
    parser.add_argument("-u", "--user", required=True)
    parser.add_argument("-p", "--password")
    parser.add_argument("--tag-prefix", default="",
        help="filter docker tags with this prefix")
    return parser
