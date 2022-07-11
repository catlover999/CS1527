# This is Assessment 3 for CS1527 as written by 52091278.
# I encourage you run this script with an up to date version of Python 3 in some Unix(-like) terminal.
# This scripted comes with a built in menu that is run when __name__ == "__main__" (aka, it is not being imported).
# Hence, run this script with "python3 expression_tree.py" after renaming "expression_tree.txt" (note, python may be aliased to just "python", validate that you are using Python 3 using "python -V". This script was written using Python 3.9.2)
# You may choice to import the library if you wish, in that case, call the class BinaryTree with the format "tree = BinaryTree(expression)" where "expression" is a string, "tree.printTree()" then can be used to print the generated tree.
# This script requires no external modules or files (only using a few built in modules)
# Tests are run within the main menu. You can load one of 14 expressions, half of which are invalid while the other half are valid.

from re import compile      # Regex is an extremely useful utility. We use it to check for invalid characters and to pull matches out of text.
from json import load, dump # JSON is used to serialize (and unserialize) data
from os import listdir      # Not essential to the main function of the program but it lists the contents of the currently focused directory (equivalent to ls or dir). (This is used to help show available files while loading from file)

class Parser:
    # The parser takes in a string through its parse function. The purpose of this class is to take an input string and generate a nested dictionary of nodes (which parse returns). The other functions are internal, however, Parser can be more easily inherited from if your input data takes a different form as what this assessment prescribes.

    def __init__(self):
        self._data = ""
        self._level = 0
        self._regex = compile("[/*+-]") # This being in the class's init is with the intention of making it easier to add other operators (though you will need to also edit the other regex that checks for illegal characters)

    def splitBuffer(self, buffer, level, nodes):
        # This function is called after a new bracket is reached in the input data. It splits the buffer around the operator and adds each string, the current level (depth), and operator to the running tally of nodes.

        # Uses regex to split the the 2 terms of the buffer. An empty string means that there is a sub-node. Input: "55+2", Output: ["55", "2"]
        elements = self._regex.split(buffer)
        
        # This turns all number containing strings into intergers. This makes the output more flexible because you can perform operations on the nodes. Nodes are at times checked for being intergers so this ensures that.
        for i in range(len(elements)):
            if not elements[i] == '':
                elements[i] = int(elements[i])

        # Fetches the operator. Input "5+2", Output "+"
        try:
            operator = self._regex.search(buffer).__getitem__(0)
        except AttributeError:
            raise(Exception("No operator found"))
        
        # Validates number of operands within a buffer. For example, a buffer of "+5+" would have a split length of 3, ['', '5', '']
        if not len(elements) == 2 :
            raise(Exception("Not a valid expression, wrong number of operands. Found: " + str(len(elements)) + ", expected 2"))
        
        # Appends a new node. We don't care about nodes within nodes at this point, rather we track what level a node is on (that being, how many levels down the tree we are)
        nodes.append({"node1" : elements[0], "node2" : elements[1], "operator" : operator, "level": level}) 
    
    def combineNodes(self, node, nodeNum, pivotNode):
        # This function takes in a node and a pivotNode and nests the node into the pivotNode. 
        
        # If the list of nodes is only one, there is no point in having that list anymore (we want out final dictionary to contain no lists). This makes the first item in the list into the node.
        if len(node)==1:                    
            node = node[0]
        # This is the recursive entry point. If there are multiple nodes in the list, this is called to start the cycle again of splitting the list in two, till there is only one element in every list.
        else:
            node = self.unflattenNodes(node)
        
        # The elements list from splitBuffer contains the values to the right and the left of the operator in the form ['5', '2']. If there is a subnode to the left or the right, the value in the list is ''. Here we nest 'node' into the pivotNode
        if pivotNode[nodeNum] == '':                    
            pivotNode[nodeNum] = node
    
    def unflattenNodes(self, listOfNodes):
        # This function takes in a list of nodes and returns a single nested node.
        # Nodes take the form of dictionaries so this puts dictionaries within dictionaries

        levelList = []
        
        # This creates a list of all the "level" (depth) values of all the nodes in listOfNodes
        for i in range(len(listOfNodes)):
            levelList.append(listOfNodes[i]["level"])
        
        # Level 0 is the base level. 5*6 would be level 0 (though that would not have been passed anyway). (4-3)*(3/2), as it is not surrounded by brackets, would raise this error.
        if 0 in levelList:
            raise(Exception("The expression is not surrounded by brackets"))

        if levelList:
            # We only can have 2 operands in a Binary Tree. Therefore in the lowest level of the tree
            if not levelList.count(min(levelList)) == 1:    
                raise(Exception("Not a valid binary tree. Wrong number of operands. " + str(levelList.count(min(levelList))+1) + " operands detected."))
            
            pivotPosition = levelList.index(min(levelList))
            
            # This was highly inspired by the Binary Search algorithm.
            # We take all the nodes to the left of the pivot
            nodesLeft = listOfNodes[:pivotPosition]
            # Then all the nodes to the right of the pivot
            nodesRight = listOfNodes[pivotPosition+1:] # Adding 1 to pivot excludes the pivot node from node2
            pivotNode = listOfNodes[pivotPosition]

            # We then send those new lists to be combined. combineNodes will call unflattenNodes again (recursively) to split the right side from left if need be.
            self.combineNodes(nodesLeft,"node1",pivotNode) 
            self.combineNodes(nodesRight,"node2",pivotNode)
        
            return pivotNode
        return listOfNodes

    def parse(self, data):
        nodes = []      # Stores a list of all nodes.
        level = 0       # Stores the current depth
        buffer = ""     # A buffer of all legal non bracket characters. This is passed on to splitBuffer for processing
        
        data = data.replace(" ", "")            # Removes spaces from input string

        pattern = compile("[^()0-9/*+-]")    # Checks if there are any illegal characters in input
        if pattern.search(data):
            raise(Exception("Illegal character: " + pattern.search(data).__getitem__(0)))

        for x in list(data):
            if x == "(":
                if not buffer == "":                        # If anything is in the buffer, send the buffer to splitBuffer
                    self.splitBuffer(buffer, level, nodes)
                    buffer = ""
                level += 1

            elif x == ")":
                if not buffer == "":
                    self.splitBuffer(buffer, level, nodes)
                    buffer=""
                level -= 1

            else:
                buffer += x # Add character to buffer. Though not a part of the requirements, this means that we support more than single digit numbers.
        
        # We here return a nested dictionary containing all nodes. The unflattenNodes function turns the list of nodes into a nested dictionary based partially on the tracked level.
        return(self.unflattenNodes(nodes))

