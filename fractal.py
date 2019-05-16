#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fractal.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""
from __future__ import absolute_import, division, print_function

import random
from collections import namedtuple, defaultdict

from . import tools

P = Point = namedtuple('Point', 'x y')


####################### FRACTAL GEN DATA #######################
class BaseFractalGenerator(object):
    def __init__(self, size, chaos, seed=None, wraped=True, island=False):
        self.size = size
        self.chaos = chaos
        self.seed = seed if seed is not None else tools.make_seed()
        self.wraped = wraped
        self.island = island

        # prepare placeholders for statistics data
        self.mean = None
        self.stdev = None

        # random generator
        self._randgen = random.Random(seed)

        # grain generation
        class LazyGrainDict(dict):
            _randgen = self._randgen
            make_grain = lambda self: self._randgen.randint(-100, 100)
            #make_grain = lambda self : int(self._randgen.gauss(0,1)*100)
            middle_grain = make_grain
            border_grain = lambda self: self._randgen.randint(-100, -50)

            def __missing__(self, key):
                return self.make_grain()

        # grain data
        self._grain = LazyGrainDict()

        # fractal data
        self._data = defaultdict(int)

    def get_value(self, xy):
        return self._data[(xy[0], xy[1])]

    def statistics(self):
        if self.mean is None or self.stdev is None:
            self.mean = 0.0
            self.stdev = 0.0
            for field in self._point_iterator():
                self.mean += self._data[field]
            self.mean /= len(self._data)

            for field in self._point_iterator():
                self.stdev += (self._data[field] - self.mean) ** 2
            self.stdev /= len(self._data)
            self.stdev = self.stdev ** 0.5

        return {'mean': self.mean,
                'stdev': self.stdev,
                'chaos': self.chaos,
                'seed': self.seed,
                }

    def reset_statistics(self):
        self.mean = None
        self.stdev = None

    def transform(self, new_mean, new_stdev):
        """
        Apply linear transform to fractal data that will set new mean and stdev
        """
        # ensure statistics are ready
        self.statistics()
        if self.stdev:  # avoid DivideByZero
            ratio = float(new_stdev) / self.stdev
            for field in self._point_iterator():
                self._data[field] = (((self._data[field] - self.mean) * ratio)
                                     + new_mean)
        self.reset_statistics()

    def linear_transform(self, multipier, shift):
        """
        Apply linear transform to fractal data
        """
        for field in self._point_iterator():
            self._data[field] = self._data[field] * multipier + shift
        if self.mean is not None and self.stdev is not None:
            self.mean = self.mean * multipier + shift
            self.stdev *= multipier * multipier

    def power_transform(self, power, point_one=1,
                        calculate_positives=True,
                        calculate_negatives=False):
        """
        Apply power function transformation to fractal data
        point_one specifies which value should be treated as argument=1
        for the power function
        """
        point_one = float(point_one)
        for field in self._point_iterator():
            if calculate_positives and self._data[field] > 0:
                self._data[field] = (((self._data[field] / point_one)
                                      ** power) * point_one)
            elif calculate_negatives and self._data[field] < 0:
                self._data[field] = (-((-self._data[field] / point_one)
                                       ** power) * point_one)
        self.reset_statistics()


