#!/usr/bin/env python

import argparse, sys, re
from argparse import RawTextHelpFormatter

__author__ = "Colby Chinag (cc2qe@virginia.edu)"
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2013-12-29 14:31 $"

# --------------------------------------
# define functions

def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\
parseHtmlStats.py\n\
author: " + __author__ + "\n\
version: " + __version__ + "\n\
description: Basic python script template")
    parser.add_argument('html', nargs='?', type=argparse.FileType('r'), default=None, help='html file to read. If \'-\' or absent then defaults to stdin.')

    # parse the arguments
    args = parser.parse_args()

    # if no input, check if part of pipe and if so, read stdin.
    if args.html == None:
        if sys.stdin.isatty():
            parser.print_help()
            exit(1)
        else:
            args.html = sys.stdin

    # send back the user input
    return args

# primary function
def parseHtml(html):
    # for line in html:
    while 1:
        line = html.readline()
        if line == '':
            break

        if "<TABLE width='300' CELLSPACING=0 CELLPADDING=" in line:
            # get the teams
            #{            print line
            html.readline() # burn a line
            team_1 = html.readline().rstrip().replace('&nbsp;',''); # home team
            html.readline() # burn a line
            final_score = html.readline().rstrip() # final score
            html.readline() # burn a line
            team_2 = html.readline().rstrip().replace('&nbsp;',''); # away team
            # store the teams' final scores
            (team_1_final_score, team_2_final_score) = map(int, final_score.split(' - '))

            # now get the individual scoring times
            team_1_minutes = list()
            team_1_scorers = list()
            team_2_minutes = list()
            team_2_scorers = list()
            while 1:
                line = html.readline()
                # if 'Attendance' in line or 'Att.:&nbsp;' in line:
                if '</TABLE>' in line:
                    break

                # the following indicates that a goal was scored
                if "<tr class='trow3'><td align='right'>" in line or "<TR class='trow3'><TD ALIGN='right'>" in line:
                    s1 = html.readline().rstrip() # home team score line
                    for i in range(3): html.readline() # burn 3 lines
                    s2 = html.readline().rstrip() # away team score line
                    if s1 != '&nbsp;':
                        team_1_scorers.append(s1.split(' (')[0])
                        team_1_minutes.append(int(re.sub('\([^0-9]*\)','',s1).replace(' pen.','').split(' (')[1].replace(')','')))
                    elif s2 != '&nbsp;':
                        team_2_scorers.append(s2.split(' (')[0])
                        team_2_minutes.append(int(re.sub('\([^0-9]*\)','',s2).replace(' pen.','').split(' (')[1].replace(')','')))

            print '\t'.join(map(str, [team_1, team_2, team_1_final_score, team_2_final_score])) + '\t' + ','.join(team_1_scorers) + '\t' + ','.join(map(str,team_1_minutes)) + '\t' + ','.join(team_2_scorers) + '\t' + ','.join(map(str,team_2_minutes))
                    
    return

# --------------------------------------
# main function

def main():
    # parse the command line args
    args = get_args()

    # store into global values
    html = args.html
    
    # call primary function
    parseHtml(html)

    # close the input file
    html.close()

# initialize the script
if __name__ == '__main__':
    sys.exit(main())
