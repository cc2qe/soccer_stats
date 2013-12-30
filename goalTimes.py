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
    parser.add_argument('-d', '--debug', required=False, action='store_true', help='show debugging info for each game')
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

# in a fixture, there are two teams. each has certain properties defined here
class Team(object):
    def __init__(self, name, num_scored, num_conceded, goal_scorers, goal_minutes, is_home):
        # given attributes #
        self.name = name
        self.num_scored = int(num_scored)
        self.num_conceded = int(num_conceded)
        self.goal_scorers = goal_scorers
        self.goal_minutes = map(int,goal_minutes)
        self.is_home = bool(is_home) # true if home team, false if visiting team

        # derived attributes #
        # points from match (3 for win, 1 for tie, 0 for loss)
        if self.num_scored > self.num_conceded:
            self.points = 3
        elif self.num_scored == self.num_conceded:
            self.points = 1
        else:
            self.points = 0

    # import the opposing team (can't do on init, since other team might not have been created yet)
    def add_opponent(self, opponent):
        self.opp = opponent

    # return the team's score at a certain time
    def score_at_time(self, time):
        score = 0
        for i in self.goal_minutes:
            if i <= time: score = score + 1
        return score

    # define a global 'null team' with empty attributes to return
    @staticmethod
    def null():
        t = Team('null', -1, -1, [], [], False)
        t.add_opponent(t)
        return t

# basic class for a game
class Fixture(object):
    def __init__(self, v = []):
        if len(v) > 0:
            # ensure that v has 8 elements
            v = v + [''] * (8 - len(v))

            team1_name = v[0]
            team2_name = v[1]
            team1_num_scored = int(v[2])
            team2_num_scored = int(v[3])
            if v[4] != '':
                team1_scorers = v[4].split(',')
                team1_minutes = map(int,v[5].split(','))
            else:
                team1_scorers = []
                team1_minutes = []
            if v[6] != '':
                team2_scorers = v[6].split(',')
                team2_minutes = map(int,v[7].split(','))
            else:
                team2_scorers = []
                team2_minutes = []

            self.team1 = Team(team1_name, team1_num_scored, team2_num_scored, team1_scorers, team1_minutes, True)
            self.team2 = Team(team2_name, team2_num_scored, team1_num_scored, team2_scorers, team2_minutes, False)

            # import their opponents
            self.team1.add_opponent(self.team2)
            self.team2.add_opponent(self.team1)

            # derived attributes #
            unsorted_goal_minutes = self.team1.goal_minutes + self.team2.goal_minutes
            unsorted_goal_scorers = self.team1.goal_scorers + self.team2.goal_scorers
            unsorted_team_goals = [self.team1] * self.team1.num_scored + [self.team2] * self.team2.num_scored
            self.goal_order = [a for (b,a) in sorted(zip(unsorted_goal_minutes, unsorted_team_goals))]
            self.scorer_order = [a for (b,a) in sorted(zip(unsorted_goal_minutes, unsorted_goal_scorers))]
            self.goal_minutes = sorted(unsorted_goal_minutes)
            
            # number of goals in the match
            self.num_goals = self.team1.num_scored + self.team2.num_scored

            # get winner and loser (if not a draw)
            if self.team1.points == 3:
                self.winner = self.team1
                self.loser = self.team2
            elif self.team2.points == 3:
                self.winner = self.team2
                self.loser = self.team1
            else:
                self.winner = Team.null()
                self.loser = Team.null()

    # basic data validation
    def isValid(self):
        self.valid = 1

        for t in [self.team1, self.team2]:
            # two teams exist
            if not t:
                self.valid = 0
            # same num of goals and scorers
            elif len(t.goal_scorers) != t.num_scored:
                self.valid = 0
            elif len(t.goal_scorers) != len(t.goal_minutes):
                self.valid = 0

        return self.valid

        
    # methods in Fixture #
    def get_team_by_name(query_name):
        for t in [self.team1, self.team2]:
            if query_name == t.name:
                return t
        return Team.null()

    # returns the team object that scored the first goal
    def first_goal(self):
        if self.goal_order:
            return self.goal_order[0]
        else:
            return Team.null()

    # returns the team object that scored the last goal
    def last_goal(self):
        if self.goal_order:
            return self.goal_order[-1]
        else:
            return Team.null()

    # returns the team object that scored the kth goal
    def scoring_team(k):
        return self.goal_order[k-1]

    # returns the time (minute) of the kth goal
    def time_of_goal(self,k):
        return self.goal_minutes[k-1]

    # the number of minutes that a team spent leading the match
    def minutes_in_lead(self, myTeam):
        t = 0
        prev_event = 0
        for g in self.goal_minutes:
            prev_score = myTeam.score_at_time(g-1)
            opp_prev_score = myTeam.opp.score_at_time(g-1)
            if prev_score > opp_prev_score:
                t = t + (g - prev_event)
            prev_event = g
        # add in the lead time at the end of the game
        prev_score = myTeam.score_at_time(90)
        opp_prev_score = myTeam.opp.score_at_time(90)
        if prev_score > opp_prev_score:
            t = t + (90 - prev_event)

        return t

