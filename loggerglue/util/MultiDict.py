"""Dictionary-like objects which allow multiple keys

Python dictionaries map a key to a value.  Duplicate keys are not
allowed, and new entries replace old ones with the same key.  Order is
not otherwise preserved, so there's no way to get the items in the
order they were added to a dictionary.

Some types of data is best stored in dictionary-like object which
allow multiple values per key.  Some of these need the input order
strongly preserved, so the items can be retrieved in the same order as
they were added to the dictionary.  That is the OrderedMultiDict.

To create a MultiDict, pass in an object which implements the
'allitems' method and returns a list of (key, value) pairs, or
pass in the list of (key, value) pairs directly.

The two MultiDict classes implement the following dictionary methods
  d["lookup"],
  d["key"] = value
  del d[key]
  d.get("key", default = None)
  d1 == d2, d1 != d2, len(d), iter(d), str(d)
  d.keys(), d.values(), d.items()

The new methods are:
  d.getall(key)
  d.allkeys()
  d.allvalues()
  d.allitems()

  >>> import MultiDict
  >>> od = MultiDict.OrderedMultiDict()
  >>> od["Name"] = "Andrew"
  >>> od["Color"] = "BLUE"
  >>> od["Name"] = "Dalke"
  >>> od["Color"] = "Green"
  >>> od[3] = 9
  >>> len(od)
  3
  >>> od["Name"]
  'Dalke'
  >>> od.getall("Name")
  ['Andrew', 'Dalke']
  >>> for k, v in od.allitems():
  ...     print "%r == %r" % (k, v)
  ...
  'Name' == 'Andrew'
  'Color' == 'BLUE'
  'Name' == 'Dalke'
  'Color' == 'Green'
  3 == 9
  >>> del od["Name"]
  >>> len(od)
  2
  >>> for k, v in od.allitems():
  ...     print "%r == %r" % (k, v)
  ...
  'Color' == 'BLUE'
  'Color' == 'Green'
  3 == 9
  >>>

The latest version of this code can be found at
  http://www.dalkescientific.com/Python/
"""
# Written in 2003 by Andrew Dalke, Dalke Scientific Software, LLC.
# This software has been released to the public domain.  No
# copyright is asserted.

from __future__ import generators

# Implementation inheritence -- not asserting a class hierarchy here
#
# If there is a class hierarchy, OrderedMultiDict is a child of
# UnorderedMultiDict because it makes stronger but not different
# guarantees on how the data works, at least data-wise.
# Performance-wise, Ordered has a slower (O(n)) than Unordered (O(1)).
# Convince me otherwise and I'll change.  Besides, hierarchies are
# overrated.
class _BaseMultiDict:
    def __str__(self):
        """shows contents as if this is a dictionary

        If multiple values exist for a given key, use the last
        one added.
        """
        d = {}
        for k in self.data:
            d[k] = self.data[k][-1]
        return str(d)
    def __len__(self):
        """the number of unique keys"""
        return len(self.data)

    def __getitem__(self, key):
        """value for a given key

        If more than one value exists for the key, use one added most recently
        """
        return self.data[key][-1]

    def get(self, key, default = None):
        """value for the given key; default = None if not present

        If more than one value exists for the key, use the one added
        most recently.
        """
        return self.data.get(key, [default])[-1]

    def __contains__(self, key):
        """check if the key exists"""
        return key in self.data

    def keys(self):
        """unordered list of unique keys"""
        return self.data.keys()

    def values(self):
        """unordered list of values

        If more than one value exists for a given key, use the value
        added most recently.
        """
        return [x[-1] for x in self.data.values()]

    def items(self):
        """unordered list of key/value pairs

        If more than one value exists for a given key, use the value
        added most recently.
        """
        return [(k, v[-1]) for k, v in self.data.items()]

    def getall(self, key):
        """Get all values for a given key

        Multiple values are returned in input order.
        If the key does not exists, returns an empty list.
        """
        return self.data[key]

    def __iter__(self):
        """iterate through the list of unique keys"""
        return iter(self.data)


