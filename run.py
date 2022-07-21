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



def next_business_day( date ):
    ''' Return the next weekday
    '''
    # https://stackoverflow.com/questions/9187215/
    return date + [1, 1, 1, 1, 3, 2, 1][date.weekday()]


def new_triage_event( date, attendees, location ):
    names = attendees.keys()
    emails = attendees.values()
    px.new_all_day_event(
        date = date, 
        subject = f"Triage: {','.join(names)}"
        attendees = emails,
        location = location,
        categories = [ 'TicketMaster' ],
        free = True,
    )
    triage_event.save(send_meeting_invitations=exchangelib.items.SEND_TO_ALL_AND_SAVE_COPY)
    )
    # self.make_or_update_shift_change_event( date=date, attendees=attendees, location=location )
    # next_day = self.next_business_day( date=date )
    # self.make_or_update_shift_change_event( date=next_date, attendees=attendees, location=location )


def make_or_update_shift_change_event( self, date, attendees, location ):
    emails = attendees.values()
    existing_event = self.get_shift_change_mtg( date )
    if existing_event:


def run( args ):
    pprint.pprint( ['ARGS', args] )

    # pyexch login
    px = pyexch.pyexch.PyExch()

    # # pyexch read test
    # start = datetime.datetime.now() - datetime.timedelta( days=args.days )
    # events = px.get_events_filtered( start=start )
    # pprint.pprint( events )

    # pyexch write test
    date = datetime.date( 2022, 6, 27 )
    attendees = { 'Loftus': 'aloftus@illinois.edu' }
    location='https://illinois.zoom.us/j/87390897249?pwd=JZ8_SzMfvWmFMJp2hSizNx2vxQm4ZC.1'
    new_triage_event( date=date, attendees=attendees, location=location )
    # SAMPLE EVENT
    # SimpleEvent(
    #   start=EWSDateTime(2022, 7, 11, 0, 0, tzinfo=EWSTimeZone(key='America/Chicago')),
    #   end=EWSDateTime(2022, 7, 11, 23, 59, 59, tzinfo=EWSTimeZone(key='America/Chicago')),
    #   elapsed=datetime.timedelta(seconds=86399),
    #   is_all_day=True,
    #   type='TRIAGE',
    #   location='https://illinois.zoom.us/j/87390897249?pwd=JZ8_SzMfvWmFMJp2hSizNx2vxQm4ZC.1',
    #   subject='Triage: Rundall, Bouvet'
    #   )


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

