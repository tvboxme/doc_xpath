#!/usr/bin/env python
# encoding: utf-8
# author: 04

import logging

XPATH_EMPTY = object()
XPATH_NO_DEFAULT = object()
logger = logging.getLogger()


class X(object):
    """ doc_xpath_dict_map using object
    receive list of string or single string.
    Will pick the first xpath matched.
    """

    XPATH_NO_DEFAULT = NotImplemented

    def __init__(self, *xpath, default=XPATH_NO_DEFAULT):
        self.xpath_list = list(xpath)
        self.default = default

    def __str__(self):
        default_msg = f"|default:{self.default}" if self.default is not self.XPATH_NO_DEFAULT else ''
        return f"<Xpath {self.xpath_list}{default_msg}>"

    def __or__(self, next_one):
        if not isinstance(next_one, X):
            raise NotImplementedError('Cannot operate with other types.')
        return X(*(self.xpath_list + next_one.xpath_list))


def doc_xpath(doc, xpath, allow_empty=False):
    """
    Xpath for document
    >>> a = {'a': [{'b': {'c': ['d', 'f']}}, {'b': {'c': ['g', 'h']}}]}
    >>> doc_xpath(a, 'a.b.c')
    Traceback (most recent call last):
       ...
    KeyError: "Xpath <a.b.c> failed at <b>.[{'b': {'c': ['d', 'f']}}, {'b': {'c': ['g', 'h']}}]"
    >>> doc_xpath(a, 'a.[].b.c')
    [['d', 'f'], ['g', 'h']]
    >>> doc_xpath(a, 'a.[].b.c.[]')
    ['d', 'f', 'g', 'h']
    """
    check_points = [doc]
    for word in xpath.split('.'):
        new_points = []
        for point in check_points:
            try:
                if word == '[]':
                    if not isinstance(point, list):
                        raise KeyError(f'Xpath <{xpath}> unexpected list word at {point}')
                    new_points.extend(point)
                else:
                    if point.get(word, XPATH_EMPTY) is XPATH_EMPTY:
                        if not allow_empty:
                            raise KeyError(f'Xpath <{xpath}> unexpected empty at {point}')
                        else:
                            continue
                    new_points.append(point[word])
            except Exception as e:
                raise KeyError(f'Xpath <{xpath}> failed at <{word}>.{point}') from e
        check_points = new_points
    return check_points


def doc_xpath_dict_map(doc, xpath_dict, default=X.XPATH_NO_DEFAULT):
    """
    Xpath with dict
    If default is not set, we will raise a KeyError while value can't got.
    Hint: this default is general for whole map.
    >>> a = {'a1': {'b1': {'c1': 'd1'}}, 'a2': {'b3': '3'}}
    >>> test_dict = {'alpha': X('y', 'a1.b1.c1'), 'beta': (X('a1.b3') | X('a2.b3'), int)}
    >>> doc_xpath_dict_map(a, test_dict)
    {'alpha': 'd1', 'beta': 3}
    """
    output = {}
    for key, desc in xpath_dict.items():
        if isinstance(desc, tuple):
            value, func = desc
            if not callable(func):
                raise ValueError('%s must be callable.' % repr(func))
        else:
            value = desc
            func = None
        if isinstance(value, X):
            for doc_path in value.xpath_list:
                try:
                    xpath_value = doc_xpath(doc, doc_path, allow_empty=True)
                except KeyError:
                    logger.info(f'Read {key} from {doc_path} failed.')
                if len(xpath_value) != 0:
                    if len(xpath_value) == 1:
                        xpath_value = xpath_value[0]
                    output[key] = xpath_value
                    break
            else:
                output[key] = value.default if value.default is not X.XPATH_NO_DEFAULT else default
        elif isinstance(value, dict):
            output[key] = doc_xpath_dict_map(doc, value)
        else:
            output[key] = value
        if func and output[key] is not X.XPATH_NO_DEFAULT:
            output[key] = func(output[key])
        if output[key] is X.XPATH_NO_DEFAULT:
            raise KeyError(f"The {value} does not exist at origin data. \n{doc}")
    return output


if __name__ == "__main__":
    import doctest
    doctest.testmod()
