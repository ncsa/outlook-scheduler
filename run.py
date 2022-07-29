#!/bin/env python3

# Configure logging
import argparse
import csv
import datetime
import dateutil.parser
import logging
import netrc
import os
import pprint
import pyexch.pyexch

# Hash to hold module level data
resources = {}

def get_args():
    if 'args' not in resources:
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
        resources['args'] = args
    return resources['args']


def get_regex_map():
    return {
        "TRIAGE":"^Triage: ",
        "SHIFTCHANGE":"^Triage Shift Change: ",
        }


def get_pyexch():
    if 'pyexch' not in resources:
        regex_map = get_regex_map()
        resources['pyexch'] = pyexch.pyexch.PyExch( regex_map = regex_map )
    return resources['pyexch']


def get_triage_location():
    if 'triage_location' not in resources:
        resources['triage_location'] = 'https://illinois.zoom.us/j/87390897249?pwd=JZ8_SzMfvWmFMJp2hSizNx2vxQm4ZC.1'
    return resources['triage_location']


def get_triage_categories():
    if 'triage_categories' not in resources:
        resources['triage_categories'] = [ 'TicketMaster' ]
    return resources['triage_categories']


def get_existing_events( start, end ):
    ''' px = PyExch instance, already logged in
        start = datetime.date OR datetime.datetime
        end = datetime.date OR datetime.datetime
        Get existing events between "start" and "end"
    '''
    px = get_pyexch()
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


def create_or_update_triage_event( date, attendees, existing_event:None):
    ''' date = datetime.date for new event
        attendees = list of email addresses
        existing_event = raw exchange event
    '''
    if existing_event:
        #logging.info( f'Existing TRIAGE event {pprint.pprint(ev)}' )
        logging.info( f'Existing TRIAGE event for date "{date}"' )
    else:
        px = get_pyexch()
        logging.info( f'Making new TRIAGE event for date "{date}"' )
        px.new_all_day_event( 
            date = date, 
            subject = f"Triage: {','.join(attendees)}",
            attendees = attendees,
            location = get_triage_location(),
            categories = get_triage_categories(),
            free = True
        )



def run():
    args= get_args()
    # pprint.pprint( ['ARGS', args] )

    # get CSV input
    csv_data = csv.reader( args.infile, dialect='excel-tab' )
    triage_raw_data = { dateutil.parser.parse(row[0]):row[1:] for row in csv_data }
    # pprint.pprint( triage_raw_data )

    # for dt in sorted( existing_events.keys() ):
    #     for typ, ev in current_events[dt].items():
    #         subj = ev.subject
    #         members = [ x.mailbox.email_address for x in ev.raw_event.required_attendees ]
    #         pprint.pprint( [ dt, typ, subj, members ] )

    # (1) create all triage meetings
    triage_start_date = min( triage_raw_data.keys() )
    triage_end_date = max( triage_raw_data.keys() )
    existing_events = get_existing_events(
        start = triage_start_date,
        end = triage_end_date,
    )

    pprint.pprint( existing_events.keys() )
    pprint.pprint( triage_raw_data.keys() )
    raise SystemExit( 'forced exit' )

    for dt, members in triage_raw_data.items():
        try:
            ev = existing_events[dt]['TRIAGE']
        except KeyError:
            ev = None
        #create_or_update_triage_event( date=dt, attendees=members, existing_event=ev)

    # # (2) create / update SHIFTCHANGE events
    # existing_events = get_existing_events(
    #     start = triage_start_date,
    #     end = next_business_day( triage_end_date ),
    # )
    # for today in existing_events.keys():
    #     # get members for today's triage team
    #     triage_ev = existing_events[today]['TRIAGE']
    #     attendees = [ x.mailbox.email_address for x in triage_ev.required_attendees ]
    #     try:
    #         shiftchange_ev = existing_events[dt]['SHIFTCHANGE']
    #     except KeyError:
    #         shiftchange_ev = None
    #     create_or_update_shiftchange_event(
    #         date=dt, attendees=attendees, existing_event=shiftchange_ev )




if __name__ == '__main__':
    log_lvl = logging.INFO
    args = get_args()
    fmt = '%(levelname)s %(message)s'
    if args.debug:
        log_lvl = logging.DEBUG
        fmt = '%(levelname)s [%(filename)s:%(funcName)s:%(lineno)s] %(message)s'
    logging.basicConfig( level=log_lvl, format=fmt )
    no_debug = [
        'exchangelib',
    ]
    for key in no_debug:
        logging.getLogger(key).setLevel(logging.CRITICAL)
    run()

