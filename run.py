#!/bin/env python3

import argparse
import csv
import datetime
import dateutil.parser
import logging
import netrc
import os
import pprint
import pyexch.pyexch

def process_args():
    constructor_args = {
        'formatter_class': argparse.RawDescriptionHelpFormatter,
        'description': 'triage duty scheduler',
        'epilog': '''
Program is controlled using the following environment variables:
    NETRC
        path to netrc file (default: ~/.netrc)
        where netrc file has a key named "EXCH"
        and the "EXCH" key has values for:
        "login" in format username@illinois.edu
        "password",
        "account" in format username@illinois.edu
        NOTE that account can be different than login,
        which is how to access a shared calendar.
'''
    }
    parser = argparse.ArgumentParser()
    parser.add_argument( '-d', '--debug', action='store_true' )
    parser.add_argument( '-f', '--infile', type=argparse.FileType() )
    # parser.add_argument( '-k', '--netrckey',
    #     help='key in netrc to use for login,passwd; default=%(default)s' )
    defaults = {
        'debug': False,
        'infile': '-',
    }
    parser.set_defaults( **defaults )
    args = parser.parse_args()
    # # Load login and passwd from netrc
    # netrc_fn = os.getenv( 'NETRC' )
    # nrc = netrc.netrc( netrc_fn )
    # nrc_parts = nrc.authenticators( args.netrckey )
    # if nrc_parts:
    #     args.user = nrc_parts[0]
    #     args.passwd = nrc_parts[2]
    # if not args.user:
    #     raise UserWarning( 'Empty username not allowed' )
    # if not args.passwd:
    #     raise UserWarning( 'Empty passwd not allowed' )
    return args


def get_existing_events( px, start, end ):
    ''' px = PyExch instance, already logged in
        start = datetime.date OR datetime.datetime
        end = datetime.date OR datetime.datetime
        Get existing events between "start" and "end"
    '''
    # convert end to a datetime at the end of the day 11:59:59 PM
    existing_events = px.get_events_filtered(
        start = start,
        end = end + datetime.timedelta( seconds=86399 ),
    )
    # pprint.pprint( existing_events )
    # pprint.pprint( [ (e.start, e.type, e.subject) for e in existing_events ] )
    # create hash of event dates & types
    current_events = {}
    for e in existing_events:
        dt = datetime.date( e.start.year, e.start.month, e.start.day )
        if dt not in current_events:
            current_events[dt] = {}
        current_events[dt][e.type] = e
    return current_events


def next_business_day( date ):
    ''' Return the next weekday
    '''
    # https://stackoverflow.com/questions/9187215/
    return date + [1, 1, 1, 1, 3, 2, 1][date.weekday()]


def new_triage_event( px, date, attendees, location ):
    names = attendees.keys()
    emails = attendees.values()
    px.new_all_day_event(
        date = date, 
        subject = f"Triage: {','.join(names)}",
        attendees = emails,
        location = location,
        categories = [ 'TicketMaster' ],
        free = True,
    )
    # self.make_or_update_shift_change_event( date=date, attendees=attendees, location=location )
    # next_day = self.next_business_day( date=date )
    # self.make_or_update_shift_change_event( date=next_date, attendees=attendees, location=location )


# def make_or_update_shift_change_event( self, date, attendees, location ):
#     emails = attendees.values()
#     existing_event = self.get_shift_change_mtg( date )
#     if existing_event:


def run( args ):
    pprint.pprint( ['ARGS', args] )

    # get CSV input
    csv_data = csv.reader( args.infile, dialect='excel-tab' )
    triage_raw_data = { dateutil.parser.parse(row[0]):row[1:] for row in csv_data }
    # pprint.pprint( triage_raw_data )

    # get existing events as dict[date][type]
    regex_map = {
        "TRIAGE":"^Triage: ",
        "SHIFTCHANGE":"^Triage Shift Change: ",
        }
    px = pyexch.pyexch.PyExch( regex_map = regex_map )
    existing_events = get_existing_events(
        px,
        start = min( triage_raw_data.keys() ),
        end = max( triage_raw_data.keys() ),
    )

    for dt in sorted( current_events.keys() ):
        for typ, ev in current_events[dt].items():
            subj = ev.subject
            members = [ x.mailbox.email_address for x in ev.raw_event.required_attendees ]
            pprint.pprint( [ dt, typ, subj, members ] )

    # attempt to create triage meetings
    for dt, members in triage_raw_data.items():
        for typ in regex_map.keys():
            existing_event = None
            existing_event = existing_events[dt][typ]

    





    raise SystemExit( 'forced exit' )


    # # pyexch read test
    # start = datetime.datetime.now() - datetime.timedelta( days=args.days )
    # events = px.get_events_filtered( start=start )
    # pprint.pprint( events )

    # pyexch write test
    date = datetime.date( 2022, 6, 27 )
    attendees = { 'Loftus': 'aloftus@illinois.edu' }
    location='https://illinois.zoom.us/j/87390897249?pwd=JZ8_SzMfvWmFMJp2hSizNx2vxQm4ZC.1'
    new_triage_event( px=px, date=date, attendees=attendees, location=location )
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

