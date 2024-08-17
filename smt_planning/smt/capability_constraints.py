from typing import List

from smt_planning.smt.StateHandler import StateHandler
from smt_planning.openmath.parse_openmath import from_open_math_in_graph

def capability_constraints_smt(happenings: int, event_bound: int) -> List[str]:	
	query_handler = StateHandler().get_query_handler()
	capability_dictionary = StateHandler().get_capability_dictionary()
	constraint_assertions = []
	for happening in range(happenings):
		for constraint_info in capability_dictionary.input_capability_constraints:
			current_capability = capability_dictionary.get_capability_occurrence(constraint_info.cap, happening).z3_variable	
			infix_constraint = from_open_math_in_graph(query_handler, constraint_info.constraintIri, happening, 0)							
			prefix_expression = infix_to_prefix(infix_constraint)
			assertion = f"(assert (=> {(current_capability.sexpr())} ({prefix_expression})))"
			constraint_assertions.append(assertion)
		for constraint_info in capability_dictionary.output_capability_constraints:
			current_capability = capability_dictionary.get_capability_occurrence(constraint_info.cap, happening).z3_variable	
			infix_constraint = from_open_math_in_graph(query_handler, constraint_info.constraintIri, happening, 1)							
			prefix_expression = infix_to_prefix(infix_constraint)
			assertion = f"(assert (=> {(current_capability.sexpr())} ({prefix_expression})))"
			constraint_assertions.append(assertion)

	return constraint_assertions



def infix_to_prefix(infix_expression):
	precedence_levels = {
		'or': 0,
		'and': 1,
		'=': 2,
		'>': 2,
		'>=': 2,
		'<': 2,
		'<=': 2,
		'distinct': 2,
		'+': 3,
		'-': 3,
		'*': 4,
		'/': 4,
		'^': 5
	}
	
	def precedence(operator):
		return precedence_levels.get(operator, 0)

	def reverse_expression(expression):
		return ''.join(reversed(expression))

	def infix_to_postfix(expression):
		stack = []
		output = []
		expression = reverse_expression(expression)

		split_expression = expression.split(" ")
		reversed_operators = [reverse_expression(op) for op in precedence_levels.keys()]
		for element in split_expression:
			if element in reversed_operators: # Operator
				while stack and precedence(element) <= precedence(stack[-1]):
					output.append(stack.pop())
				element = add_space(element)
				stack.append(element)
			elif element == ')':
				element = add_space(element)
				stack.append(element)
			elif element == '(':
				while stack and stack[-1] != ')':
					output.append(stack.pop())
				stack.pop()  # Pop the '('
			else:  # Operand
				element = add_space(element)
				output.append(element)

		while stack:
			output.append(stack.pop())

		return reverse_expression(''.join(output))
	
	def add_space(element):
		padded_element = element + " "
		return padded_element

	return infix_to_postfix(infix_expression)