#!/usr/bin/env python3

import xml.dom.minidom
import xml.dom


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
    Remove a specific DAP Attribute element by name and type.

    :param root: The DOM tree root
    :param attr_name: The name of the attribute to remove
    :param attr_type: The type of the attribute to remove
    :returns: Nothing; the DOM tree is modified
    """
    for element in root.getElementsByTagName("Attribute"):
        if element.getAttribute("name") == attr_name and element.getAttribute("type") == attr_type:
            element.parentNode.removeChild(element)


def get_builder_version(root):
    """
    Remove a specific attribute by name and type."build_dmrpp", "build_dmrpp_metadata"

    :param root: The DOM tree root
    :returns: The version of the DMR++ builder that made this document, as a string
    :rtype: string
    """
    for element in root.getElementsByTagName("Attribute"):
        if element.getAttribute("name") == "build_dmrpp_metadata":
            for attr in element.getElementsByTagName("Attribute"):
                if attr.getAttribute("name") == "build_dmrpp":
                    value = attr.getElementsByTagName("Value")
                    if len(value) and value[0].firstChild.nodeType == xml.dom.minidom.Node.TEXT_NODE:
                        return value[0].firstChild.data
                    else:
                        raise Exception("Expected a single Value element, but found many.")


def remove_elements_by_name(root, elem_name):
    """
    Remove all the elements named 'Attribute'

    :param root: The root of the DOM tree
    :param elem_name: The name of the element(s) to remove
    :returns: Nothing; the DOM tree is modified
    """
    for element in root.getElementsByTagName(elem_name):
        cleanup_extra_spaces(element)
        element.parentNode.removeChild(element)


def clean_chunk_elements(root):
    """
    Remove each <chunk> element.

    Note: This used to remove only two attributes but there is a case where
    different granules can have a different number of chunks for the same
    variable. This happens when the values differ and the variable uses HDF5
    fill values. In that case, chunks in one file that have only fill values
    will not be written to disk. In a different file with different values,
    if those same chunks don't contain only fill values, they will be written
    to disk. Thus, the number of chunk elements may differ.

    :param: root: The root of the DMR++ XML document
    :returns: Nothing; the DOM tree is modified
    """
    for element in root.getElementsByTagName("dmrpp:chunk"):
        cleanup_extra_spaces(element)
        element.parentNode.removeChild(element)


def clean_element_except(root, elem_name, attrs_to_keep):
    """
    FIXME rewrite comment
    For the <Dataset> element, remove all the attributes except the ones in 'attrs_to_keep.'

    :param: root: The root of the DMR++ XML document
    :param: elem_name: The name of element to clean. Cleans all that match
    :param: attrs_to_keep: A List/Tuple of attributes (i.e., their names) to keep
    :returns: Nothing; the DOM tree is modified
    """
    for dataset in root.getElementsByTagName(elem_name):
        named_node_map = dataset.attributes
        for attr in named_node_map.items():
            if attr[0] not in attrs_to_keep:
                dataset.removeAttribute(attr[0])


def clean_element(root, elem_name, attrs_to_remove):
    """
    For the <Dataset> element, remove all the attributes in the List/Tuple 'attrs_to_remove.'

    :param: root: The root of the DMR++ XML document
    :param: elem_name: The name of element to clean. Cleans all that match
    :param: attrs_to_remove: A List/Tuple of attributes (i.e., their names) to remove
    :returns: Nothing; the DOM tree is modified
    """
    for dataset in root.getElementsByTagName(elem_name):
        named_node_map = dataset.attributes
        for attr in named_node_map.items():
            if attr[0] in attrs_to_remove:
                dataset.removeAttribute(attr[0])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build the invariant DMR++ using a complete DMR++")
    parser.add_argument("-d", "--dimensions", help="Some collections (e.g., level 1 and 2 data) have varying dimension "
                                                   "sizes. This option removes the 'size' attribute from the invariant "
                                                   "and the 'chunkDimensionSize' element.", action="store_true")

    parser.add_argument("-v", "--version", help="Instead of building the invariant, extract the DMR++ builder version",
                        action="store_true")
    parser.add_argument("-l", "--list", help="Instead of building the invariant, extract the DMR++ builder version. "
                                             "Unlike --version/-v, return a list of the four version numbers.",
                        action="store_true")
    parser.add_argument("dmrpp_document", help="Build the DMR++ invariant from this DMR++ document ")

    args = parser.parse_args()

    with open(args.dmrpp_document) as dmrpp:
        root = xml.dom.minidom.parse(dmrpp)
        if args.version:
            print(f'DMR++ Builder Version: {get_builder_version(root)}')
        elif args.list:
            for number in get_builder_version(root).replace("-", ".").split("."):
                print(number, end=" ")
            print('')
        else:
            remove_elements_by_name(root, "Attribute")
            remove_elements_by_name(root, "dmrpp:chunk")
            clean_element_except(root, "Dataset", ("xmlns", "xmlns:dmrpp"))
            if args.dimensions:
                remove_elements_by_name(root, "dmrpp:chunkDimensionSizes")
                clean_element(root, "Dimension", ("size"))
            print(root.toxml())


if __name__ == "__main__":
    main()
