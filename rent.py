import math, random

# Small epsilon used for numeric comparisons (zero threshold, equality)
EPS = 0.01
# Number of decimal places to round coordinates to when storing Points
ROUNDING = 3

# ============================= Strategies =============================

def cheapskateStrategy(point):
    """Return the index (room id) of the cheapest room at this point.

    If there is a tie, the smaller-indexed room is chosen because
    `index` returns the first matching value.
    """
    min_cost = min(point.coords)
    min_index = point.coords.index(min_cost)
    return rooms[min_index]

def makeRoomNStrategy(n):
    if n not in rooms:
        raise Exception('No such room {} in all rooms {}'
                .format(n, rooms))
    def wantRoomNStrategy(point):
        if 0 in point.coords and point.coords[n-1] != 0:
            return cheapskateStrategy(point)
        else:
            return n
    return wantRoomNStrategy

def randomStrategy(point):
    """Choose a valid room at random from `rooms`.

    The original implementation returned a random integer in a numeric
    range which could produce 0 or an out-of-range value. Use
    `random.choice(rooms)` to guarantee a valid room id is returned.
    """
    return random.choice(rooms)

# prices = {1 : 500, 2: 500, 3: 0, 'favorite': 1, 'order': [1,2,3]}
def makeCapStrategy(prices):
    def capStrategy(point):
        if 0 in point.coords and point.coords[prices['favorite']-1] != 0:
            return cheapskateStrategy(point)
        for i in prices['order']:
            if point.coords[i-1] < prices[i]:
                return i
    return capStrategy

# ============================= Initialization =============================

# Housemates
housemates = ['A', 'B', 'C']

# Rooms
rooms = [1, 2, 3]

# This is a dumb strategy where the player always chooses the
# cheapest room. If tie, choose the smaller numbered room

# By default several strategy configurations were present in the file.
# Uncomment or change the `strategies` assignment you want to use.

# Example: everyone picks a random room
# strategies = { 'A' : randomStrategy, 'B' : randomStrategy, 'C' : randomStrategy }

# Example: everyone picks the cheapest room
# strategies = { 'A' : cheapskateStrategy, 'B' : cheapskateStrategy, 'C' : cheapskateStrategy }

# Example: A always wants room 3 (unless special rule triggers)
# strategies = { 'A' : makeRoomNStrategy(3), 'B' : cheapskateStrategy, 'C' : cheapskateStrategy }

# Example: A has a capped preference ordering
capA = {1: 500, 2:500, 3:0, 'favorite':1, 'order':[1,2,3]}
strategies = { 'A' : makeCapStrategy(capA),
               'B' : cheapskateStrategy,
               'C' : cheapskateStrategy }

# Total rent to split across rooms (sum of a Point's coords must equal this)
total_rent = 1000

# ============================= Initialization =============================

class Point():
    """A point in the simplex representing a price split across rooms.

    coords: a tuple of non-negative numbers whose sum equals `total_rent`.
    The constructor validates inputs, applies a small-zero threshold and
    rounding, and then computes each housemate's decision at that point by
    calling the strategy functions.
    """
    def __init__(self, *coords):
        # Dimension check: we assume one coordinate per room
        if len(coords) != len(rooms):
            raise Exception('Mismatched dimensions {} != {}'
                    .format(coords, rooms))

        # Use a small tolerance when checking sums. The original code used
        # a tolerance of 1 which is large; use EPS instead for stricter checks.
        if abs(sum(coords) - total_rent) > EPS:
            raise Exception(
                    'Total coordinates does not add up to total rent! {} != {}'
                    .format(coords, total_rent))

        if min(coords) < 0:
            raise Exception('Negative values in coordinates: {}'
                    .format(coords))

        # Zero-out tiny values and round coordinates for cleaner output
        coords = tuple([0 if i < EPS else round(i,ROUNDING) for i in coords])
        self.coords = coords

        # Precompute what each housemate would choose at this price vector
        self.decisions = {}
        for h in housemates:
            self.decisions[h] = self.query(h)

    def distance(self, other):
        return math.sqrt(sum([(self.coords[i] - other.coords[i]) ** 2
            for i in range(len(self.coords))]))

    def findPoint(self, pt2, t=0.5): # t = 0, return pt1, t = 1, return pt2
        # Linear interpolation between two points; returns a new Point.
        return Point(*[(1-t) * self[i] + t * pt2[i] for i in range(len(self))])

    # Returns the chosen room for a particular housemate
    def query(self, housemate):
        return strategies[housemate](self)

    def __eq__(self, other):
        # Points are considered equal when all coordinates are close within EPS
        return all([abs(self[i] - other[i]) < EPS for i in range(len(self))])

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, key):
        return self.coords[key]

    def __str__(self):
        return str(self.coords)

    def __repr__(self):
        return str(self)

