import json
import pydot
from IPython.display import display, Image

index = 0

class State:
    def __init__(self, name):
        global index
        self.name = "S" + str(index)
        index += 1
        self.transitions = {}

    def add_transition(self, symbol, state):
        if symbol in self.transitions:
            self.transitions[symbol].append(state)
        else:
            self.transitions[symbol] = [state]

class NFA:
    def __init__(self):
        self.start_state = None
        self.final_state = None
        self.states = {}
        self.current_state_count = 0

    def add_state(self):
        new_state = State("S" + str(self.current_state_count))
        self.current_state_count += 1
        self.states[new_state.name] = new_state
        return new_state

    def connect_states(self, state1, state2, symbol):
        state1.add_transition(symbol, state2)

    def add_states_of_nfa_to_another(self, nfa1, nfa2):
        for state_name, state in nfa2.states.items():
            # #rename the state
            # new_state_name = state_name
            # base_state_name = "S"
            # index = 0
            # while new_state_name in nfa1.states:
            #     index += 1
            #     new_state_name = base_state_name + str(index)
            # #add the  state to the nfa1
            # new_state = State(new_state_name)
            # new_state.transitions = state.transitions
            nfa1.states[state_name] = state

    # def remname_two_nfas(self, nfa1, nfa2):
    #     # Rename the states of nfa2
    #     base_state_name = "S"
    #     index = 0
    #     for state_name, state in nfa2.states.items():
    #         new_state_name = state_name
    #         while new_state_name in nfa1.states:
    #             index += 1
    #             new_state_name = base_state_name + str(index)
    #         # Update the state name in nfa2
    #         if state.name == nfa2.start_state.name:
    #             nfa2.start_state.name = new_state_name
    #         if state.name == nfa2.final_state.name:
    #             nfa2.final_state.name = new_state_name
    #         state.name = new_state_name
    #     return nfa1, nfa2

    def concatenate(self, nfa1, nfa2):
        self.add_states_of_nfa_to_another(nfa1, nfa2)
        nfa1.final_state.add_transition("ε", nfa2.start_state)
        nfa1.final_state = nfa2.final_state
        return nfa1

    def union(self, nfa1, nfa2):
        new_nfa = NFA()
        
        new_start = new_nfa.add_state()
        new_start.add_transition("ε", nfa1.start_state)
        new_start.add_transition("ε", nfa2.start_state)

        new_final = new_nfa.add_state()
        nfa1.final_state.add_transition("ε", new_final)
        nfa2.final_state.add_transition("ε", new_final)

        new_nfa.start_state = new_start
        new_nfa.final_state = new_final

        self.add_states_of_nfa_to_another(new_nfa, nfa1)
        self.add_states_of_nfa_to_another(new_nfa, nfa2)
        
        return new_nfa

    def star(self, nfa):
        new_nfa = NFA()

        new_start = new_nfa.add_state()
        new_final = new_nfa.add_state()

        new_start.add_transition("ε", nfa.start_state)
        new_start.add_transition("ε", new_final)
        nfa.final_state.add_transition("ε", nfa.start_state)
        nfa.final_state.add_transition("ε", new_final)

        new_nfa.start_state = new_start
        new_nfa.final_state = new_final
        
        self.add_states_of_nfa_to_another(new_nfa, nfa)

        return new_nfa


    def plus(self, nfa):
        new_nfa = NFA()

        new_start = new_nfa.add_state()
        new_final = new_nfa.add_state()

        new_start.add_transition("ε", nfa.start_state)
        nfa.final_state.add_transition("ε", nfa.start_state)
        nfa.final_state.add_transition("ε", new_final)

        new_nfa.start_state = new_start
        new_nfa.final_state = new_final
        
        self.add_states_of_nfa_to_another(new_nfa, nfa)

        return new_nfa
    
    def optional(self, nfa):
        new_nfa = NFA()

        new_start = new_nfa.add_state()
        new_final = new_nfa.add_state()

        new_start.add_transition("ε", nfa.start_state)
        new_start.add_transition("ε", new_final)
        nfa.final_state.add_transition("ε", new_final)

        new_nfa.start_state = new_start
        new_nfa.final_state = new_final
        
        self.add_states_of_nfa_to_another(new_nfa, nfa)

        return new_nfa

    def build_nfa(self, regex):
        stack = []
        insideRange = False
        rangeSymbol = ""
        for char in regex:
            if insideRange:
                if char != "]":
                    rangeSymbol += char
                    
                    if index == len(regex) - 1: #[A-Z case]
                        print("Invalid input as the parentheses are not well formed: " + rangeSymbol)
                        return None
                else:
                    rangeSymbol += "]"
                    if rangeSymbol[-2] == "-": #[A-] case
                        print("Invalid input as the range is incomplete: " + rangeSymbol)
                        return None
                    if rangeSymbol[1] == "-": #[-A] case
                        print("Invalid input as the range is incomplete: " + rangeSymbol)
                        return None
                    if not (any(char.isalnum() for char in rangeSymbol[1:-1])): # Check if rangeSymbol contains alphanumeric characters
                        print("Invalid input as the range didn't contain alphanumeric characters: " + rangeSymbol)
                        return None
                    
                    insideRange = False
                    new_nfa = NFA()
                    new_start = new_nfa.add_state()
                    new_final = new_nfa.add_state()
                    new_start.add_transition(rangeSymbol, new_final)
                    new_nfa.start_state = new_start
                    new_nfa.final_state = new_final
                    stack.append(new_nfa)
                    rangeSymbol = ""
            elif char.isalnum(): # Alphanumeric characters
                new_nfa = NFA()
                new_start = new_nfa.add_state()
                new_final = new_nfa.add_state()
                new_start.add_transition(char, new_final)
                new_nfa.start_state = new_start
                new_nfa.final_state = new_final
                stack.append(new_nfa)
            elif char == ".":
                new_nfa = NFA()
                new_start = new_nfa.add_state()
                new_final = new_nfa.add_state()
                new_start.add_transition("[a-zA-z0-9]", new_final)
                new_nfa.start_state = new_start
                new_nfa.final_state = new_final
                stack.append(new_nfa)
            elif char == "*":
                nfa = stack.pop()
                new_nfa = self.star(nfa)
                stack.append(new_nfa)
            elif char == "+":
                nfa = stack.pop()
                new_nfa = self.plus(nfa)
                stack.append(new_nfa)
            elif char == "?":
                nfa = stack.pop()
                new_nfa = self.optional(nfa)
                stack.append(new_nfa)
            elif char == "|":
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                new_nfa = self.union(nfa1, nfa2)
                stack.append(new_nfa)
            elif char == "(":
                stack.append(char)
            elif char == ")":
                nfa = stack.pop()   #the first nfa inside the parenthesis
                nfas_list = []
                while stack[-1] != "(":
                    nfas_list.append(stack.pop())
                if nfas_list.__len__() > 0:
                    for nfa1 in nfas_list:
                        nfa = self.concatenate(nfa1, nfa)
                stack.pop()
                stack.append(nfa)
            elif char == "[":
                insideRange = True
                rangeSymbol = "["
            elif char == "&":
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                new_nfa = self.concatenate(nfa1, nfa2)
                stack.append(new_nfa)

        #print the stack elemments
        # for nfa in stack:
        #     print(nfa.start_state.name, nfa.final_state.name)
        #     print(nfa.generate_json())
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")

        return stack.pop()

    def generate_json(self):
        fsm_dict = {"startingState": self.start_state.name}
        for state_name, state in self.states.items():
            transitions = {}
            for symbol, next_states in state.transitions.items():
                transitions[symbol] = [next_state.name for next_state in next_states]
            fsm_dict[state_name] = {"isTerminatingState": state_name == self.final_state.name, **transitions}
        return json.dumps(fsm_dict, indent=4)
    
    def print_nfa(self):
        for state_name, state in self.states.items():
            print(state_name, state.transitions.keys())
            # for symbol, next_states in state.transitions.items():
            #     print(symbol, [next_state.name for next_state in next_states])

