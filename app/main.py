import bottle
import os
import random
from api import ping_response, start_response, move_response, end_response

INF = 1000000000
DEBUG = True

##set up code from https://github.com/Wyllan/battlesnake-python/blob/master/app/main.py
def debug(message):
    if DEBUG: print(message)


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

    def surrounding_four(self):
        '''Get a list of the 4 surrounding points'''
        return [self.left(), self.right(), self.up(), self.down()]

    def surrounding_eight(self):
        '''Get a list of the 8 surrounding points'''
        return [self.left(), self.right(), self.up(), self.down(),
                self.left().up(), self.left().down(), self.right().up(), self.right().down()]

    def direction_of(self, point):
        '''Returns (roughly) what direction a point is in'''
        if self.x < point.x: return 'right'
        if self.x > point.x: return 'left'
        if self.y < point.y: return 'down'
        if self.y > point.y: return 'up'
        return 'left'  # whatever


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

    def available_space(self, p):
        '''Same as above but return a list of the points'''
        # TODO: Lazy, should find a better way to achieve this.
        visited = []
        return self.rec_flood_fill2(p, visited)

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

    def is_threatened_by_enemy(self, point):
        '''Returns True if this point is in the path of an enemy'''
        for enemy in self.enemies:
            if enemy.length >= self.player.length:
                if point in enemy.head.surrounding_four():
                    return True
        return False

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
        "color": "#9932CC",
        "headType": "",
        "tailType": ""
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # Set-up our board and snake and define its goals
    board = Board(data)
    snake = board.player

    directions= snake.valid_moves()
    direction = random.choice(directions)

    return move_response(direction)

@bottle.post('/end')
def end():
    return {}


@bottle.post('/ping')
def ping():
    return {}


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