class HexFractalGenerator(BaseFractalGenerator):
    def __init__(self, size, chaos, seed=None, wraped=True, island=False):
        super(HexFractalGenerator, self).__init__(size, chaos,
                                                  seed, wraped, island)

        width = 2 ** size + 1
        last = width - 1
        edge = int((width + 1) / 2)

        if island:
            self._grain[P(last // 2, last // 2)] = self._grain.middle_grain()
            for i in range(edge):
                self._grain[P(i, 0)] = self._grain.border_grain()
                self._grain[P(0, i)] = self._grain.border_grain()
                self._grain[P(last - i, last)] = self._grain.border_grain()
                self._grain[P(last, last - i)] = self._grain.border_grain()
                self._grain[P(edge - 1 + i, i)] = self._grain.border_grain()
                self._grain[P(i, edge - 1 + i)] = self._grain.border_grain()

        corners_and_middle = (P(0, 0),
                              P(edge - 1, 0),
                              P(0, edge - 1),
                              P(last, last),
                              P(edge - 1, last),
                              P(last, edge - 1),
                              P(edge - 1, edge - 1))
        for point in corners_and_middle:
            self._data[point] = self._grain[point]

        # generate fractal
        self._generate()

    def _point_iterator(self):
        return list(self._data.keys())

    def _generate(self):
        ratio = 2. ** (-self.chaos)
        positive_directions = (P(1, 0), P(0, 1), P(1, 1))
        # directions to neighbouring hexes
        hex_neighbours = {P(1, 0): (P(0, -1), P(1, 1)),
                          P(0, 1): (P(1, 1), P(-1, 0)),
                          P(1, 1): (P(1, 0), P(0, 1))}
        # we do calculation as if size was 2 times lower
        # to enable hex shaped board
        size = self.size - 1
        width = 2 ** size + 1
        for step in range(size):
            factor = ratio ** step
            edge_size = (width - 1) // (2 ** step)
            for point in self._point_iterator():
                for direction in positive_directions:
                    second = P(point.x + direction.x * edge_size,
                               point.y + direction.y * edge_size)
                    if second in self._data:
                        new_point = P(point.x + direction.x * edge_size // 2,
                                      point.y + direction.y * edge_size // 2)
                        # add to data
                        # point and second have double weight
                        # because of hex shape from triangles
                        vertices = 4
                        value = (self._data[point] + self._data[second]) * 2
                        # check neighbours for average value
                        for neighbour in hex_neighbours:
                            neigh_point = P(point.x + neighbour.x
                                            * edge_size // 2,
                                            point.y + neighbour.y
                                            * edge_size // 2)
                            if neigh_point in self._data:
                                value += self._data[neigh_point]
                                vertices += 1
                        self._data[new_point] = ((value / vertices)
                                                 + (self._grain[new_point]
                                                    * factor))


class SquareDiamondFractalGenerator(BaseFractalGenerator):
    def __init__(self, size, chaos, seed=None, wraped=True, island=False):
        super(SquareDiamondFractalGenerator, self).__init__(size, chaos,
                                                            seed, wraped,
                                                            island)

        # setting initial numbers in island mode
        if island:
            width = 2 ** size + 1
            middle = 2 ** (size - 1)
            self._grain[P(middle, middle)] = self._grain.middle_grain()
            for i in range(width):
                self._grain[P(i, width - 1)] = self._grain.border_grain()
                self._grain[P(width - 1, i)] = self._grain.border_grain()
                self._grain[P(i, 0)] = self._grain.border_grain()
                self._grain[P(0, i)] = self._grain.border_grain()

        # generate fractal
        self._generate()

    def _point_iterator(self):
        """
        Iterator over every field in fractal
        """
        width = 2 ** self.size + 1
        for x in range(width):
            for y in range(width):
                yield P(x, y)

    def _avg_diamond_vals(self, i, j, stride, sub_size):
        """
        Given the i,j location as the center of a diamond,
        average the data values at the four corners of the diamond and
        return it. "Stride" represents the distance from the diamond center
        to a diamond corner.

        Called by fill2DFractArray.

        In this diagram, our input stride is 1, the i,j location is
        indicated by "X", and the four value we want to average are
        "*"s:
              .   *   .

              *   X   *

              .   *   .

        In order to support tiled surfaces which meet seamless at the
        edges (that is, they "wrap"), We need to be careful how we
        calculate averages when the i,j diamond center lies on an edge
        of the array. The first four 'if' clauses handle these
        cases. The final 'else' clause handles the general case (in
        which i,j is not on an edge).
        """
        width = 2 ** self.size + 1
        if i == 0:
            return (self._data[P(i, j - stride)]
                    + self._data[P(i, j + stride)]
                    + self._data[P(sub_size - stride, j)]
                    + self._data[P(i + stride, j)]) // 4
        elif i == width - 1:
            return (self._data[P(i, j - stride)]
                    + self._data[P(i, j + stride)]
                    + self._data[P(i - stride, j)]
                    + self._data[P(0 + stride, j)]) // 4
        elif j == 0:
            return (self._data[P(i - stride, j)]
                    + self._data[P(i + stride, j)]
                    + self._data[P(i, j + stride)]
                    + self._data[P(i, sub_size - stride)]) // 4
        elif j == width - 1:
            return (self._data[P(i - stride, j)]
                    + self._data[P(i + stride, j)]
                    + self._data[P(i, j - stride)]
                    + self._data[P(i, 0 + stride)]) // 4
        else:
            return (self._data[P(i - stride, j)]
                    + self._data[P(i + stride, j)]
                    + self._data[P(i, j - stride)]
                    + self._data[P(i, j + stride)]) // 4

    def _avg_square_vals(self, i, j, stride):
        """
         Given the i,j location as the center of a square,
         average the data values at the four corners of the square and return
         it. "Stride" represents half the length of one side of the square.

         Called by fill2DFractArray.

         In this diagram, our input stride is 1, the i,j location is
               indicated by "*", and the four value we want to average are
               "X"s:
           X   .   X

           .   *   .

           X   .   X
         """
        return (self._data[P(i - stride, j - stride)]
                + self._data[P(i - stride, j + stride)]
                + self._data[P(i + stride, j - stride)]
                + self._data[P(i + stride, j + stride)]) // 4

    def _generate(self):
        """
         Use the diamond-square algorithm to tessalate a
         grid of float values into a fractal height map.
         """
        #subSize is the dimension of the array in terms of connected line
        #segments, while size is the dimension in terms of number of
        #vertices.

        width = 2 ** self.size + 1
        sub_size = width - 1

        #Set up our roughness constants.
        #Random numbers are always generated in the range 0.0 to 1.0.
        #'scale' is multiplied by the randum number.
        #'ratio' is multiplied by 'scale' after each iteration
        #to effectively reduce the random number range.

        ratio = 2. ** (-self.chaos)
        scale = 1000

        # Seed the first four values. For example, in a 4x4 array, we
        # would initialize the data points indicated by '*':
        #
        #   *   .   .   .   *
        #
        #   .   .   .   .   .
        #
        #   .   .   .   .   .
        #
        #   .   .   .   .   .
        #
        #   *   .   .   .   *
        #
        # In terms of the "diamond-square" algorithm, this gives us
        #   "squares".
        #
        # We want the four corners of the array to have the same
        # point. This will allow us to tile the arrays next to each other
        # such that they join seemlessly.
        stride = sub_size // 2
        # Now we add ever-increasing detail based on the "diamond" seeded
        # values. We loop over stride, which gets cut in half at the
        # bottom of the loop. Since it's an int, eventually division by 2
        # will produce a zero result, terminating the loop.

        while stride:
            # Take the existing "square" data and produce "diamond"
            # data. On the first pass through with a 4x4 matrix, the
            # existing data is shown as "X"s, and we need to generate the
            # "*" now:
            #
            #       X   .   .   .   X
            #
            #       .   .   .   .   .
            #
            #       .   .   *   .   .
            #
            #       .   .   .   .   .
            #
            #       X   .   .   .   X
            #
            # It doesn't look like diamonds. What it actually is, for the
            # first pass, is the corners of four diamonds meeting at the
            # center of the array.
            scale = int(scale * ratio)
            i = stride
            while i < sub_size:
                j = stride
                while j < sub_size:
                    #self._avgSquareVals (i, j, stride)
                    self._data[P(i, j)] = (
                        scale * self._grain[P(i, j)]
                        + self._avg_square_vals(i, j, stride)
                    )
                    j += 2 * stride
                i += 2 * stride
            # Take the existing "diamond" data and make it into
            # "squares". Back to our 4X4 example: The first time we
            # encounter this code, the existing values are represented by
            # "X"s, and the values we want to generate here are "*"s:
            #
            #   X   .   *   .   X
            #
            #   .   .   .   .   .
            #
            #   *   .   X   .   *
            #
            #   .   .   .   .   .
            #
            #   X   .   *   .   X
            #
            # i and j represent our (x,y) position in the array. The
            # first value we want to generate is at (i=2,j=0), and we use
            # "oddline" and "stride" to increment j to the desired value.
            oddline = False
            i = 0
            while i < sub_size:
                oddline = not oddline
                j = 0
                while j < sub_size:
                    if oddline and j == 0:
                        j += stride
                    # i and j are setup. Call avgDiamondVals with the
                    # current position. It will return the average of the
                    # surrounding diamond data points.
                    #self._avgDiamondVals (i, j, stride, subSize)
                    self._data[P(i, j)] = scale * self._grain[P(i, j)]
                    self._data[P(i, j)] += self._avg_diamond_vals(i, j,
                                                                  stride,
                                                                  sub_size)
                    # To wrap edges seamlessly, copy edge values around
                    # to other side of array
                    if self.wraped:
                        if i == 0:
                            self._data[P(sub_size, j)] = self._data[P(i, j)]
                        if j == 0:
                            self._data[P(i, sub_size)] = self._data[P(i, j)]
                    j += 2 * stride
                i += stride
            stride >>= 1
