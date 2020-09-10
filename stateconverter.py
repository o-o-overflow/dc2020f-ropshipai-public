
import game

import copy
import math
from collections import OrderedDict
import shapely
from shapely.geometry import Point
from shapely.geometry import LineString
import struct
import os


def state_to_nnstate(state, defcon_id):
    def ls(v, mx, mn = 0):
        return round((float(v)-float(mn)) / float(mx-mn),8)
    
    def bs(v):
        return 1.0 if v else 0.0

    def distance(x1,y1,x2,y2):
        dx = x1-x2
        dy = y1-y2
        return math.sqrt(dx**2+dy**2)

    def coord_to_distance(sx, sy, ix, iy, radius):
            d = distance(sx, sy, ix, iy)
            return ls((radius*2*1.002) - d, (radius*2*1.002))

    def location_to_outer_circle(location, radius, direction=0):
        l2 = copy.deepcopy(location)
        l2.move(a=direction,t=10000.0)
        p = Point(0,0)
        c = p.buffer(radius*1.002).boundary
        l = LineString([(location.x, location.y), (l2.x, l2.y)])
        i = c.intersection(l)

        invalid_point = False
        try:
            t = type(i.coords)
            if t is list:
                invalid_point = True
        except NotImplementedError:
            invalid_point = True

        if not invalid_point:
            return coord_to_distance(location.x, location.y, i.xy[0][0], i.xy[1][0], radius)
        else:
            return 1.0

    def location_to_inner_circle(location, radius, direction=0):
        l2 = copy.deepcopy(location)
        l2.move(a=direction,t=10000.0)
        p = Point(0,0)
        c = p.buffer(radius*0.998).boundary
        l = LineString([(location.x, location.y), (l2.x, l2.y)])
        i = c.intersection(l)

        invalid_point = False
        try:
            t = type(i.coords)
            if t is list:
                if len(i.coords) == 0: 
                    return 0.0
                else:
                    return 0.0 

        except NotImplementedError:
            i1, i2 = list(i)
            sd1 = coord_to_distance(location.x, location.y, i1.xy[0][0], i1.xy[1][0], radius)
            sd2 = coord_to_distance(location.x, location.y, i2.xy[0][0], i2.xy[1][0], radius)
            return max(sd1, sd2)

        return coord_to_distance(location.x, location.y, i.xy[0][0], i.xy[1][0], radius)

    def team_to_dict(state, team):
        tstate = OrderedDict()
        tstate["xxx"] = 1.0 
        tstate["fspeed"] = ls(team.ship.fspeed, game.MAXFSPEED, 0.0)
        tstate["aspeed"] = ls(team.ship.aspeed, game.MAXASPEED, -game.MAXASPEED)
        tstate["shield_available"] = min((state.tick - team.last_shield)/float(game.SHIELDDELAY), 1.0)
        tstate["attack_available"] = min((state.tick - team.last_shooting)/float(game.BULLETDELAY), 1.0)

        tstate["ocirclef"] = location_to_outer_circle(team.ship.location, state.boardradius, direction=0)
        tstate["ocircleb"] = location_to_outer_circle(team.ship.location, state.boardradius, direction=math.pi)
        tstate["ocirclel"] = location_to_outer_circle(team.ship.location, state.boardradius, direction=math.pi/2.0)
        tstate["ocircler"] = location_to_outer_circle(team.ship.location, state.boardradius, direction=-math.pi/2.0)
        tstate["icirclef"] = location_to_inner_circle(team.ship.location, state.boardradius_inner, direction=0)
        tstate["icircleb"] = location_to_inner_circle(team.ship.location, state.boardradius_inner, direction=math.pi)
        tstate["icirclel"] = location_to_inner_circle(team.ship.location, state.boardradius_inner, direction=math.pi/2.0)
        tstate["icircler"] = location_to_inner_circle(team.ship.location, state.boardradius_inner, direction=-math.pi/2.0)

        slist_distances = []
        for tid, team2 in state.teams.items():
            if team2 == team:
                continue
            if team2.ship == None:
                slist_distances.append((0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            else:
                dd = distance(team2.ship.location.x, team2.ship.location.y, team.ship.location.x, team.ship.location.y)
                rda = math.atan2(team2.ship.location.y-team.ship.location.y, team2.ship.location.x-team.ship.location.x)
                sa = ls(math.sin(rda-team.ship.location.a), 1, -1)
                ca = ls(math.cos(rda-team.ship.location.a), 1, -1)
                sad = ls(math.sin(rda-team2.ship.location.a), 1, -1)
                cad = ls(math.cos(rda-team2.ship.location.a), 1, -1)
                slist_distances.append((ls(game.BOARDSIZE*game.BOARDRADIUS*2 - dd, game.BOARDSIZE*game.BOARDRADIUS*2, 0), sa, ca, bs(team2.shield), sad, cad))
        sorted_distances = sorted(slist_distances, key=lambda x:round(-1*x[0],10)+x[1]/100000000000)
        for i in range(3):
            tstate["ships"+str(i)+"d"], tstate["ships"+str(i)+"sa"], tstate["ships"+str(i)+"ca"], tstate["ships"+str(i)+"shield"], tstate["ships"+str(i)+"sad"], tstate["ships"+str(i)+"cad"] = sorted_distances[i]
            
        slist_distances = [(0.0, 0.0, 0.0, 0.0, 0.0)]*5
        for tid, team2 in state.teams.items():
            if team2 == team:
                continue
            for b in team2.bullets:
                dd = distance(b.location.x, b.location.y, team.ship.location.x, team.ship.location.y)
                rda = math.atan2(b.location.y-team.ship.location.y, b.location.x-team.ship.location.x)
                sa = ls(math.sin(rda-team.ship.location.a), 1, -1)
                ca = ls(math.cos(rda-team.ship.location.a), 1, -1)
                sad = ls(math.sin(rda-b.location.a), 1, -1)
                cad = ls(math.cos(rda-b.location.a), 1, -1)
                slist_distances.append((ls(game.BOARDSIZE*game.BOARDRADIUS*2 - dd, game.BOARDSIZE*game.BOARDRADIUS*2, 0), sa, ca, sad, cad))
        sorted_distances = sorted(slist_distances, key=lambda x:round(-1*x[0],10)+x[1]/100000000000)
        for i in range(3):
            tstate["bullets"+str(i)+"d"], tstate["bullets"+str(i)+"sa"], tstate["bullets"+str(i)+"ca"], tstate["bullets"+str(i)+"sad"], tstate["bullets"+str(i)+"cad"] = sorted_distances[i]

        return tstate



    team = state.teams_by_defcon_id[defcon_id]
    return team_to_dict(state, team)


def serialize(nnstate, fname):
    try:
        os.unlink(fname)
    except OSError:
        pass
    vl = list(nnstate.values())
    with open(fname, "wb") as fp:
        fp.write(struct.pack("="+str(len(vl))+"f", *vl))

