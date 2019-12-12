#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for controlling the GoPiGo3 Motors
#
# Results:  When you run this program, the GoPiGo3 Motors will rotate back and forth.
class LinkedList():
	
	def __init__():

		
		self.head = Node()
		self.tail = head
		self.cur = head
		self.next = self.cur.next
		self.prev =self.head.prev



	def delete():

		if ((self.cur == self.head) & (self.next == True) ):
			self.cur = self.cur.next
			self.head.next = null
			self.head = self.cur
			self.cur.prev = null

		if not(self.cur == self.head):
			self.cur.prev.next= self.cur.next
			self.cur.next.prev = self.cur.prev
			hldr = self.cur.prev
			self.cur.next = null
			self.cur.prev = null
			self.cur = hldr

	def Add():
		toAdd = Node()
		toAdd.prev = self.tail
		self.tail.next = toAdd
		self.tail = toAdd

	def getSize():
		size = 1
		cur = self.head
		while not(cur == null):
			cur = cur.next
			size = size + 1
			
		return size


class Node():

	i = 1
	def __init__():
		self.index = i
		self.next = null
		self.prev = null
		self.angle = 0
		self.dist = 0
		self.vstd = 0
		i = 1 +1




		