class Display:
    # Display Class Design Methedology
    #   To display the internal representation of the binary tree, we generate a text based image representing the tree's nodes.
    #   To that end, we use a 2d grid made out of lists in a list that is sticked together with the __str__ magic method.
    #   Each row in a list of strings. We use space strings to correctly position the output (terminal output is monospaced)
    #   Unicode box drawing characters are used to make lines. https://en.wikipedia.org/wiki/Box-drawing_character
    #   I used the idea of "cursors" to represent positions on the grid. All edits to the grid happen relative to a cursor.
    #   Multiple cursors are stored (this allows us to traverse down the tree in order to make a secondary node)

    def __init__(self):
        self._display = [[]]                                            # 2d grid made out of lists in a list
        self._length = 0                                                # Tracks the number of rows occupied. This is used to generate sufficient spacing between nodes
        self._cursors = []                                              # A list (treaded as a stack) of "cursors". A cursor takes the form of {'x':int, 'y':int}

    def insert(self, cursor, item):                                     # Inserts an item at a certain x, y coordinate on the display
        self.addCursor(cursor)
        self._display[cursor['y']][cursor['x']] = item
    
    def append(self, item):                                             # Appends a new item to the current row. self._cursors[-1] gives the last cursor on the stack
        self._display[self._cursors[-1]['y']].append(item)              # ['y'] gives the y position of the current cursor. 
    
    def addCursor(self, cursor):                                        
        # Adds a cursor to the cursor stack and generate sufficient black space. This ensures that whatever is written to the display is never out of range.
        self._cursors.append(cursor)
        while cursor['y']+1 > len(self._display):                       # Adds new row
            self._display.append([])
        while cursor['x']+1 > len(self._display[cursor['y']]):          # Adds new column. The list contains a space character so it can align the monospace output
            self._display[cursor['y']] += [" "]

    def drawLine(self):                                                 # Draws vertical lines between two nodes.
        startX = self._cursors[-1]['x']                                 # Sets the column the line should be drawn on to be the X value of the last cursor on the stack
        startY = self._cursors[-2]['y'] + 1                             # Sets the starting point of the line to be 1 after second most item on the stack
        length = self._cursors[-1]['y'] - self._cursors[-2]['y'] - 1    # Determines the length of the line (between the latest 2 nodes on the stack)
        for i in range(length):
            self.insert({'x':startX, 'y':startY + i}, "│")
            self._cursors.pop()                                         # Clean up. We don't need the cursor that 'insert' generates anymore.

    def addOperator(self, operator):                                    # Adds the operator between the last 2 cursors. Calculates y position between them.
        x = self._cursors[-1]['x'] + 1
        y = int((self._cursors[-1]['y'] - self._cursors[-2]['y']) /2) + self._cursors[-2]['y']
        self.insert({'x' : x, 'y' : y}, operator)                       
        self._cursors.pop()                                             # Clean up, removes created cursor
        
    def __str__(self):                                                  # Returns the display in string representation. This is used to display the binary tree.
        out = ""
        for a in self._display:                                         # Loops through the list of rows. [row1, row2, ...]
            for b in a:                                                 # For every row, add each element in a row together
                out += str(b)
            out += "\n"                                                 # Adds a new line at the end of every row
        return out

