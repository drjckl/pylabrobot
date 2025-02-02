""" Tests for Resource """
# pylint: disable=missing-class-docstring

import unittest

from .coordinate import Coordinate
from .deck import Deck
from .resource import Resource


class TestResource(unittest.TestCase):
  def test_get_resource(self):
    deck = Deck()
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))
    child = Resource("child", size_x=5, size_y=5, size_z=5)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))

    self.assertEqual(deck.get_resource("parent"), parent)
    self.assertEqual(deck.get_resource("child"), child)

    with self.assertRaises(ValueError):
      deck.get_resource("not_a_resource")

  def test_assign_in_order(self):
    deck = Deck()
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))
    child = Resource("child", size_x=10, size_y=10, size_z=10)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))

    self.assertEqual(deck.get_resource("parent"), parent)
    self.assertEqual(deck.get_resource("child"), child)
    self.assertEqual(child.parent, parent)
    self.assertEqual(parent.parent, deck)
    self.assertIsNone(deck.parent)

  def test_assign_build_carrier_first(self):
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    child = Resource("child", size_x=5, size_y=5, size_z=5)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))

    deck = Deck()
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))

    self.assertEqual(deck.get_resource("parent"), parent)
    self.assertEqual(deck.get_resource("child"), child)
    self.assertEqual(child.parent, parent)
    self.assertEqual(parent.parent, deck)
    self.assertIsNone(deck.parent)

  def test_assign_name_taken(self):
    deck = Deck()
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))
    child = Resource("child", size_x=5, size_y=5, size_z=5)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))

    with self.assertRaises(ValueError):
      other_child = Resource("child", size_x=5, size_y=5, size_z=5)
      deck.assign_child_resource(other_child, location=Coordinate(5, 5, 5))

  def test_absolute_location(self):
    deck = Deck()
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))
    child = Resource("child", size_x=5, size_y=5, size_z=5)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))

    self.assertEqual(deck.get_resource("parent").get_absolute_location(), Coordinate(10, 10, 10))
    self.assertEqual(deck.get_resource("child").get_absolute_location(), Coordinate(15, 15, 15))

  def test_unassign_child(self):
    deck = Deck()
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))
    child = Resource("child", size_x=5, size_y=5, size_z=5)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))
    parent.unassign_child_resource(child)

    self.assertIsNone(child.parent)
    with self.assertRaises(ValueError):
      deck.get_resource("child")
    with self.assertRaises(ValueError):
      parent.get_resource("child")

  def test_get_all_children(self):
    deck = Deck()
    parent = Resource("parent", size_x=10, size_y=10, size_z=10)
    deck.assign_child_resource(parent, location=Coordinate(10, 10, 10))
    child = Resource("child", size_x=5, size_y=5, size_z=5)
    parent.assign_child_resource(child, location=Coordinate(5, 5, 5))

    self.assertEqual(deck.get_all_children(), [parent, child])

  def test_eq(self):
    deck1 = Deck()
    deck2 = Deck()
    self.assertEqual(deck1, deck2)

    parent1 = Resource("parent", size_x=10, size_y=10, size_z=10)
    parent2 = Resource("parent", size_x=10, size_y=10, size_z=10)
    self.assertEqual(parent1, parent2)

    child1 = Resource("child", size_x=5, size_y=5, size_z=5)
    child2 = Resource("child", size_x=5, size_y=5, size_z=5)
    self.assertEqual(child1, child2)

  def test_serialize(self):
    r = Resource("test", size_x=10, size_y=10, size_z=10)
    self.assertEqual(r.serialize(), {
      "name": "test",
      "location": None,
      "size_x": 10,
      "size_y": 10,
      "size_z": 10,
      "type": "Resource",
      "children": [],
      "category": None,
      "parent_name": None,
      "model": None,
    })

  def test_deserialize(self):
    r = Resource("test", size_x=10, size_y=10, size_z=10)
    self.assertEqual(Resource.deserialize(r.serialize()), r)

  def test_deserialize_location_none(self):
    r = Resource("test", size_x=10, size_y=10, size_z=10)
    c = Resource("child", size_x=1, size_y=1, size_z=1)
    r.assign_child_resource(c, location=None)
    self.assertEqual(Resource.deserialize(r.serialize()), r)

  def test_get_center_offsets(self):
    r = Resource("test", size_x=10, size_y=120, size_z=10)
    self.assertEqual(r.get_2d_center_offsets(), [Coordinate(5, 60, 0)])
    self.assertEqual(r.get_2d_center_offsets(n=2), [Coordinate(5, 40, 0), Coordinate(5, 80, 0)])

  def test_rotation90(self):
    r = Resource("parent", size_x=200, size_y=100, size_z=100)
    r.location = Coordinate.zero()
    c = Resource("child", size_x=10, size_y=20, size_z=10)
    r.assign_child_resource(c, location=Coordinate(20, 10, 10))

    r.rotate(90)
    self.assertEqual(r.get_size_x(), 100)
    self.assertEqual(r.get_size_y(), 200)
    self.assertEqual(c.get_absolute_location(), Coordinate(70, 20, 10))
    self.assertEqual(c.get_size_x(), 20)
    self.assertEqual(c.get_size_y(), 10)

  def test_rotation180(self):
    r = Resource("parent", size_x=200, size_y=100, size_z=100)
    r.location = Coordinate.zero()
    c = Resource("child", size_x=10, size_y=20, size_z=10)
    r.assign_child_resource(c, location=Coordinate(20, 10, 10))

    r.rotate(180)
    self.assertEqual(r.get_size_x(), 200)
    self.assertEqual(r.get_size_y(), 100)
    self.assertEqual(c.get_absolute_location(), Coordinate(170, 70, 10))
    self.assertEqual(c.get_size_x(), 10)
    self.assertEqual(c.get_size_y(), 20)

  def test_rotation270(self):
    r = Resource("parent", size_x=200, size_y=100, size_z=100)
    r.location = Coordinate.zero()
    c = Resource("child", size_x=10, size_y=20, size_z=10)
    r.assign_child_resource(c, location=Coordinate(20, 10, 10))

    r.rotate(270)
    self.assertEqual(r.get_size_x(), 100)
    self.assertEqual(r.get_size_y(), 200)
    self.assertEqual(c.get_absolute_location(), Coordinate(10, 170, 10))
    self.assertEqual(c.get_size_x(), 20)
    self.assertEqual(c.get_size_y(), 10)

  def test_rotation_invalid(self):
    r = Resource("parent", size_x=200, size_y=100, size_z=100)

    with self.assertRaises(ValueError):
      r.rotate(45)

    with self.assertRaises(ValueError):
      r.rotate(360)

    with self.assertRaises(ValueError):
      r.rotate(0)

  def test_multiple_rotations(self):
    r = Resource("parent", size_x=200, size_y=100, size_z=100)
    r.location = Coordinate.zero()
    c = Resource("child", size_x=10, size_y=20, size_z=10)
    r.assign_child_resource(c, location=Coordinate(20, 10, 10))

    r.rotate(90)
    r.rotate(90) # 180
    self.assertEqual(r.get_size_x(), 200)
    self.assertEqual(r.get_size_y(), 100)
    self.assertEqual(c.get_absolute_location(), Coordinate(170, 70, 10))

    r.rotate(90) # 270
    self.assertEqual(r.get_size_x(), 100)
    self.assertEqual(r.get_size_y(), 200)
    self.assertEqual(c.get_absolute_location(), Coordinate(10, 170, 10))

    r.rotate(90) # 0
    self.assertEqual(r.get_size_x(), 200)
    self.assertEqual(r.get_size_y(), 100)
    self.assertEqual(c.get_absolute_location(), Coordinate(20, 10, 10))
