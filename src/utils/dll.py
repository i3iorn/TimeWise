import time
from typing import Any


class Node:
    """
    A node in a doubly-linked list. Each node contains a data element and a timestamp. The timestamp is used to determine
    the age of the cache entry.

    Args:
        data (Any): The data element to store in the node.

    Attributes:
        data (Any): The data element stored in the node.
        prev (Node): The previous node in the list.
        next (Node): The next node in the list.
        timestamp (float): The timestamp when the node

    Example:
        node = Node("foo")
    """
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None
        self.timestamp = time.time()


class DoublyLinkedList:
    """
    A doubly-linked list that stores nodes. The list has a head and a tail. The head is the first node in the list, and
    the tail is the last node in the list.

    Attributes:
        head (Node): The first node in the list.
        tail (Node): The last node in the list.

    Example:
        dll = DoublyLinkedList()
    """
    def __init__(self) -> None:
        self.head = None
        self.tail = None

    def append(self, data: Any) -> None:
        """
        Append a new node to the end of the list.

        :param data: The data element to store in the new node.
        :type data: Any

        :return: None

        Example:
            dll.append("foo")

        """
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            return
        self.tail.next = new_node
        new_node.prev = self.tail
        self.tail = new_node

    def prepend(self, data: Any) -> None:
        """
        Prepend a new node to the beginning of the list.

        :param data: The data element to store in the new node.
        :type data: Any

        :return: None

        Example:
            dll.prepend("foo")
        """
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            return
        self.head.prev = new_node
        new_node.next = self.head
        self.head = new_node

    def delete(self, node: Node) -> None:
        """
        Delete a node from the list.

        :param node: The node to delete.
        :type node: Node

        :return: None

        Example:
            dll.delete(node)

        Example:
            dll = DoublyLinkedList()
            dll.append("foo")
            dll.append("bar")
            dll.append("baz")
            dll.delete(dll.head.next)
        """
        if not self.head:
            return
        if node == self.head:
            self.head = node.next
            if self.head:
                self.head.prev = None
            else:
                self.tail = None
        elif node == self.tail:
            self.tail = node.prev
            if self.tail:
                self.tail.next = None
            else:
                self.head = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

    def print_list_forward(self) -> None:
        """
        Print the list in forward order.

        :return: None

        Example:
            dll.print_list_forward()
        """
        current = self.head
        while current:
            print(current.data, end=" <-> ")
            current = current.next
        print("None")

    def print_list_backward(self) -> None:
        """
        Print the list in backward order.

        :return: None

        Example:
            dll.print_list_backward()
        """
        current = self.tail
        while current:
            print(current.data, end=" <-> ")
            current = current.prev
        print("None")