class OrderedMultiDict(_BaseMultiDict):
    """Store key/value mappings.

    Acts like a standard dictionary with the following features:
       - duplicate keys are allowed;

       - input order is preserved for all key/value pairs.

    >>> od = OrderedMultiDict([("Food", "Spam"), ("Color", "Blue"),
    ...                        ("Food", "Eggs"), ("Color", "Green")])
    >>> od["Food"]
    'Eggs'
    >>> od.getall("Food")
    ['Spam', 'Eggs']
    >>> list(od.allkeys())
    ['Food', 'Color', 'Food', 'Color']
    >>>

    The order of keys and values(eg, od.allkeys() and od.allitems())
    preserves input order.

    Can also pass in an object to the constructor which has an
    allitems() method that returns a list of key/value pairs.

    """
    def __init__(self, multidict = None):
        self.data = {}
        self.order_data = []
        if multidict is not None:
            if hasattr(multidict, "allitems"):
                multidict = multidict.allitems()
            elif hasattr(multidict, "items"):
                multidict = multidict.items()
            for k, v in multidict:
                self[k] = v
    def __eq__(self, other):
        """Does this OrderedMultiDict have the same contents and order as another?"""
        return self.order_data == other.order_data
    def __ne__(self, other):
        """Does this OrderedMultiDict have different contents or order as another?"""
        return self.order_data != other.order_data

    def __repr__(self):
        return "<OrderedMultiDict %s>" % (self.order_data,)

    def __setitem__(self, key, value):
        """Add a new key/value pair

        If the key already exists, replaces the existing value
        so that d[key] is the new value and not the old one.

        To get all values for a given key, use d.getall(key).
        """
        self.order_data.append((key, value))
        self.data.setdefault(key, []).append(value)

    def __delitem__(self, key):
        """Remove all values for the given key"""
        del self.data[key]
        self.order_data[:] = [x for x in self.order_data if x[0] != key]

    def allkeys(self):
        """iterate over all keys in input order"""
        for x in self.order_data:
            yield x[0]
    def allvalues(self):
        """iterate over all values in input order"""
        for x in self.order_data:
            yield x[1]
    def allitems(self):
        """iterate over all key/value pairs in input order"""
        return iter(self.order_data)


__test__ = {
    "test_ordered_multidict": """
        >>> od = OrderedMultiDict()
        >>> od["Name"] = "Andrew"
        >>> od["Color"] = "BLUE"
        >>> od["Name"] = "Dalke"
        >>> od["Color"] = "Green"
        >>> od[3] = 9
        >>> len(od)
        3
        >>> len(od.keys())
        3
        >>> len(od.values())
        3
        >>> len(od.items())
        3
        >>> od.keys()
        ['Color', 3, 'Name']
        >>> "Name" in od and "Name" in od.keys() and "Name" in od.allkeys()
        1
        >>> "Color" in od and "Color" in od.keys() and "Color" in od.allkeys()
        1
        >>> 3 in od and 3 in od.keys() and 3 in od.allkeys()
        1
        >>> od == od
        1
        >>> od != OrderedMultiDict()    # line 25
        1
        >>> list(od.allkeys())
        ['Name', 'Color', 'Name', 'Color', 3]
        >>> list(od.allvalues())
        ['Andrew', 'BLUE', 'Dalke', 'Green', 9]
        >>> list(od.allitems())
        [('Name', 'Andrew'), ('Color', 'BLUE'), ('Name', 'Dalke'), ('Color', 'Green'), (3, 9)]
        >>> len(list(od))
        3
        >>> od["invalid"]
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
          File "MultiDict.py", line 33, in __getitem__
            return self.data[key]
        KeyError: invalid
        >>> od["Color"]
        'Green'
        >>> od.getall("Color")
        ['BLUE', 'Green']
        >>> od2 = OrderedMultiDict(od)
        >>> list(od2.allitems())
        [('Name', 'Andrew'), ('Color', 'BLUE'), ('Name', 'Dalke'), ('Color', 'Green'), (3, 9)]
        >>> od == od2
        1
        >>> od2 == od                  # line 53
        1
        >>> od2 != od
        0
        >>> del od["Color"]
        >>> od["Color"]
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
          File "MultiDict.py", line 33, in __getitem__
            return self.data[key]
        KeyError: Color
        >>> list(od.allitems())
        [('Name', 'Andrew'), ('Name', 'Dalke'), (3, 9)]
        >>> list(od2.allkeys())
        ['Name', 'Color', 'Name', 'Color', 3]
        >>> od2["Color"]
        'Green'
        >>> od == od2
        0
        >>>
        >>> s = str(od2)
        >>> s = repr(od2)
    """,
  "__doc__": __doc__,
}

def _test():
    import doctest, MultiDict
    return doctest.testmod(MultiDict)

if __name__ == "__main__":
    _test()

