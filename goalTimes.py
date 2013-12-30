#!/usr/bin/env python

import argparse, sys
from argparse import RawTextHelpFormatter

__author__ = "Colby Chiang (cc2qe@virginia.edu)"
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2013-12-29 14:31 $"

# --------------------------------------
# define functions

def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\
goalTimes.py\n\
author: " + __author__ + "\n\
version: " + __version__ + "\n\
description: Analyze time of goal")
    parser.add_argument('data', nargs='?', type=argparse.FileType('r'), default=None, help='tab delimited data to read. If \'-\' or absent then defaults to stdin.')

    # parse the arguments
    args = parser.parse_args()

    # if no input, check if part of pipe and if so, read stdin.
    if args.data == None:
        if sys.stdin.isatty():
            parser.print_help()
            exit(1)
        else:
            args.data = sys.stdin

    # send back the user input
    return args

# basic class for a game
class Fixture(object):
    def __init__(self, v = []):
        if len(v) > 0:
            # ensure that v has 8 elements
            v = v + [''] * (8 - len(v))

            self.team1 = v[0]
            self.team2 = v[1]
            self.team1_final = int(v[2])
            self.team2_final = int(v[3])
            if v[4] != '':
                self.team1_scorers = v[4].split(',')
                self.team1_minutes = map(int,v[5].split(','))
            else:
                self.team1_scorers = []
                self.team1_minutes = []
            if v[6] != '':
                self.team2_scorers = v[6].split(',')
                self.team2_minutes = map(int,v[7].split(','))
            else:
                self.team2_scorers = []
                self.team2_minutes = []

            # calculated attributes
            self.all_minutes = self.team1_minutes + self.team2_minutes
            self.all_scorers = self.team1_scorers + self.team2_scorers
            
            team_goals = [self.team1] * len(self.team1_minutes) + [self.team2] * len(self.team2_minutes)
            self.goal_order = [a for (b,a) in sorted(zip(self.all_minutes, team_goals))]

            # points from match (3 points for win, 1 point for tie, 0 for los)
            if self.team1_final > self.team2_final:
                self.team1_points = 3
                self.team2_points = 0
            elif self.team1_final < self.team2_final:
                self.team1_points = 0
                self.team2_points = 3
            else:
                self.team1_points = 1
                self.team2_points = 1

        else:
            self.valid = 0
            self.query = 'null'

    def first_goal(self):
        if self.goal_order:
            return self.goal_order[0]
        else:
            return 0


    def last_goal(self):
        if self.goal_order:
            return self.goal_order[-1]
        else:
            return 0

    def winner(self):
        if self.team1_final > self.team2_final:
            return self.team1
        elif self.team2_final > self.team1_final:
            return self.team2
        else:
            return 0

    def loser(self):
        if self.team1_final < self.team2_final:
            return self.team1
        elif self.team2_final < self.team1_final:
            return self.team2
        else:
            return 0

    def points(self, which_team):
        if which_team == self.team1:
            return self.team1_points
        elif which_team == self.team2:
            return self.team2_points
        else:
            return

    # given a team name, this returns the other team in the match
    def other_team(self, which_team):
        if which_team == self.team1:
            return self.team2
        elif which_team == self.team2:
            return self.team1
        else:
            return
        

    # return the score at a certain time
    def score_at_time(self, time):
        team1_score = 0
        team2_score = 0
        for i in self.team1_minutes:
            if i <= time: team1_score = team1_score + 1
        for i in self.team2_minutes:
            if i <= time: team2_score = team2_score + 1

        return [team1_score, team2_score]
            

    def minutes_in_lead(self, which_team):
        t = 0
        prev_event = 0
        if which_team == self.team1:
            for g in sorted(self.all_minutes):
                prev_score = self.score_at_time(g-1)
                if prev_score[0] - prev_score[1] > 0:
                    t = t + (g - prev_event)
                prev_event = g

            # add in the lead time at the end of the game
            prev_score = self.score_at_time(90)
            if prev_score[0] - prev_score[1] > 0:
                t = t + (90 - prev_event)
            return t

        elif which_team == self.team2:
            for g in sorted(self.all_minutes):
                prev_score = self.score_at_time(g-1)
                if prev_score[1] - prev_score[0] > 0:
                    t = t + (g - prev_event)
                prev_event = g

            # add in the lead time at end of the game
            prev_score = self.score_at_time(90)
            if prev_score[1] - prev_score[0] > 0:
                t = t + (90 - prev_event)
            return t
        # if which_team not one of the teams, return -1
        else:
            return -1
                


                
            
            
            

# primary function
def myFunction(data):
    for l in data:
        f = Fixture(l.rstrip().split('\t'))

        # this diagnostic line print all the available info
        # print f.team1, f.team2, f.team1_final, f.team2_final, f.team1_scorers, f.team2_scorers, f.team1_minutes, f.team2_minutes

        # test 1
        # print '\t'.join(map(str,[f.first_goal(), f.last_goal(), f.winner(), f.loser(), f.team1_final, f.team2_final]))

        # test 2: minute of first goal
        first_goal_time = None
        if f.all_minutes:
            first_goal_time = sorted(f.all_minutes)[0]

        # test 3: total goals
        num_goals = f.team1_final + f.team2_final
        
        #if first_goal_time:
        #    print '%s\t%s' % (first_goal_time, num_goals)

        # test 4: scoring the first goal vs scoring a goal
        #if (f.team1_minutes and f.team2_minutes):
        #    print '\t'.join(map(str,[f.first_goal(), f.winner()]))


        # test 5: time of goals
        #if f.all_minutes:
        #    for g in f.all_minutes:
        #        print g

        # test 6: minutes in lead
        # print '%s\t%s' % (first_goal_time, f.minutes_in_lead(f.first_goal()))

        # test 7: points from match (3 points for a win, 1 for a tie, 0 for a loss)
        # print '\t'.join(map(str,[f.first_goal(), f.last_goal(), f.winner(), f.loser(), f.team1_final, f.team2_final, f.points(f.first_goal()), f.points(f.last_goal())]))

        # test 8: points expected for scoring first goal in matches in which there is more than 1 goal
        #if num_goals > 1:
        #    print '\t'.join(map(str,[f.first_goal(), f.last_goal(), f.winner(), f.loser(), f.team1_final, f.team2_final, f.points(f.first_goal()), f.points(f.last_goal())]))

        # test 9: points expected for scoring any non-first goal in matches in which there is more than 1 goal
        if num_goals > 1:
            #            if f.team1_final

            print '\t'.join(map(str,[f.first_goal(), f.last_goal(), f.winner(), f.loser(), f.team1_final, f.team2_final, f.points(f.first_goal()), f.points()]))            

    
    return

# --------------------------------------
# main function

def main():
    # parse the command line args
    args = get_args()

    # store into global values
    data = args.data
    
    # call primary function
    myFunction(data)

    # close the input file
    data.close()

# initialize the script
if __name__ == '__main__':
    sys.exit(main())
