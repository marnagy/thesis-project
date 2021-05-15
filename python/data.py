from typing import Dict, Tuple

class Point:
    """Stores geographical point."""
    lat = 0
    lon = 0

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
    
    def json(self) -> Dict[str, float]:
        """Get JSON representing Point

        :return: JSON of Point object
        :rtype: Dict[str, float]
        """
        return {
            'lat': self.lat,
            'lon': self.lon
        }
    
    def to_tuple(self) -> Tuple[float, float]:
        '''Get Point as Tuple.

        :return: Pair representing Point
        :rtype: Tuple[float, float]
        '''
        return (self.lat, self.lon)

    # @staticmethod
    # def from_json(point_json):
    #     #print("Loading Point from: {}".format(point_json))
    #     return Point(point_json['lat'], point_json['lon'])

    def __str__(self) -> str:
        """Get string representation of Point object.

        :return: representation of Point
        :rtype: str
        """
        return "Lat: {}, Lon: {}".format(self.lat, self.lon)

class Warehouse:
    '''
        Stores warehouse and its information:
        Main point, fitness and routes.
    '''
    point = None
    routes = None
    fitness_time = None
    fitness_distance = None

    def __init__(self, point: Point):
        self.point = point

    def json(self) -> Dict:
        '''Get JSON representing Warehouse

        :return: JSON of Warehouse object
        :rtype: dictionary
        '''
        return {
            'point': self.point.json(),
            'routes': [
                list(map(lambda x: x.json(), route)) for route in self.routes
            ]
        }
    
    def add_route(self, route):
        '''Adds route to Warehouse object

        :param route: route starting and ending in Warehouse.point
        :type route: List of Point
        '''
        if self.routes is None:
            self.routes = [ route ]
        else:
            self.routes.append(route)
    
    def add_fitness(self, fitness_time: float, fitness_distance: float):
        '''Add fitness to object.

        :param fitness: fitness value of current Warehouse object
        :type fitness: float
        '''
        self.fitness_time = fitness_time
        self.fitness_distance = fitness_distance

    # @staticmethod
    # def from_json(wh_json):
    #     #print("Loading JSON from: {}".format(wh_json))
    #     wh = Warehouse(Point.from_json(wh_json['point']))
    #     for route in wh_json['routes']:
    #         #print("Loading route from: {}".format(route))
    #         r = list(map(lambda x: Point.from_json(x), route))
    #         wh.add_route(r)
    #     return wh

    def __str__(self) -> str:
        '''Get string representation of Warehouse object.

        :return: representation of Warehouse
        :rtype: str
        '''
        res = """Warehouse:
        Point: {}
        Routes:\n""".format(self.point)
        for route in self.routes:
            r = "["
            for i in range(len(route)):
                point = route[i]
                if i > 0:
                    r += ", "
                r += str(point)
            r += "]"
            res += r + '\n'
        return res