.. AutoExtract documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:04:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AutoExtract's documentation!
=======================================

Contents:

.. toctree::
   :maxdepth: 2

   modules

.. py:exception:: IOError

   Raised when an I/O operation fails for an I/O-related reason, e.g., “file not found” or “disk full”.


.. py:module:: tableausdk.Extract

.. py:class:: TableauDefinition

   Represents the schema for a table in a Tableau data extract.


.. py:module:: tableausdk.Exceptions

.. py:exception:: TableauException

   Inherits Exception.


.. py:module:: lxml.etree

.. py:class:: Element(_tag, attrib=None, nsmap=None, **_extra)

   Element class.

.. py:class:: XPath(path, namespaces=None, extensions=None, regexp=True, smart_strings=True)

   A compiled XPath expression that can be called on Elements and ElementTrees.

.. py:class:: XMLParser(encoding=None, attribute_defaults=False, dtd_validation=False, \
                        load_dtd=False, no_network=True, ns_clean=False, recover=False, \
                        schema: XMLSchema =None, remove_blank_text=False, resolve_entities=True, \
                        remove_comments=False, remove_pis=False, strip_cdata=True, collect_ids=True, \
                        target=None, compact=True)

   The XML parser. Parsers can be supplied as additional argument to various parse functions of the lxml API.

.. py:exception:: XMLSchemaParseError

   Error while parsing an XML document as XML Schema.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
