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
		self.connections = {self.bitmap(r, c):self.gen_connections(r, c) for r in range(self.ROWS) for c in range(self.COLS)}

	def gen_connections(self, r, c):	#returns each of up, down, left, and right if it exists
		return {self.bitmap(r+dr, c+dc) for (dr,dc) in ((-1,0), (1,0), (0,-1), (0,1))
			if (dr+r>-1 and dc+c>-1 and dr+r<self.ROWS and dc+c<self.COLS)}

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
		
		self.flows[level] = self.next_path(level, filled, queue, visited)
		while self.flows[level] is not None:
			if level == len(self.flows)-1 or self.solve(level+1):
				return True
			self.flows[level] = self.next_path(level, filled, queue, visited)
		#no solution here, reset and backtrack:
		self.flows[level] = init_flow
		return False

	def next_path(self, flow_index, filled, queue, visited, exist_only=False):
		#exist_only is used when we're seeing if a connection is still possible
		while queue:
			square, path = queue.popleft()
			#if we're searching for a useable path and have cut off another flow, stop searching here:
			if not exist_only and not all(self.next_path(i, filled|path, deque([(self.starts[i], self.starts[i])]), {self.starts[i]}, True) for i in range(flow_index+1, len(self.flows))):
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
	p = Puzzle(15, 9, [
		(7,1,6,5,WHITE),
		(7,2,13,6,LIGHT_BLUE),
		(9,0,14,7,PINK),
		(10,0,11,1,BROWN),
		(10,1,13,1,LIME),
		(6,8,12,8,BLUE),
		(5,7,3,8,DARK_RED),

		(11,2,9,4,YELLOW),
		(2,2,2,4,GREEN),
		(3,3,1,7,ORANGE),
		(3,4,2,8,GRAY),
		(14,8,2,5,PURPLE),
		(8,2,3,6,RED)
	])
	p.flows[0] |= sum(p.bitmap(6,i) for i in range(1,5))
	p.flows[1] |= sum(p.bitmap(7,i) for i in range(2,6)) | sum(p.bitmap(i,6) for i in range(7,13))
	p.flows[2] |= sum(p.bitmap(9,i) for i in range(1,4)) | sum(p.bitmap(8,i) for i in range(3,6)) | sum(p.bitmap(i,5) for i in range(8,15)) | p.bitmap(14,6)
	p.flows[3] |= p.bitmap(11,0)
	p.flows[4] |= p.bitmap(10,2) | sum(p.bitmap(i,3) for i in range(10,14)) | p.bitmap(13,2)
	p.flows[5] |= sum(p.bitmap(i,8) for i in range(6,12))
	p.flows[6] |= p.bitmap(4,8) | p.bitmap(5,8)

	p.save("puzzle.png")
	t = time()
	print(p.solve(7))
	print(time()-t)
	p.save("solution.png")

if __name__ == "__main__":
	main()