def convert_to_nfa(regex):
    nfa = NFA()
    nfa_expression = nfa.build_nfa(regex)
    return nfa_expression


def precedence(operator):
    if operator == '*' or operator == '+' or operator == '?':
        return 3
    elif operator == '&':
        return 2
    elif operator == '|':
        return 1
    else:
        return 0

def add_concatenation(regex):
    result = []
    clearResult = []
    for i, char in enumerate(regex):
        result.append(char)
        if i < len(regex) - 1 and regex[i+1] != ')' and regex[i+1] not in ['*', '+' , '|', '?' , ')'] and char not in ['(', '|'] and char != '&':
            result.append('&')  # Add concatenation symbol '?'
    
    # clear the result from the '&' symbol if it is between the brackets []
    inside_range = False
    for i, char in enumerate(result):
        if char == '[':
            inside_range = True
        elif char == ']':
            inside_range = False
        if not inside_range or (inside_range and char != '&'):
            clearResult.append(char)
        # if inside_range and char != '&':
        #     clearResult.append(char)
    return ''.join(clearResult)

def shunting_yard(regex):
    regex = add_concatenation(regex)
    print("Regex with concatenation:", regex)
    output = []
    operator_stack = []
    
    i = 0
    while i < len(regex):
        char = regex[i]
        
        if char == '[':
            # Find the first occurrence of the closing bracket ']' starting from i
            closing_bracket_index = regex.find(']', i)
            if closing_bracket_index != -1:
                # Add the substring between '[' and ']' as a single symbol
                symbol = regex[i:closing_bracket_index+1]
                output.append(symbol)
                i = closing_bracket_index + 1
            else:
                # If closing bracket is not found
                print("Invalid input as the parentheses are not well formed. ")
                return None
        elif char.isalnum():
            output.append(char)
            i += 1
        elif char == '(':
            operator_stack.append(char)
            i += 1
        elif char == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()  # Discard '('
            i += 1
        else:
            while operator_stack and precedence(operator_stack[-1]) >= precedence(char):
                output.append(operator_stack.pop())
            operator_stack.append(char)
            i += 1
    
    # Pop remaining operators from the stack and append them to the output
    while operator_stack:
        output.append(operator_stack.pop())
    
    return ''.join(output)

