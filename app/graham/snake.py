import bottle
import os
import random as rand
import sys
import neural_network as nn
import numpy as np
from api import ping_response, start_response, move_response, end_response
import signal

INF = 1000000000
DEBUG = True


##set up code from https://github.com/Wyllan/battlesnake-python/blob/master/app/main.py
def debug(message):
    if DEBUG: print(message)

#Declare the snake's neural network and move count
weights = None
movecount = 0
gamecount = 0
queue = None
server = None
	
class Point:
    '''Simple class for points'''

    def __init__(self, x, y):
        '''Defines x and y variables'''
        self.x = x
        self.y = y

    def __eq__(self, other):
        '''Test equality'''
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return (str)(self.x) + ',' + (str)(self.y)

    def __repr__(self):
        return self.__str__()

    def closest(self, l):
        '''Returns Point in l closest to self'''
        closest = l[0]
        for point in l:
            if (self.dist(point) < self.dist(closest)):
                closest = point
        return closest

    def dist(self, other):
        '''Calculate Manhattan distance to other point'''
        # TODO: Should use A* dist not Manhattan
        return abs(self.x - other.x) + abs(self.y - other.y)
    def xydist(self,other):
        return abs(self.x - other.x),  abs(self.y - other.y)

    def get(self, direction):
        '''get an adjacent point by passing a string'''
        if (direction == 'left'):
            return self.left()
        if (direction == 'right'):
            return self.right()
        if (direction == 'up'):
            return self.up()
        if (direction == 'down'):
            return self.down()

    class Point:
        '''Simple class for points'''

        def __init__(self, x, y):
            '''Defines x and y variables'''
            self.x = x
            self.y = y

        def __eq__(self, other):
            '''Test equality'''
            return self.x == other.x and self.y == other.y

        def __str__(self):
            return (str)(self.x) + ',' + (str)(self.y)

        def __repr__(self):
            return self.__str__()

        def closest(self, l):
            '''Returns Point in l closest to self'''
            closest = l[0]
            for point in l:
                if (self.dist(point) < self.dist(closest)):
                    closest = point
            return closest

        def dist(self, other):
            '''Calculate Manhattan distance to other point'''
            # TODO: Should use A* dist not Manhattan
            return abs(self.x - other.x) + abs(self.y - other.y)

        def get(self, direction):
            '''get an adjacent point by passing a string'''
            if (direction == 'left'):
                return self.left()
            if (direction == 'right'):
                return self.right()
            if (direction == 'up'):
                return self.up()
            if (direction == 'down'):
                return self.down()

        def left(self):
            '''Get the point to the left'''
            return Point(self.x - 1, self.y)

        def right(self):
            '''Get the point to the right'''
            return Point(self.x + 1, self.y)

        def up(self):
            '''Get the point above'''
            return Point(self.x, self.y - 1)

        def down(self):
            '''Get the point below'''
            return Point(self.x, self.y + 1)


def point_from_string(string):
    s = string.split(',')
    return Point(int(s[0]), int(s[1]))


class Snake:
    '''Simple class to represent a snake'''

    def __init__(self, board, data):
        '''Sets up the snake's information'''
        self.board = board
        self.id = data['id']
        self.name = data['name']
        self.health = data['health']
        self.head = Point(data['body'][0]['x'],
                          data['body'][0]['y'])
        self.tail = Point(data['body'][-1]['x'],
                          data['body'][-1]['y'])
        self.body = []

        for b in data['body'][1:]:
            self.body.append(Point(b['x'], b['y']))

        self.length = len(self.body)
        self.next_move = ''

    # High level, composable actions the snake can perform


    def valid_moves(self):
        '''Returns a list of moves that will not immediately kill the snake'''
        moves = ['up', 'down', 'left', 'right']
        for move in moves[:]:
            next_pos = self.head.get(move)
            if ((next_pos in self.board.obstacles or
                 self.board.is_outside(next_pos)) and
                    (next_pos not in self.board.tails or
                     self.board.tail_health.get(str(next_pos)) == 100)):
                moves.remove(move)
        return moves



