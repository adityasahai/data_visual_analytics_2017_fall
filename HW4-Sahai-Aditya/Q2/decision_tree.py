from util import entropy, information_gain, partition_classes, median, mean
import numpy as np 
import ast


class Tree(object):
    def __init__(self, col_number=None, split_value=None, info_gain=None):
        self.attribute_column = col_number
        self.split_val = split_value
        self.info_gain = info_gain
        self.is_leaf = False
        self.left = None
        self.right = None
        self._class_ = None

    def set_class(self, label):
        if self.is_leaf:
            self._class_ = label

    def get_class(self):
        if self.is_leaf:
            return self._class_


class DecisionTree(object):
    def __init__(self):
        # Initializing the tree as an empty dictionary or list, as preferred
        self.tree = None
        self.num_attributes = 0
        self._attr_to_exclude_ = []

    def find_info_gain(self, X, y, attr):
        '''
        Find the information gain for a given attribute
        '''
        # Find out if its a numerical or categorical
        isCategorical = type(X[1][attr]) == str
        if isCategorical:
            value_set = set([x[attr] for x in X])
            if len(value_set) == 1:
                # only one value for entire list
                return None
            elif len(value_set) == 2:
                attribute_values = [list(value_set)[0]]
            else:
                attribute_values = [x for x in value_set]
        else:
            # calculate mean, median of the values
            value_set = set([x[attr] for x in X])
            if len(value_set) == 1:
                return None
            values = [x for x in value_set]
            # calculate info gain on median and mean
            attribute_values = [mean(values), median(values)]
        max_info_gain = 0
        val = None
        X_left = None
        X_right = None
        Y_left = None
        Y_right = None
        for each in attribute_values:
            x_left, x_right, y_left, y_right = partition_classes(X, y, attr, each)
            info_gain = information_gain(y, [y_left, y_right])
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                val = each
                X_left, X_right, Y_left, Y_right = x_left, x_right, y_left, y_right
        return isCategorical, val, max_info_gain, X_left, X_right, Y_left, Y_right

    def find_attr_with_max_gain(self, X, y):
        '''
        Find the attribute which has the maximum gain for the given dataset and labels.
        rtype: int (column number)
        '''
        max_info_gain = 0
        attr_max = None
        attr_val = None
        X_left = None
        X_right = None
        Y_left = None
        Y_right = None
        for attr in range(0, len(X[0])):
            if attr in self._attr_to_exclude_:
                continue
            try:
                isCat, val, info_gain, x_left, x_right, y_left, y_right = self.find_info_gain(X, y, attr)
            except TypeError:
                # this happens when the attribute has only one value
                # we should exclude it
                self._attr_to_exclude_.append(attr)
                continue
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                attr_max = attr
                attr_val = val
                X_left, X_right, Y_left, Y_right = x_left, x_right, y_left, y_right
        return attr_max, attr_val, max_info_gain, X_left, X_right, Y_left, Y_right

    def popular_class(self, y):
        '''
        Calculate the most popular class in y
        :param y:
        :return: 0 or 1
        '''
        size_y = len(y)
        size_1 = sum(y)
        if (size_1) / (size_y * 1.0) > 0.5:
            return 1
        else:
            return 0

    def create_tree(self, X, y):
        '''
        Create and return node for tree
        :param X:
        :param y:
        :return: tree
        '''
        if len(set(y)) == 1:
            tree = Tree()
            tree.is_leaf = True
            tree.set_class(y[0])
            return tree
        else:
            attr_max, attr_val, info_gain, x_left, x_right, y_left, y_right = self.find_attr_with_max_gain(X, y)
            if attr_max:
                self._attr_to_exclude_.append(attr_max)
                tree = Tree(col_number=attr_max, split_value=attr_val, info_gain=info_gain)
                tree.left = self.create_tree(x_left, y_left)
                tree.right = self.create_tree(x_right, y_right)
                return tree
            else:
                tree = Tree()
                tree.is_leaf = True
                tree.set_class(self.popular_class(y))
                return tree

    def learn(self, X, y):
        # You will have to make use of the functions in utils.py to train the tree
        
        # One possible way of implementing the tree:
        #    Each node in self.tree could be in the form of a dictionary:
        #       https://docs.python.org/2/library/stdtypes.html#mapping-types-dict
        #    For example, a non-leaf node with two children can have a 'left' key and  a 
        #    'right' key. You can add more keys which might help in classification
        #    (eg. split attribute and split value)
        self.num_attributes = len(X[0])
        if not self.tree:
            self.tree = self.create_tree(X, y)

    def print_tree(self, tree):
        if tree.is_leaf:
            print "Leaf : " + str(tree.get_class())
        else:
            print "col number : " + str(tree.attribute_column)
            print "info_gain : " + str(tree.info_gain)
            self.print_tree(tree.left)
            self.print_tree(tree.right)

    def parse_tree(self):
        if not self.tree:
            print "Tree not initialized yet!"
        else:
            self.print_tree(self.tree)

    def _classify_(self, record, node):
        if not node.is_leaf:
            isCategorical = type(node.split_val) == str
            if isCategorical:
                if record[node.attribute_column] == node.split_val:
                    return self._classify_(record, node.left)
                else:
                    return self._classify_(record, node.right)
            else:
                if record[node.attribute_column] <= node.split_val:
                    return self._classify_(record, node.left)
                else:
                    return self._classify_(record, node.right)
        else:
            return node.get_class()

    def classify(self, record):
        return self._classify_(record, self.tree)
