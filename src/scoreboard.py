import sys
from rv_zep import SParser
from uf import FuncUnit

def main():
    parse = SParser()
    unit = FuncUnit()
    file = sys.argv[1]
    unit.unit_file(file)
    instructions = parse.parse_file(file)
    unit.set_parser(instructions)
    unit.scoreboarding()
    unit.show()

main()
