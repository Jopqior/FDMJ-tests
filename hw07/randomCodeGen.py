import random
import os
from enum import Enum
from typing import Optional

ID_MAX_LENGTH = 10
NUM_MAX = 114514
VAR_MAX = 10

EMPTY_RATE = 0.02
EMPTY_RATE_INC = 0.1

EXP_MAX_DEPTH = 5

TEST_MAX = 20


class VarType(Enum):
    INT = 0
    FLOAT = 1
    # INT_ARRAY = 2
    # FLOAT_ARRAY = 3
    # CLASS = 4

    def __init__(self, class_name: Optional[str] = None):
        self.class_name = class_name

    def __str__(self) -> str:
        if self == VarType.INT:
            return "int"
        elif self == VarType.FLOAT:
            return "float"
        # elif self == VarType.INT_ARRAY:
        #     return "int[]"
        # elif self == VarType.FLOAT_ARRAY:
        #     return "float[]"
        # elif self == VarType.CLASS:
        #     return "class"
        else:
            raise ValueError("Invalid VarType")


var_table = {}

reserved_id = [
    "true",
    "false",
    "public",
    "main",
    "class",
    "extends",
    "int",
    "float",
    "if",
    "else",
    "while",
    "continue",
    "break",
    "return",
    "this",
    "new",
    "putnum",
    "putch",
    "putarray",
    "starttime",
    "stoptime",
    "getnum",
    "getarray",
    "length",
]


def gen_id(alloc: bool = False, var_type: VarType = VarType.INT) -> str:
    def _gen_id() -> str:
        first_char: str = random.choice(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
        )
        rest_chars: str = "".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_",
                k=random.randint(0, ID_MAX_LENGTH),
            )
        )
        return first_char + rest_chars

    if alloc:
        res = _gen_id()
        while res in list(var_table.keys()) or res in reserved_id:
            res = _gen_id()
        var_table[res] = var_type
        return res
    else:
        # ignore var_type
        # choose from all vars
        res = random.choice(list(var_table.keys()))
        return res


def gen_num_const() -> str:
    # gen int or float at random
    return random.choice(
        [str(random.randint(0, NUM_MAX)), str(random.uniform(0, NUM_MAX))]
    )


def gen_var_decl() -> str:
    # decl or decl = exp at random
    var_type = random.choice(list(VarType))
    var_id = gen_id(alloc=True, var_type=var_type)
    return random.choice(
        [f"{var_type} {var_id};", f"{var_type} {var_id} = {gen_num_const()};"]
    )


def gen_var_decl_list() -> str:
    # decl_list or decl_list decl at random
    decl_list = []
    for _ in range(random.randint(1, VAR_MAX)):
        decl_list.append(gen_var_decl())
    return "\n".join(decl_list)


def gen_exp(depth: int, empty_rate: float) -> str:
    def _gen_id() -> str:
        return gen_id(alloc=False)

    def _gen_num_const() -> str:
        return gen_num_const()

    def _gen_op() -> str:
        return random.choice(
            ["+", "-", "*", "/", "||", "&&", "<", "<=", ">", ">=", "==", "!="]
        )

    def _gen_bool() -> str:
        return random.choice(["true", "false"])

    def _gen_ext_call() -> str:
        return random.choice(["getnum()", "getch()"])

    _gen_terminal = [_gen_id, _gen_num_const, _gen_bool, _gen_ext_call]

    class _Exp_Nonterminal(Enum):
        OP_EXP = 0
        NOT_EXP = 1
        MINUS_EXP = 2
        PAR_EXP = 3
        ESC_EXP = 4

    def _gen_exp(depth: int, empty_rate: float) -> str:
        if depth == 1:
            return random.choice(_gen_terminal)()
        else:
            exp = random.choice(list(_Exp_Nonterminal))
            if exp == _Exp_Nonterminal.OP_EXP:
                lexp = _gen_exp(depth - 1, empty_rate + EMPTY_RATE_INC)
                rexp = _gen_exp(depth - 1, empty_rate + EMPTY_RATE_INC)
                op = _gen_op()
                return f"({lexp}) {op} ({rexp})"
            elif exp == _Exp_Nonterminal.NOT_EXP:
                return f"!({_gen_exp(depth - 1, empty_rate + EMPTY_RATE_INC)})"
            elif exp == _Exp_Nonterminal.MINUS_EXP:
                return f"-({_gen_exp(depth - 1, empty_rate + EMPTY_RATE_INC)})"
            elif exp == _Exp_Nonterminal.PAR_EXP:
                return f"({_gen_exp(depth - 1, empty_rate + EMPTY_RATE_INC)})"
            elif exp == _Exp_Nonterminal.ESC_EXP:
                return f"({{{gen_stm_list(empty_rate + EMPTY_RATE_INC)}}} ({_gen_exp(depth - 1, empty_rate + EMPTY_RATE_INC)}))"

    return _gen_exp(depth, empty_rate)


