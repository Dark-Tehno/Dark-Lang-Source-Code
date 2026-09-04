# Copyright 2026 Dark.Tehno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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