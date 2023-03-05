from automaton.automaton import Automaton
from tree.tree import Tree
from utils.set import Set
from utils.state import State


class Direct():
    def __init__(self):
        self.counter = 1
        self.table = []
        self.automata = Automaton()

    def Direct(self, postfix_expression):

        postfix_expression = postfix_expression + "#."
        tree = Tree(postfix_expression)
        tree.BuildTree("arbol_direct")
               
        direct = self.directAfd(tree.node)
        direct.toString()
        direct.toGraph(direct, "Direct")

        return direct
    
    def directAfd(self, node):
        self.numberNodes(node)
        self.checkNullable(node)
        self.checkFirstPos(node)
        self.checkLastPos(node)
        self.checkFollowPos(node)

        self.addSymbols(node)

        counter = 0

        # initstate  es firstpos del nodo raiz
        initstate = State(counter,"inicial", node.firstpos)
        self.automata.states.AddItem(initstate)
        self.automata.initialState = initstate
        counter += 1

        for state in self.automata.states.elements:
            for symbol in self.automata.symbols.elements:
                union = Set()
                for element in state.AFN_states.elements:
                    if symbol == element.symbol:
                        union = union.Union(element.followpos)

                if not union.IsEmpty():
                    alreadyExists = self.stateAlreadyExists(union)

                    if alreadyExists is None:

                        if "#" in(s.symbol for s in union.elements):
                            new_state = State(counter, 'final', union)
                            self.automata.finalStates.AddItem(new_state)
                        else:                     
                            new_state = State(counter, 'normal', union)

                        self.automata.states.AddItem(new_state)
                        union = Set()
                        counter += 1    

                        self.automata.addTransition(state, new_state, symbol)

                    else:
                        self.automata.addTransition(state, alreadyExists, symbol)

        return self.automata
                    

    def stateAlreadyExists(self, state):
        for element in self.automata.states.elements:
            if element.AFN_states.elements == state.elements:
                return element
        return None       


    def numberNodes(self, node):

        if node.is_leaf():
            if node.symbol != 'ε':
                node.number = self.counter
                self.table.append(node)
                self.counter += 1
        else:
            if (node.left_child != None):
                self.numberNodes(node.left_child)
            if (node.right_child != None):
                self.numberNodes(node.right_child)

    def checkNullable(self, node):
        if node.is_leaf():
            node.nullable = node.symbol == 'ε'
        else:
            if node.symbol == '*':
                self.checkNullable(node.left_child)
                node.nullable = True
                
            elif node.symbol == '+':
                self.checkNullable(node.left_child)
                node.nullable = True
                
            elif node.symbol == '?':
                self.checkNullable(node.left_child)
                node.nullable = True
                
            elif node.symbol == '.':
                self.checkNullable(node.left_child)
                self.checkNullable(node.right_child)

                if node.left_child.nullable and node.right_child.nullable:
                    node.nullable = True
                else:
                    node.nullable = False

            elif node.symbol == '|':
                self.checkNullable(node.left_child)
                self.checkNullable(node.right_child)

                if node.left_child.nullable or node.right_child.nullable:
                    node.nullable = True
                else:
                    node.nullable = False

    def checkFirstPos(self, node):
        if node.is_leaf():
            if node.symbol == 'ε':
                node.firstpos = Set()
            else:
                node.firstpos.AddItem(node)

        else:
            if node.symbol == '*':
                self.checkFirstPos(node.left_child)
                node.firstpos = node.left_child.firstpos
                
            elif node.symbol == '+':
                self.checkFirstPos(node.left_child)
                node.firstpos = node.left_child.firstpos
            
            elif node.symbol == '?':
                self.checkFirstPos(node.left_child)
                node.firstpos = node.left_child.firstpos

            elif node.symbol == '.':
                self.checkFirstPos(node.left_child)
                self.checkFirstPos(node.right_child)

                if node.left_child.nullable:
                    node.firstpos = node.left_child.firstpos.Union(node.right_child.firstpos)
                else:
                    node.firstpos = node.left_child.firstpos
            elif node.symbol == '|':
                self.checkFirstPos(node.left_child)
                self.checkFirstPos(node.right_child)

                node.firstpos = node.left_child.firstpos.Union(node.right_child.firstpos)

    def checkLastPos(self, node):
        if node.is_leaf():
            if node.symbol == 'ε':
                node.lastpos = Set()
            else:
                node.lastpos.AddItem(node)
        else:
            if node.symbol == '*':
                self.checkLastPos(node.left_child)
                node.lastpos = node.left_child.lastpos

            elif node.symbol == '+':
                self.checkLastPos(node.left_child)
                node.lastpos = node.left_child.lastpos

            elif node.symbol == '?':
                self.checkLastPos(node.left_child)
                node.lastpos = node.left_child.lastpos

            elif node.symbol == '.':
                self.checkLastPos(node.left_child)
                self.checkLastPos(node.right_child)

                if node.right_child.nullable:
                    node.lastpos = node.left_child.lastpos.Union(node.right_child.lastpos)
                else:
                    node.lastpos = node.right_child.lastpos
            elif node.symbol == '|':
                self.checkLastPos(node.left_child)
                self.checkLastPos(node.right_child)

                node.lastpos = node.left_child.lastpos.Union(node.right_child.lastpos)


    def checkFollowPos(self,node):
        if node.symbol == ".":
            first_pos_right = node.right_child.firstpos
            last_pos_left = node.left_child.lastpos

            for i in last_pos_left.elements:
                for j in first_pos_right.elements:
                    self.FindNode(i.number).followpos.AddItem(j)

            self.checkFollowPos(node.left_child)
            self.checkFollowPos(node.right_child)

        if node.symbol == "*":
            first_pos = node.firstpos
            last_pos = node.lastpos

            for i in last_pos.elements:
                for j in first_pos.elements:
                    self.FindNode(i.number).followpos.AddItem(j)

            self.checkFollowPos(node.left_child)
        
        if node.symbol == "+":
            self.checkFollowPos(node.left_child)

        if node.symbol == "?":
            self.checkFollowPos(node.left_child)

        if node.symbol == "|":
            self.checkFollowPos(node.left_child)
            self.checkFollowPos(node.right_child)


    def FindNode(self, number):
        for i in self.table:
            if i.number == number:
                return i
            
    def addSymbols(self, node):
        if node.is_leaf():
            if node.symbol != 'ε' and node.symbol != '#':
                if node.symbol not in self.automata.symbols.elements:
                    self.automata.symbols.AddItem(node.symbol)
        else:
            if (node.left_child != None):
                self.addSymbols(node.left_child)
            if (node.right_child != None):
                self.addSymbols(node.right_child)