class Triangle():
    def __init__(self, pt1, pt2, pt3, initInner=False, name=""):
        """A triangle in the simplex defined by three Point corners.

        The class can initialize its midpoints and an internal barycentre, then
        optionally create the six inner (sub-)triangles used for combinatorial
        subdivision. `corner_label` is a 3-character string where each
        character is a housemate label indicating which housemate's choice
        to read at the corresponding corner.
        """
        self.corners = [pt1, pt2, pt3]
        self.all_points = []
        self.mid_points = []
        self.inner_triangles = []
        # Default corner_label: ask housemate 'A' at every corner
        self.corner_label = 'AAA'
        # Flag meaning that this triangle's corner-queries cover all rooms
        self.good = False
        self.name = name

        self.initPointsFromCorners()
        # Default labelling used when generating inner corner labels
        self.labels = ['ABC', 'BAC', 'CAB', 'CBA', 'BCA', 'ACB']

        if initInner:
            self.initInnerTriangles()

    """
    Arrangement of points
          c0
         /  \
        /    \
       m0  b  m2
      /        \
     /          \
    c1 -- m1 -- c2
    
    """
    def initPointsFromCorners(self):
        c = self.corners
        self.mid_points = []
        for i in range(len(c)):
            self.mid_points.append(c[i].findPoint(c[(i+1)%len(c)]))
        self.barycentre_pt = c[0].findPoint(self.mid_points[1], 2/3)
        self.all_points = self.mid_points + c + [self.barycentre_pt]

    """
    Arrangement of inner triangles

                  c0
                  /\
                 /| \
                / |  \
               /  |   \
              /   |    \
             /    |     \
           m0   0 |  5  m2
           /  .   |   .    \
          /       b         \
         /  1  .  |  .  4    \
        /   .  2  |  3  .     \
       / .        |         .  \
      c1----------m1-----------c2

    Labelling of who to ask with Corner label AAA
                   A
                  /\
                 /| \
                / |  \
               /  |   \
              /   |    \
             /    |     \
            B   0 |  5   B
           /  .   |   .    \
          /       C         \
         /  1  .  |  .  4    \
        /   .  2  |  3  .     \
       / .        |         .  \
      A ----------B ----------- A


      After pulling

      m0----------c0-----------m2
       \ .        |         .  /
        \   .  0  |  5  .     /
         \  1  .  |  .  4    /
          \       b         /
           \  .   |   .    /
           c1   2 |  3  c2
             \    |     /
              \   |    /
               \  |   /
                \ |  /
                 \| /
                  \/
                  m1
    """
    def initChoicesFromCornerLabel(self):
        """Compute the choices for the triangle by asking the corner_label

        corner_label is a 3-character string, where the i-th character is
        the housemate whose decision to read at corner i. We collect the
        chosen rooms (as ints) and set `self.good` when all rooms appear.
        """
        choices = []
        for i in range(len(self.corner_label)):
            l = self.corner_label[i]
            # corner's decision for housemate l (an int room id)
            choices.append(self.corners[i].decisions[l])
        self.choices = choices
        # A triangle is "good" when the set of chosen rooms contains every room
        self.good = all([room in self.choices for room in rooms])

    def initInnerTriangles(self):
        c = self.corners
        m = self.mid_points
        b = self.barycentre_pt
        t0 = Triangle(c[0], m[0], b, False, self.name + '0')
        t1 = Triangle(m[0], c[1], b, False, self.name + '1')
        t2 = Triangle(b, c[1], m[1], False, self.name + '2')
        t3 = Triangle(b, m[1], c[2], False, self.name + '3')
        t4 = Triangle(m[2], b, c[2], False, self.name + '4')
        t5 = Triangle(c[0], b, m[2], False, self.name + '5')

        self.inner_triangles = [t0, t1, t2, t3, t4, t5]

        # Set the inner labels and compute whether each inner triangle is good
        for i in range(len(self.inner_triangles)):
            t = self.inner_triangles[i]
            l = self.labels[i]
            t.corner_label = l
            t.initChoicesFromCornerLabel()
            if t.good:
                # If an inner triangle is already good, propagate labels further
                t.generateLabelsFromCornerLabel()


    """
    Labelling of who to ask from Corner Labels l0 l1 l2
                  l0 
                  /\
                 /| \
                / |  \
               /  |   \
              /   |    \
             /    |     \
           l3   0 |  5   l4
           /  .   |   .    \
          /      l5         \
         /  1  .  |  .  4    \
        /   .  2  |  3  .     \
       / .        |         .  \
     l1 ---------l6 ----------- l2
    """
    def generateLabelsFromCornerLabel(self):
        if any([x not in self.corner_label for x in housemates]):
            raise Exception('Cannot generate labels if non-distinct corner labels {}'
                    .format(self.corner_label))

        l0 = self.corner_label[0]
        l1 = self.corner_label[1]
        l2 = self.corner_label[2]
        l3 = l2
        l4 = l1
        l6 = l0
        # l5 is a function that gives that last label give 2 labels
        l5 = lambda x, y: [z for z in housemates if z not in [x, y]][0]

        self.labels = [l0+l3+l5(l0, l3),
                       l3+l1+l5(l3, l1),
                       l5(l1, l6)+l1+l6,
                       l5(l6, l2)+l6+l2,
                       l4+l5(l4, l2)+l2,
                       l0+l5(l0, l4)+l4]


    def getGoodInnerTriangleIndex(self):
        """Return (index, triangle) for the first inner triangle marked good.

        Raises IndexError if no inner triangle is good.
        """
        t = self.inner_triangles
        idx = [i for i in range(len(t)) if t[i].good][0]
        return idx, t[idx]

    def getGoodInnerTriangle(self):
        """Return the first inner triangle object that is good.

        Note: the name indicates it returns a triangle object.
        """
        return [i for i in self.inner_triangles if i.good][0]

    def __str__(self):
        return ", ".join(list(map(str, self.corners)))
        #return "Triangle\n========\n" + "\n".join(list(map(str, self.corners))) + "\n======="

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    # Build the outer simplex corners (extreme price splits)
    initial_triangle = Triangle(Point(0, 0, total_rent),
                                Point(0, total_rent, 0),
                                Point(total_rent, 0, 0), True)

    i = 1
    last_bary = initial_triangle.barycentre_pt

    try:
        idx, tri = initial_triangle.getGoodInnerTriangleIndex()
        print(f"Good Triangle at index {idx} with corners {tri.corners}")
    except Exception:
        print("No good inner triangle found in initial subdivision")

    def debug(t):
        for ii, tt in enumerate(t.inner_triangles):
            print('inner triangle', ii, 'corners=', tt.corners,
                  'label=', tt.corner_label, 'choices=', tt.choices)

    # Iteratively follow a good inner triangle into its subdivision until
    # the barycentre stabilizes or we hit a max iteration count.
    max_iter = 1000
    while True:
        try:
            # Move into the first found good inner triangle
            initial_triangle = initial_triangle.getGoodInnerTriangle()
            initial_triangle.initInnerTriangles()
            new_bary = initial_triangle.barycentre_pt

            debug(initial_triangle)
            print(f"Try {i} into {initial_triangle.barycentre_pt} with label "
                  f"{initial_triangle.corner_label} => {initial_triangle.choices}")

            print(initial_triangle)
            print("Good Triangle", initial_triangle.getGoodInnerTriangleIndex())
            i += 1
            if new_bary == last_bary or i > max_iter:
                break
            last_bary = new_bary
        except Exception as e:
            # Print exception text (use str(e) for Python3 compatibility)
            print(str(e))
            break

