# -*- coding: utf-8 -*-
"""
Module contains defination of classes that help convert an xml tree
to python dictionary object

:ref: http://code.activestate.com/recipes/410469-xml-as-dictionary/
"""


class XmlListConfig(list):
    """
    XmlListConfig instantiate a array in xml as a list in python

    Parameters
    ----------
    a_list : :py:obj:`~lxml.etree.Element`
        an xml element containing xml like array of elements

    """

    def __init__(self, a_list):
        super(XmlListConfig, self).__init__()

        for element in a_list:
            if len(element):
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                to_append = None
                text = element.text.strip()

                if element.items():
                    to_append = dict(element.items())
                    if text:
                        to_append.update({'_text': text})
                elif text:
                    to_append = text

                if to_append is not None:
                    self.append(to_append)


class XmlDictConfig(dict):
    """
    XmlDictConfig instantiate a xml tree as dict in python

    Parameters
    ----------
    parent_element : :py:obj:`~lxml.etree.Element`
        parent_element of elements to parse as dictionary


    Warnings
    --------
    - If the parent_element only contains array of same tag elements, then wrap
      the parent element into another element and pass it or otherwise only
      the last value will be returned from the array as others are overwritten.


    Notes
    -----
    - It assumes if first 2 children's tags are different then all are different
      else all are same (in which case it treats the element as list). So an element
      expected to contain only one element will be returned as a `dict`.


    Example
    -------

    >>> import lxml.etree as etree
    >>> tree = etree.parse('sample/sample.tds')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root.find('connection'))

    And then use xmldict for what it is... a dict.
    """

    def __init__(self, parent_element):
        super(XmlDictConfig, self).__init__()

        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if len(element):
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    a_dict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    a_dict = {element[0].tag: XmlListConfig(element)}  # pylint: disable=locally-disabled,R0204
                # if the tag has attributes, add those to the dict
                if element.items():
                    a_dict.update(dict(element.items()))
                self.update({element.tag: a_dict})
            # if you have got an attribute in a tag, text will be inserted
            # in dict with key _text
            elif element.items():
                self.update({element.tag: dict(element.items())})
                if element.text:
                    self[element.tag].update({'_text': element.text})
            # finally, if there are no child tags and no attributes, extract
            # the text directly as value
            else:
                self.update({element.tag: element.text})
