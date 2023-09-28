from smt_planning.openmath.math_symbol_information import MathSymbolInformation

class OperatorDictionary:
	mathJsToOpenMathMapping = {
		# Relations
		"=": "http://www.openmath.org/cd/relation1#eq",
		"<": "http://www.openmath.org/cd/relation1#lt", 
		">": "http://www.openmath.org/cd/relation1#gt", 
		"!=": "http://www.openmath.org/cd/relation1#neq",
		"<=": "http://www.openmath.org/cd/relation1#leq",
		">=": "http://www.openmath.org/cd/relation1#geq", 
		# Arithmetic operators
		"+": "http://www.openmath.org/cd/arith1#plus",
		"-": "http://www.openmath.org/cd/arith1#minus",
		"*": "http://www.openmath.org/cd/arith1#times",
		"/": "http://www.openmath.org/cd/arith1#divide",
		"sqrt": "http://www.openmath.org/cd/arith1#root",
		"pow": "http://www.openmath.org/cd/arith1#power",
		"abs": "http://www.openmath.org/cd/arith1#abs",
		# Transcendental functions
		"sin": "http://www.openmath.org/cd/transc1#sin",
		"cos": "http://www.openmath.org/cd/transc1#cos",
		"tan": "http://www.openmath.org/cd/transc1#tan",
	}

	openMathToMathJsMapping = {
		# Relations
		"http://www.openmath.org/cd/relation1#eq": MathSymbolInformation("=", 2),
		"http://www.openmath.org/cd/relation1#lt": MathSymbolInformation("<",2),
		"http://www.openmath.org/cd/relation1#gt": MathSymbolInformation(">",2),
		"http://www.openmath.org/cd/relation1#neq": MathSymbolInformation("!=", 2),
		"http://www.openmath.org/cd/relation1#leq": MathSymbolInformation("<=",2),
		"http://www.openmath.org/cd/relation1#geq": MathSymbolInformation(">=", 2),
		# Arithmetic operators
		"http://www.openmath.org/cd/arith1#plus": MathSymbolInformation("+", 2),
		"http://www.openmath.org/cd/arith1#minus": MathSymbolInformation("-", 2),
		"http://www.openmath.org/cd/arith1#times": MathSymbolInformation("*", 2),
		"http://www.openmath.org/cd/arith1#divide": MathSymbolInformation("/", 2),
		"http://www.openmath.org/cd/arith1#root": MathSymbolInformation("sqrt", 1),
		"http://www.openmath.org/cd/arith1#power": MathSymbolInformation("pow", 1),
		"http://www.openmath.org/cd/arith1#abs": MathSymbolInformation("abs", 1),
		# Transcendental functions
		"http://www.openmath.org/cd/transc1#sin": MathSymbolInformation("sin", 1),
		"http://www.openmath.org/cd/transc1#cos": MathSymbolInformation("cos", 1),
		"http://www.openmath.org/cd/transc1#tan": MathSymbolInformation("tan", 1),
	}

	@staticmethod
	def getOpenMathSymbol(mathJsSymbol: str) -> str:
		try:
			return OperatorDictionary.mathJsToOpenMathMapping[mathJsSymbol]
		except:
			return "http://www.openmath.org/cd/error#unhandled_symbol"

	@staticmethod
	def getMathJsSymbol(openMathSymbol: str)-> MathSymbolInformation:
		try:
			return OperatorDictionary.openMathToMathJsMapping[openMathSymbol]
		except:
			raise Exception(f"Error while finding the MathJS symbol for the OpenMath symbol {openMathSymbol}")