class Node:
    def __init__(self, cursor, node, display, typeNode = True, length = 0):
        self._cursor = cursor       # The cursor that represents the node's position
        self._node = node           # The contents of the node (be it annother node or an interger)
        self._display = display     # Points self._display to the main display
        self._isPrimary = typeNode  # If the node is the first or second node
        self._length = length       # Tracks the number of rows used up by a node (and all of its subnodes) so a secondary node does not overlap with what's above.

    def appendNode(self, focus):
        # This method 

        if type(focus) == int:                  # Appends intergers to tree
            self._display.append("─")
            self._display.append(focus)
            if self._isPrimary:                 # Only adding 2 to length when the node is both primary and an int leads to more compact trees than always adding 2.
                self._length += 2
        else:                                   # If a node is not an interger, that means it is a subnode. This creates a new subnode to the right 
            self._display.append("─┐")
            
            # +2 to x and +1 to y are the positional offset between the current node and a new node
            newCursor = {'x' : self._cursor['x'] + 2, 'y' : self._cursor['y'] + 1} 
            newNodeRight = Node(newCursor, focus, self._display)
            
            self._length += newNodeRight.cycle() + 2

    def cycle(self):
        # The cycle method is the primary method which renders a node to a display. The result is that a tree object is rendered.
        
        # We care if the node is the first or the second. The same "node" value is interpreted in different ways depending if "node1" or "node2" are in focus.
        if self._isPrimary:
            
            self._display.insert(self._cursor, "├") # Base character. Appends cursor to stack
            self.appendNode(self._node["node1"])
            
            # Creates a secondard node below
            newCursor = {'x' : self._cursor['x'],'y' : self._cursor['y'] + self._length}
            newNodeDown = Node(newCursor, self._node, self._display, False)
            
            # Keeps track of length
            self._length += newNodeDown.cycle()

        else:
            self._display.insert(self._cursor, "└")

            self.appendNode(self._node["node2"])

            # Draws line between this (secondary) node and the above primary node (which are represented by the last 2 cursors on the c)
            self._display.drawLine()
            self._display.addOperator(self._node["operator"])
        
        self._display._cursors.pop()
        return self._length 

class BinaryTree:
    # This is meant as an easy entry point for people to use this method in their code. It is responsible for employing all the needed methods to produce an output for the user.                                                           
    def __init__(self, expression, tree = None):
        self._expression = expression                                       # The input expression to be turned into a binary tree
        self._parser = Parser()
        if not tree:
            self._tree = self._parser.parse(expression)                     # Parses the expression into an internal representation (which can be serialized)
        else:
            self._tree = tree
        self._display = Display()
        self._primaryNode = Node({'x':0, 'y':0}, self._tree, self._display) # Initializes the root node of the binary tree (staring at (0,0))
        self._primaryNode.cycle()                                           # Renders the binary tree to self._display

    def __str__(self):              
        return str(self._display)

    def calculate(self):
        return eval(self._expression)   # I'm fully aware that this is unsafe, however, there is no easy solution for this. Before this is executed, it is checked with regex and has to not through an error while being past through by the Parser. The tree is also created before this and therefore, the input is (to the extent of my ability) sanitized. I intended to use literal_eval, however, that is not an indended usecase and it is not supported. If I would redo this assessment, I'd do my parsing through Python's built in Parser and extract things out of that.
    
    def printTree(self):
        print("\nBinary Tree for: " + self._expression + ", with the result of: " + str(self.calculate()) + "\n" + str(self._display))

