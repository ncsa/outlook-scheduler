#!/bin/env python3

import argparse
import datetime
import logging
import netrc
import os
import pprint
import pyexch.pyexch

def process_args():
    constructor_args = {
        'formatter_class': argparse.RawDescriptionHelpFormatter,
        'description': 'outlook scheduler',
        'epilog': '''
Program is controlled using the following environment variables:
    NETRC
        path to netrc file (default: ~/.netrc)
        where netrc file has keys "EXCH"
        and the "EXCH" key has values for login, password, account
'''
    }
    parser = argparse.ArgumentParser()
    parser.add_argument( '--debug', action='store_true' )
    parser.add_argument( '-d', '--days', type=int )
    parser.add_argument( '-k', '--netrckey',
        help='key in netrc to use for login,passwd; default=%(default)s' )
    defaults = {
        'days': 7,
        'debug': False,
        'netrckey': 'EXCH',
        'passwd': None,
        'user': None,
    }
    parser.set_defaults( **defaults )
    args = parser.parse_args()
    # Load login and passwd from netrc
    netrc_fn = os.getenv( 'NETRC' )
    nrc = netrc.netrc( netrc_fn )
    nrc_parts = nrc.authenticators( args.netrckey )
    if nrc_parts:
        args.user = nrc_parts[0]
        args.passwd = nrc_parts[2]
    if not args.user:
        raise UserWarning( 'Empty username not allowed' )
    if not args.passwd:
        raise UserWarning( 'Empty passwd not allowed' )
    return args


def run( args ):
    pprint.pprint( ['ARGS', args] )

    # pyexch login
    px = pyexch.pyexch.PyExch()

    # pyexch read test
    start = datetime.datetime.now() - datetime.timedelta( days=args.days )
    events = px.get_events_filtered( start=start )
    pprint.pprint( events )

    # pyexch write test


if __name__ == '__main__':
    log_lvl = logging.INFO
    args = process_args()
    if args.debug:
        log_lvl = logging.DEBUG
    fmt = '%(levelname)s %(message)s'
    if log_lvl == logging.DEBUG:
        fmt = '%(levelname)s [%(filename)s:%(funcName)s:%(lineno)s] %(message)s'
    logging.basicConfig( level=log_lvl, format=fmt )
    no_debug = [
        'exchangelib',
    ]
    for key in no_debug:
        logging.getLogger(key).setLevel(logging.CRITICAL)
    run( args )
