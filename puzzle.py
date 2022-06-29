from PIL import Image
from collections import deque
from time import time

class Puzzle:
	#start_points format: list of (r1, c1, r2, c2, hex code)
	def __init__(self, rows, cols, start_points):
		self.ROWS = rows
		self.COLS = cols
		self.flows = []
		self.starts = []
		self.ends = []
		self.colors = []
		for (r1, c1, r2, c2, color) in start_points:
			self.starts.append(self.bitmap(r1, c1))	#we can get these from flows, but this is more readable
			self.ends.append(self.bitmap(r2, c2))
			self.flows.append(self.bitmap(r1, c1) | self.bitmap(r2, c2))
			self.colors.append(color)
		self.connections = {self.bitmap(r, c):self.__gen_connections(r, c) for r in range(self.ROWS) for c in range(self.COLS)}

	def __gen_connections(self, r, c):	#returns each of up, down, left, and right if it exists.  Used in initialization
		return {self.bitmap(r+dr, c+dc) for (dr,dc) in ((-1,0), (1,0), (0,-1), (0,1))
			if (dr+r>-1 and dc+c>-1 and dr+r<self.ROWS and dc+c<self.COLS)}

	def add_warp(self, r1, c1, r2, c2):
		self.connections[self.bitmap(r1, c1)].add(self.bitmap(r2, c2))
		self.connections[self.bitmap(r2, c2)].add(self.bitmap(r1, c1))
		return self

	def bitmap(self, r, c):
		return 1<<(r*self.COLS + c)
	def color(self, bitmap):	#returns the color for a given bitmap square for drawing
		for i in range(len(self.flows)):
			if bitmap & self.flows[i]:
				return self.colors[i]
		return (0, 0, 0)

	def solve(self, level=0):
		init_flow = self.flows[level]
		filled = sum(self.flows)
		queue = deque([(self.starts[level], self.starts[level])])
		visited = {self.starts[level]}
		
		self.flows[level] = self.__next_path(level, filled, queue, visited)
		while self.flows[level] is not None:
			if level == len(self.flows)-1 or self.solve(level+1):
				return True
			self.flows[level] = self.__next_path(level, filled, queue, visited)
		#no solution here, reset and backtrack:
		self.flows[level] = init_flow
		return False

	def __next_path(self, flow_index, filled, queue, visited, exist_only=False):
		#exist_only is used when we're seeing if a connection is still possible
		while queue:
			square, path = queue.popleft()
			#if we're searching for a useable path and have cut off another flow, stop searching here:
			if not exist_only and not all(self.__next_path(i, filled|path, deque([(self.starts[i], self.starts[i])]), {self.starts[i]}, True) for i in range(flow_index+1, len(self.flows))):
				continue
			for neighbor in self.connections[square]:
				if neighbor == self.ends[flow_index]:
					return neighbor | path
				elif (neighbor & (filled|path))==0 and not (neighbor|path) in visited:
					queue.append((neighbor, neighbor|path))
					visited.add(neighbor|path)
		return None

	def save(self, filename):
		img = Image.new(mode="RGB", size=(25*self.COLS, 25*self.ROWS), color=(192, 192, 192))
		pixels = img.load()
		for r in range(self.ROWS):
			for c in range(self.COLS):
				color = self.color(self.bitmap(r, c))	#gets the color based on what flow is there
				#color a 22x22 square (leaving 3 pixels for border) that color:
				for i in range(22):
					for j in range(22):
						pixels[25*c+j, 25*r+i] = color
		img.save(filename)

#colors:
BLUE = (0,0,255)
BROWN = (205,133,63)
DARK_RED = (139,0,0)
GRAY = (128,128,128)
GREEN = (0,139,0)
LIGHT_BLUE = (135,206,250)
LIME = (0, 255, 0)
ORANGE = (255,165,0)
PINK = (255,0,255)
PURPLE = (128,0,128)
RED = (255,0,0)
WHITE = (255, 255, 255)
YELLOW = (255,255,0)

def main():
	p = Puzzle(5, 5, [
		(0,0,2,2,BLUE),
		(1,0,4,3,GREEN),
		(3,0,1,4,YELLOW),
		(2,1,1,3,RED)
	]).add_warp(1,0,1,4).add_warp(2,0,2,4).add_warp(3,0,3,4).add_warp(0,1,4,1).add_warp(0,2,4,2).add_warp(0,3,4,3)

	p.save("puzzle.png")
	t = time()
	print(p.solve())
	print(time()-t)
	p.save("solution.png")

if __name__ == "__main__":
	main()