# driver function
def myFunction(data, debug):
    for l in data:
        f = Fixture(l.rstrip().split('\t'))

        # this diagnostic line print all the available info
        if debug:
            print f.team1.name, f.team2.name, f.team1.num_scored, f.team2.num_scored, f.team1.goal_scorers, f.team2.goal_scorers, f.team1.goal_minutes, f.team2.goal_minutes

        if not f.isValid():
            continue

        # test 1
        # print '\t'.join(map(str,[f.first_goal().name, f.last_goal().name, f.winner.name, f.loser.name, f.team1.num_scored, f.team2.num_scored]))

        # test 2: minute of first goal
        # if f.num_goals > 0:
        #    print f.time_of_goal(1)

        # test 3: minute of last goal
        # if f.num_goals >0:
        #     print f.time_of_goal(f.num_goals)

        # test 4: total goals
        # print f.num_goals
        
        # test 5: scoring the first goal vs scoring a goal
        # if (f.team1.num_scored and f.team2.num_scored):
        #    print '\t'.join(map(str,[f.first_goal().name, f.winner.name]))


        # test 6: time of goals
        #if f.num_goals > 0:
        #    for g in f.goal_minutes:
        #        print g

        # test 6: minutes in lead
        #if f.num_goals > 0:
        #    print '%s\t%s' % (f.time_of_goal(1), f.minutes_in_lead(f.first_goal()))

        # test 7: points from match (3 points for a win, 1 for a tie, 0 for a loss)
        # if f.num_goals > 0:
        #    print '\t'.join(map(str,[f.first_goal().name, f.last_goal().name, f.winner.name, f.loser.name, f.team1.num_scored, f.team2.num_scored, f.first_goal().points, f.last_goal().points]))

        # test 8: points expected for scoring first goal in matches in which there is more than 1 goal
        #if f.num_goals > 1:
        #    print '\t'.join(map(str,[f.first_goal().name, f.last_goal().name, f.winner.name, f.loser.name, f.team1.num_scored, f.team2.num_scored, f.first_goal().points, f.last_goal().points]))

        # test 9: points expected for scoring any non-first goal in matches in which there is more than 1 goal
        '''    
        if f.num_goals > 1:
            for t in f.goal_order[1:]:
                if f.team1 == t:
                    print f.team1.points
                    break
            for t in f.goal_order[1:]:
                if f.team2 == t:
                    print f.team2.points
                    break
        '''

        # test 10: points expected for scoring first goal in matches in which there is more than 1 goal
        #if f.num_goals > 1:
        #    print f.first_goal().points



    return

# --------------------------------------
# main function

def main():
    # parse the command line args
    args = get_args()

    # store into global values
    data = args.data
    debug = args.debug

    # call primary function
    myFunction(data, debug)

    # close the input file
    data.close()

# initialize the script
if __name__ == '__main__':
    sys.exit(main())
