#!/usr/bin/env python3

import xml.dom.minidom


def cleanup_extra_spaces(tag):
    """
    Spaces... When removeChild is used to extract nodes from the document,
    it leaves blanks lines. This little function removes those extra lines.

    :param tag: The tag that will be removed and will have its trailing extra
        TEXT_NODE removed
    :returns: Nothing; the dom tree is modified
    """
    if tag.nextSibling and tag.nextSibling.nodeType == xml.dom.minidom.Node.TEXT_NODE and tag.nextSibling.data.isspace():
        tag.parentNode.removeChild(tag.nextSibling)


def remove_attribute(root, attr_name, attr_type):
    """
    Remove a specific attribute by name and type.

    :param root: The DOM tree root
    :param attr_name: The name of the attribute to remove
    :param attr_type: The type of the attribute to remove
    :returns: Nothing; the DOM tree is modified
    """
    for element in root.getElementsByTagName("Attribute"):
        if element.getAttribute("name") == attr_name and element.getAttribute("type") == attr_type:
            element.parentNode.removeChild(element)


def remove_all_attributes(root):
    """
    Remove all the elements named 'Attribute'

    :param root: The root of the DOM tree
    :returns: Nothing; the DOM tree is modified
    """
    for element in root.getElementsByTagName("Attribute"):
        cleanup_extra_spaces(element)
        element.parentNode.removeChild(element)


def clean_chunk_element(element):
    """
    for a given <chunk> element, remove the 'offset' and 'nbytes' attribute values.

    :param: element: An XML element from the DMR++ document
    :returns: None; the element value is modified
    """
    element.removeAttribute("offset")
    element.removeAttribute("nBytes")


def clean_chunk_elements(root):
    """
    For each <chunk> element, remove the 'offset' and 'nbytes' attribute values.

    :param: root: The root of the DMR++ XML document
    :returns: Nothing; the DOM tree is modified
    """
    for element in root.getElementsByTagName("dmrpp:chunk"):
        clean_chunk_element(element)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("dmrpp_document", help="Build the DMR++ invariant from this DMR++ document ")

    args = parser.parse_args()

    # 19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1.nc.dmrpp
    with open(args.dmrpp_document) as dmrpp:
        root = xml.dom.minidom.parse(dmrpp)
        remove_all_attributes(root)
        clean_chunk_elements(root)
        print(root.toxml())


if __name__ == "__main__":
    main()