def add_parentheses(regex):
    precedence = {'*': 3, '?': 3, '+': 2, '|': 1}
    result = []
    stack = []
    
    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                result.append(stack.pop())
            if stack[-1] == '(':
                stack.pop()  # Discard '('
        elif char in precedence:
            while stack and precedence.get(stack[-1], 0) >= precedence[char]:
                result.append(stack.pop())
            stack.append(char)
        else:
            result.append(char)
    
    while stack:
        result.append(stack.pop())
    
    return ''.join(result)

def graph_nfa_from_json(json_data):
    graph = pydot.Dot("NFA_Graph", graph_type="digraph")

    # Parse JSON data
    nfa = json.loads(json_data)

    # Add states and transitions to the graph
    for state, transitions in nfa.items():
        if state != 'startingState':
            if transitions.get('isTerminatingState', False):
                node = pydot.Node(state, label=state, shape='doublecircle')
            else:
                node = pydot.Node(state, label=state, shape='circle')
            graph.add_node(node)

            for symbol, next_states in transitions.items():
                if symbol != 'isTerminatingState':
                    for next_state in next_states:
                        if symbol == 'ε':
                            edge = pydot.Edge(state, next_state, label='ε', style='solid')
                        else:
                            edge = pydot.Edge(state, next_state, label=symbol, style='solid')
                        graph.add_edge(edge)

    # Set starting state
    starting_state = nfa['startingState']
    starting_node = pydot.Node('.', label='', shape='point')
    graph.add_node(starting_node)
    start_end_edge = pydot.Edge(starting_node, starting_state, label='start', style='solid')
    graph.add_edge(start_end_edge)

    return graph

def validate_regex(regex):
    # Check if regex is empty
    if not regex:
        print("Error: Regular expression is empty.")
        return None
    
    # Check if regex contains invalid characters
    invalid_chars = set(regex) - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+?|().[]-")
    if invalid_chars:
        print("Error: Regular expression contains invalid characters:", invalid_chars)
        return None
    
    # Check if parentheses are well-formed
    stack = []
    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack.pop() != '(':
                print("Error: Unbalanced parentheses.")
                return None
    if stack:
        print("Error: Unbalanced parentheses.")
        return None
    
    # Check if quantifiers are applied to valid elements
    quantifier_chars = "*+?"
    for i, char in enumerate(regex):
        if char in quantifier_chars:
            if i == 0 or regex[i-1] in quantifier_chars or regex[i-1] == '|' or( i != len(regex) - 1 and regex[i+1] in quantifier_chars):
                print("Error: Invalid use of quantifier:", char)
                return None
    
    # Check if ranges in character classes are well-formed
    inside_range = False
    for i, char in enumerate(regex):
        if char == '[':
            inside_range = True
        elif char == ']':
            if inside_range:
                inside_range = False
            else:
                print("Error: Unbalanced square brackets.")
                return None
        elif inside_range:
            if char == '-':
                if i == 0 or i == len(regex) - 1 or regex[i-1] == '[' or regex[i+1] == ']':
                    print("Error: Invalid use of dash in character.")
                    return None
    
    return regex

def main():
    regex = input("Enter a regular expression: ")
    regex = validate_regex(regex)
    if regex:
        postfix_notation = shunting_yard(regex)
        print("Postfix notation:", postfix_notation)
        if postfix_notation:
            nfa = convert_to_nfa(postfix_notation)
            if nfa:
                json_output = nfa.generate_json()
                print("NFA json is:")
                print(json_output)
                with open('nfa_output.json', 'w') as file:
                    file.write(json_output)
                print("NFA json file has been created.")

                # Create graph from JSON data
                nfa_graph = graph_nfa_from_json(json_output)
                # Save the graph as a PNG file
                nfa_graph.write_png('nfa_graph.png')
                # Display the PNG image
                display(Image(filename='nfa_graph.png'))

if __name__ == "__main__":
    main()