class Board:
    '''Simple class to represent the board'''

    def __init__(self, data):
        '''Sets the board information'''
        self.width = data['board']['width']
        self.height = data['board']['height']
        self.player = Snake(self, data['you'])
        self.enemies = []
        self.turn = data['turn']
        self.food = []
        self.obstacles = []
        self.heads = []
        self.tails = []
        self.tail_health = {}
        self.snake_length = {}

        for snake_data in data['board']['snakes']:
            snake = Snake(self, snake_data)
            for point in snake_data['body']:
                self.obstacles.append(Point(point['x'], point['y']))
            if snake.id != self.player.id:
                self.enemies.append(snake)
                self.heads.append(snake.head)
                self.snake_length[str(snake.head)] = snake.length
            self.tails.append(snake.tail)
            self.tail_health[str(snake.tail)] = snake.health

        for p in data['board']['food']:
            self.food.append(Point(p['x'], p['y']))

    def is_outside(self, p):
        '''Return true if p is out-of-bounds'''
        return p.x < 0 or p.y < 0 or p.x >= self.width or p.y >= self.height

    def neighbors_of(self, p):
        '''Return list of accessible neighbors of point'''
        res = []
        for p in p.surrounding_four():
            if p not in self.obstacles and not self.is_outside(p):
                res.append(p)
        return res

    def snakes_are_around_point(self, p):
        for point in p.surrounding_eight():
            if point in self.heads and self.snake_length[str(point)] >= self.player.length:
                return True
        return False

    def count_available_space(self, p):
        '''flood fill out from p and return the accessible area'''
        visited = []
        return self.rec_flood_fill(p, visited)

    def rec_flood_fill(self, p, visited):
        '''Recursive flood fill (Used by above method)'''
        if p in visited or p in self.obstacles or self.is_outside(p):
            return 0
        visited.append(p)
        return 1 + (self.rec_flood_fill(p.left(), visited) +
                    self.rec_flood_fill(p.right(), visited) +
                    self.rec_flood_fill(p.up(), visited) +
                    self.rec_flood_fill(p.down(), visited))

    def count_available_space_and_snake_data(self, p):
        '''flood fill out from p and return the accessible area, head, and tail count'''
        visited = []
        heads = []
        tails = []
        space = self.rec_flood_fill_with_snake_data(p, visited, heads, tails)
        return [space, len(heads), len(tails)]

    def rec_flood_fill_with_snake_data(self, p, visited, heads, tails):
        '''Recursive flood fill that also counts the number of heads and tails'''
        if p in visited or p in self.obstacles or self.is_outside(p):
            if p in self.heads and p not in heads and p != self.player.head:
                heads.append(p)
            if p in self.tails and p not in tails:
                tails.append(p)
            return 0
        visited.append(p)
        return 1 + (self.rec_flood_fill_with_snake_data(p.left(), visited, heads, tails) +
                    self.rec_flood_fill_with_snake_data(p.right(), visited, heads, tails) +
                    self.rec_flood_fill_with_snake_data(p.up(), visited, heads, tails) +
                    self.rec_flood_fill_with_snake_data(p.down(), visited, heads, tails))

    def rec_flood_fill2(self, p, visited):
        '''Same as above but returns a list of the points'''
        if p in visited or p in self.obstacles or self.is_outside(p):
            return visited
        visited.append(p)
        self.rec_flood_fill(p.left(), visited)
        self.rec_flood_fill(p.right(), visited)
        self.rec_flood_fill(p.up(), visited)
        self.rec_flood_fill(p.down(), visited)
        return visited

    def distances(self, start, points):
        '''Returns a dict of the distances between start and each point'''
        distances = {}
        for point in points:
            distance = len(self.a_star_path(start, point))
            if distance > 0:
                distances[str(point)] = distance
        return distances

    def a_star_path(self, start, goal):
        '''Return the A* path from start to goal. Adapted from wikipedia page
        on A*.
        '''
        # TODO: Seems fast enough but code could be cleaned up a bit.

        closed_set = []
        open_set = [start]
        came_from = {}
        g_score = {}
        f_score = {}

        str_start = str(start)
        g_score[str_start] = 0
        f_score[str_start] = start.dist(goal)

        while open_set:
            str_current = str(open_set[0])
            for p in open_set[1:]:
                str_p = str(p)
                if str_p not in f_score:
                    f_score[str_p] = INF
                if str_current not in f_score:
                    f_score[str_current] = INF
                if f_score[str_p] < f_score[str_current]:
                    str_current = str_p

            current = point_from_string(str_current)

            if current == goal:
                path = self.reconstruct_path(came_from, current)
                path.reverse()
                return path[1:]

            open_set.remove(current)
            closed_set.append(current)

            for neighbor in self.neighbors_of(current):
                str_neighbor = str(neighbor)
                if neighbor in closed_set:
                    continue

                if neighbor not in open_set:
                    open_set.append(neighbor)

                if str_current not in g_score:
                    g_score[str_current] = INF
                if str_neighbor not in g_score:
                    g_score[str_neighbor] = INF


                tentative_g_score = (g_score[str_current] +
                                     current.dist(neighbor))
                if tentative_g_score >= g_score[str_neighbor]:
                    continue

                came_from[str_neighbor] = current
                g_score[str_neighbor] = tentative_g_score
                f_score[str_neighbor] = (g_score[str_neighbor] +
                                         neighbor.dist(goal))
        return []

    def reconstruct_path(self, came_from, current):
        '''Get the path as a list from A*'''
        total_path = [current]
        while str(current) in came_from.keys():
            current = came_from[str(current)]
            total_path.append(current)
        return total_path

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/start')
def start():

    return {
        "name" : "Buster",
        "color": "#FF69B4",
        "headType": "evil",
        "tailType": "bolt"
    }