while_cnt = 0


def gen_stm(empty_rate: float) -> str:
    global while_cnt

    def _gen_nested_stm(empty_rate: float) -> str:
        return f"{{{gen_stm_list(empty_rate + EMPTY_RATE_INC)}}}"

    def _gen_if_stm(empty_rate: float) -> str:
        return random.choice(
            [
                f"if ({gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)})\n{gen_stm(empty_rate + EMPTY_RATE_INC)}\nelse\n{gen_stm(empty_rate + EMPTY_RATE_INC)}",
                f"if ({gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)})\n{gen_stm(empty_rate + EMPTY_RATE_INC)}",
            ]
        )

    def _gen_while_stm(empty_rate: float) -> str:
        while_test = gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)
        global while_cnt
        while_cnt += 1
        res = random.choice(
            [
                f"while ({while_test}) \n{gen_stm(empty_rate + EMPTY_RATE_INC)}",
                f"while ({while_test}) \n;",
            ]
        )
        while_cnt -= 1
        return res

    def _gen_assign_stm(empty_rate: float) -> str:
        var = gen_id(alloc=False)
        return f"{var} = {gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)};"

    def _gen_continue_stm(empty_rate: float) -> str:
        return "continue;"

    def _gen_break_stm(empty_rate: float) -> str:
        return "break;"

    def _gen_return_stm(empty_rate: float) -> str:
        return f"return {gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)};"

    def _gen_putnum_stm(empty_rate: float) -> str:
        return f"putnum({gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)});"

    def _gen_putch_stm(empty_rate: float) -> str:
        return f"putch({gen_exp(EXP_MAX_DEPTH, empty_rate + EMPTY_RATE_INC)});"

    def _gen_starttime_stm(empty_rate: float) -> str:
        return "starttime();"

    def _gen_stoptime_stm(empty_rate: float) -> str:
        return "stoptime();"

    if while_cnt > 0:
        return random.choice(
            [
                _gen_nested_stm,
                _gen_if_stm,
                _gen_assign_stm,
                _gen_continue_stm,
                _gen_break_stm,
                _gen_return_stm,
                _gen_putnum_stm,
                _gen_putch_stm,
                _gen_starttime_stm,
                _gen_stoptime_stm,
            ]
        )(empty_rate)
    else:
        return random.choice(
            [
                _gen_nested_stm,
                _gen_if_stm,
                _gen_while_stm,
                _gen_assign_stm,
                _gen_return_stm,
                _gen_putnum_stm,
                _gen_putch_stm,
                _gen_starttime_stm,
                _gen_stoptime_stm,
            ]
        )(empty_rate)


def gen_stm_list(empty_rate: float) -> str:
    def _gen_empty() -> str:
        return ""

    def _gen_nonempty() -> str:
        return f"{gen_stm(empty_rate + EMPTY_RATE_INC)}\n{gen_stm_list(empty_rate + EMPTY_RATE_INC)}"

    r = random.random()
    if r < empty_rate:
        return _gen_empty()
    else:
        return _gen_nonempty()


def gen_main() -> str:
    return f"public int main() {{\n{gen_var_decl_list()}\n{gen_stm_list(EMPTY_RATE)}}}"


def gen_prog() -> str:
    return gen_main()


def test():
    for i in range(TEST_MAX):
        var_table.clear()
        with open("myRandomTest" + str(i).zfill(2) + ".fmj", "w") as f:
            f.write(gen_prog())


if __name__ == "__main__":
    test()