class FileIO:
    # This class manages file IO
    # The conscious decision was made to not write dedicated exceptions to catch File IO errors as in the context that this application will be executed in (the terminal), Python's in built reporting should be sufficient.
    # We are using JSON files as: 1. Importing them is safe. 2. They are highly correlated with dictionaries (making the process easier) 3. They are easily human/machine readable.

    def __init__(self, fileName):
        self._fileName = fileName

    def read(self):
        with open(self._fileName, "r") as fileObject:
            return load(fileObject)                     # load (and dump) are imported at the top of the file from the inbuilt JSON module

    def write(self, tree):
        with open(self._fileName, "w") as fileObject:
            return dump(tree, fileObject, indent = 4)   # indent = 4 for pretty printing

def UnitTests():
    # Built in tests. The invalid tests come directly from the assessment material.
    choice = int(input('''\nUnit Tests:
    Invalid tests:
    1. (4*3*2)                     Not a valid expression, wrong number of operands.
    2. (4*(2))                     Not a valid expression, wrong number of operands.
    3. (4*(3+2)*(2+1))             Not a valid expression, wrong number of operands.
    4. (2*4)*(3+2)                 Not a valid expression, brackets mismatched.
    5. ((2+3)*(4*5)                Not a valid expression, brackets mismatched.
    6. (2+5)*(4/(2+2)))            Not a valid expression, bracket mismatched.
    7. (((2+3)*(4*5))+(1(2+3)))    Not a valid expression, operator missing.
    
    Valid tests:
    8. (5+1)                       Test the base case
    9. (3+(1+2))                   Test if a subnode on the lower node is created correctly
    10.((3*8)-1)                   Test if a subnode on the upper node is created correctly
    11.((((1-2)+1)*2)/2)           Test if all operators are being handeled correctly
    12.((2+1)*(8-2))               Test if you can have an operator between 2 subnodes
    13.(853846384653824/2)         Test if large numbers are supported (not required by assessment)
    14.((1-(3*2))+((92*314)/24))   Test a complex case
    '''))
    choices = ["(4*3*2)", "(4*(2))", "(4*(3+2)*(2+1))", "(2*4)*(3+2)", "((2+3)*(4*5)", "(2+5)*(4/(2+2)))", "(((2+3)*(4*5))+(1(2+3)))", "(5+1)", "(3+(1+2))", "((3*8)-1)", "((((1-2)+1)*2)/2)", "((2+1)*(8-2))", "(853846384653824/2)", "((1-(3*2))+((92*314)/24))"]
    tree = BinaryTree(choices[choice-1])    # -1 offset as lists start at 0
    tree.printTree()
    return tree # Tree is returned in case you want to test the save to file function

if __name__ == "__main__":
    # This is executed if this script is not imported. It serves as a basic menu to control functions
    choice = int(input('''Assessment 3: Expression Binary Tree
    Enter 0 to input a new expression
    Enter 1 to read back a file
    Enter 2 to execute one of the built in tests
    '''))

    if choice == 1: # Read back file
        print("\nAvailable files in the current directory. You can otherwise specify the full path to a file:")
        for i in listdir():
            print(i)
        
        filename = input("\nNow please enter the file name (or file path) of the file you wish to read:\n")
        
        rawfile = FileIO(filename)
        fileWithMetadata = rawfile.read()
        
        tree = BinaryTree(fileWithMetadata["expression"], fileWithMetadata["tree"])
        tree.printTree()
    elif choice == 2: # Tests
        tree = UnitTests()

    else: # New expression
        tree = BinaryTree(input("\nPlease either input an expression\n"))
        tree.printTree()
    
    choice = int(input('''Would you like to save this tree to a file?
    Enter 0 to exit
    Enter 1 to save a file\n'''))
    if choice: # Save file
        filename = input("\nPlease specify a file name:\n")
        rawfile = FileIO(filename)
        rawfile.write({"expression":tree._expression, "tree":tree._tree})