@bottle.post('/move')
def move():
    data = bottle.request.json
    # Set-up our board and snake and define its goals
    board = Board(data)
    snake_head = board.player.head
    snake=board.player
    foods= board.food
    apple = snake_head.closest(foods)
    x_dist = snake_head.x-apple.x
    y_dist=snake_head.y-apple.y
    directions = snake.valid_moves()
    down_blocked=1
    up_blocked=1
    right_blocked=1
    lef_blocked = 1
    if 'up' in directions:
        up_blocked=0
    if 'down' in directions:
        down_blocked=0
    if 'right' in directions:
        right_blocked=0
    if 'left' in directions:
        left_blocked=0
    #get the point on the enmey snake that is closest to us
    enemy = board.enemies
    tail_array = enemy.tail
    danger_point = snake_head.closest(tail_array)
    x_dang = snake_head.x - danger_point.x
    y_dang = snake_head.y - danger_point.y
    #findout if the enemy snake can eat us
    tasty_snake=0
    if enemy.length >= snake.length:
        tasty_snake = 1

    X = np.array([snake_head.x, snake_head.y, x_dist, y_dist,up_blocked,down_blocked,lef_blocked,right_blocked,x_dang,y_dang,tasty_snake])
    direction = nn.forward_propagation(X, weights)
    move_int = np.argmax(direction)
    if move_int == 0:
        move = 'up'
    if move_int == 1:
        move = 'right'
    if move_int == 2:
        move = 'down'
    if move_int == 3:
        move = 'left'
		
    #print(move)
    global movecount
    movecount = movecount + 1
    return move_response(move)

@bottle.post('/end')
def end():
    global gamecount
    global movecount
	#queue needed to pass value back to parent
    #print(movecount)
    queue.put(movecount)
    gamecount = gamecount+1
    movecount = 0
    #application.close()
    #sys.stderr.close()
    #server.stop()
    try:
        return end_response()
    finally:
        if(gamecount==3):
            server.stop()  


@bottle.post('/ping')
def ping():
    return ping_response()

class MyWSGIRefServer(bottle.ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.server_close() #<--- alternative but causes bad fd exception
        #self.server.shutdown()

# Expose WSGI app (so gunicorn can find it)
def run(port, w, q, b):
    app = bottle.default_app()
    global weights
    global queue
    global server
    global movecount
    global gamecount
    gamecount = 0
    movecount = 0
    queue = q
    weights = w
    #print('running bottle')
    server = MyWSGIRefServer(os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', port))
    try:
        app.run(server=server, quiet=True)
    except Exception as e: 
        #import traceback
        #print(traceback.format_exc())
        #print(e)
        ()
