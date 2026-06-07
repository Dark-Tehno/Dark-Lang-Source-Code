# builtins:
code_print = "print({var}, end='')"
code_println = "print({var})"

code_input = "input()"
code_to_str = "str({var})"
code_to_int = "int({var})"
code_to_float = "float({var})"
code_type = "_dark_type({var})"

# var:
code_var = "{var_name} = {var_data}"

# binop:
code_binop_more = "{left} > {right}"
code_binop_less = "{left} < {right}"
code_binop_more_eq = "{left} >= {right}"
code_binop_less_eq = "{left} <= {right}"
code_binop_eq = "{left} == {right}"
code_binop_not_eq = "{left} != {right}"
code_binop_plus = "{left} + {right}"
code_binop_minus = "{left} - {right}"
code_binop_mul = "{left} * {right}"
code_binop_div = "{left} / {right}"

# logical_op:
code_logical_op_and = "{left} and {right}"
code_logical_op_or = "{left} or {right}"

# unary:
code_unary_not = "not {var}"