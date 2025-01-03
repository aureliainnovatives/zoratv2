from typing import Dict, Any, ClassVar, Callable, Type
import logging
from ...core.base_tool import BaseTool
import ast
import operator

logger = logging.getLogger(__name__)

class CalculatorCapability(BaseTool):
    """Calculator capability for performing mathematical operations"""
    
    # Class constants
    OPERATORS: ClassVar[Dict[Type[ast.operator], Callable]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize calculator capability"""
        if "name" not in config:
            config["name"] = "Calculator"
        if "description" not in config:
            config["description"] = "Perform mathematical expressions"
        if "parameters" not in config:
            config["parameters"] = {"expression": "string"}
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a calculation"""
        try:
            expression = input_data.get("expression", "")
            if not expression:
                return {"error": "No expression provided"}
                
            result = self._evaluate(expression)
            return {
                "expression": expression,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            return {
                "error": f"Error evaluating expression: {str(e)}"
            }
    
    def _evaluate(self, expr: str) -> float:
        """Safely evaluate a mathematical expression"""
        try:
            # Parse expression into AST
            tree = ast.parse(expr, mode='eval')
            
            # Only allow numeric operations
            if not self._is_safe_operation(tree.body):
                raise ValueError("Expression contains unsupported operations")
            
            # Evaluate expression
            return self._eval_node(tree.body)
            
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _is_safe_operation(self, node: ast.AST) -> bool:
        """Check if the AST node represents a safe operation"""
        if isinstance(node, (ast.Num, ast.UnaryOp, ast.BinOp)):
            if isinstance(node, ast.UnaryOp):
                return isinstance(node.op, tuple(self.OPERATORS.keys()))
            elif isinstance(node, ast.BinOp):
                return (isinstance(node.op, tuple(self.OPERATORS.keys())) and
                        self._is_safe_operation(node.left) and
                        self._is_safe_operation(node.right))
            return True
        return False
    
    def _eval_node(self, node: ast.AST) -> float:
        """Evaluate an AST node"""
        if isinstance(node, ast.Num):
            return float(node.n)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            return self.OPERATORS[type(node.op)](operand)
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.OPERATORS[type(node.op)](left, right)
        else:
            raise ValueError("Invalid operation") 