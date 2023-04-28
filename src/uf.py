class FuncUnit:
    OPCODES = {
        0: 'int',
        1: 'int',
        2: 'add',
        3: 'add',
        4: 'mult',
        5: 'div'
    }

    transcrição = {
        'busy': 0,
        'op': 1,
        'fi': 2,
        'fj': 3,
        'fk': 4,
        'qj': 5,
        'qk': 6,
        'rj': 7,
        'rk': 8,
        'table': 9
    }

    score_clean = [0, None, 0, 0, 0, 0, 0, 0, 0, None]

    def __init__(self):
        self.instructions = []
        self.parser = None
        self.ciclo = 0
        self.scoreboard = {
            'int': [],
            'mult': [],
            'add': [],
            'div': []
        }
        self.units = {
            'int': [0, 0],
            'mult': [0, 0],
            'add': [0, 0],
            'div': [0, 0]
        }
        self.data = {
            'instrucoes': self.instructions,
            'issue': [],
            'read': [],
            'execute': [],
            'write': []
        }
        
    def unit_file(self, filename):
        with open(filename, 'r') as file:
            for i in range(4):
                line = file.readline().rstrip()
                name, quantity, cycle = line.split()
                if name == ".int":
                    self.units['int'][0] = int(quantity)
                    self.units['int'][1] = int(cycle)
                elif name == ".mult":
                    self.units['mult'][0] = int(quantity)
                    self.units['mult'][1] = int(cycle)
                elif name == ".add":
                    self.units['add'][0] = int(quantity)
                    self.units['add'][1] = int(cycle)
                elif name == ".div":
                    self.units['div'][0] = int(quantity)
                    self.units['div'][1] = int(cycle)
                else:
                    break
            for line in file:
                self.instructions.append(line.rstrip())
        self.set_scoreboard()
        self.set_data()
    
    def scoreboarding(self):
        n_i = 0
        n_max = len(self.instructions)
        self.ciclo = 1

        # CRIAR CONDIÇÃO DE PARADA
        while (True):
            # print()
            # print('CLOCK: ', self.ciclo)
            # print()
            # Add new instruction (start issue)
            if n_i < n_max:
                inst = self.parser[n_i]
                if self.check_fi(inst['rd']):
                    op = inst['opcode']
                    opcode = self.OPCODES[op]
                    status = self.check_fc(opcode)
                    if status >= 0:
                        if self.check_fi(inst['rs1']) or op == 0:
                            pos = self.transcrição['qj']
                            self.scoreboard[opcode][status][pos] = 1
                            self.scoreboard[opcode][status][pos+2] = 1
                        if self.check_fi(inst['rs2']):
                            pos = self.transcrição['qk']
                            self.scoreboard[opcode][status][pos] = 1
                            self.scoreboard[opcode][status][pos+2] = 1
                        self.scoreboard[opcode][status][0] = 1
                        self.scoreboard[opcode][status][1] = inst['opcode']
                        self.scoreboard[opcode][status][2] = inst['rd']
                        self.scoreboard[opcode][status][3] = inst['rs1']
                        self.scoreboard[opcode][status][4] = inst['rs2']
                        pos = self.transcrição['table']
                        self.scoreboard[opcode][status][pos] = ['issue', self.ciclo, n_i]
                        self.data['issue'][n_i] = self.ciclo
                        n_i += 1
            
            # avança, se possivel, nas instruções já iniciadas
            for op in self.scoreboard:
                for k in self.scoreboard[op]:
                    pos = self.transcrição['busy']
                    if k[pos] == 0:
                        continue
                    pos = self.transcrição['table']
                    if (
                        k[pos][0] == 'issue' and self.ciclo >= k[pos][1]+1 and
                        self.check_read(k)
                        ):
                        k[pos][0] = 'read'
                        k[pos][1] = self.ciclo
                        k[pos-1] = 0
                        k[pos-2] = 0
                        self.data['read'][k[pos][2]] = self.ciclo
                    elif k[pos][0] == 'read' and self.ciclo >= k[pos][1]+1:
                        k[pos][0] = 'execute'
                        k[pos][1] = self.ciclo
                        self.data['execute'][k[pos][2]] = self.ciclo + self.units[op][1] - 1
                    elif k[pos][0] == 'execute' and self.check_cycle(k, op):
                        k[pos][0] = 'write'
                        k[pos][1] = self.ciclo
                        self.data['write'][k[pos][2]] = self.ciclo
                        for ss in range(len(self.score_clean)):
                            k[ss] = self.score_clean[ss]

            self.ciclo += 1
            # self.show_scoreboard()
            # self.show()

            if n_i >= n_max and self.is_empty():
                break  

    def is_empty(self) -> bool:
        for func in self.scoreboard:
            for k in self.scoreboard[func]:
                if k != self.score_clean:
                    return False
        return True

    # Vefifica se tem unidade funcional livre
    # Caso positivo, retorna o index da unidade livre
    def check_fc(self, op) -> int:
        n = len(self.scoreboard[op])
        for i in range(n):
            unit = self.scoreboard[op][i]
            if unit[self.transcrição['busy']] == 0:
                return i
        return -1

    # Trava issue
    # Verifica se mais alguém ira escrever em fi (WAW), (RAW)
    # Retorna false se existe
    def check_fi(self, fi) -> bool:
        if fi == 0:
            return True
        for op in self.scoreboard:
            for k in self.scoreboard[op]:
                pos = self.transcrição['fi']
                if k[pos] == fi:
                    if not (k[-1][0] == 'write' and k[-1][1] < self.ciclo):
                        return False
        return True
    
    # Verifica se as duas leituras estão prontas
    # Hazards do tipo RAW podem sofrer atrasos,
    # quando essa função for chamada antes da liberação da unidade funcional.
    def check_read(self, unit) -> bool:
        p_fi = self.transcrição['fi']
        p_fj = self.transcrição['fj']
        p_fk = self.transcrição['fk']
        p_rj = self.transcrição['rj']
        p_rk = self.transcrição['rk']
        if unit[p_rj] and unit[p_rk]:
            return True
        
        for func in self.scoreboard:
            for k in self.scoreboard[func]:
                posA = self.transcrição['busy']
                posB = self.transcrição['op']
                if k[posA] == 0 or k[-1][2] == unit[-1][2]:
                    continue
                if k[p_fi] == unit[p_fj]:
                    return False
                if k[p_fi] == unit[p_fk]:
                    return False
        unit[p_rj] = 1
        unit[p_rk] = 1
        return False
    
    # Verifica se passou os n ciclos de execução
    # verifica hazard WAR
    def check_cycle(self, unit, op) -> bool:
        pos = self.transcrição['table']
        cycle = self.data['read'][unit[pos][2]]
        n_cycle = self.units[op][1]

        # Check Hazard WAR
        hazard = False
        p_fi = self.transcrição['fi']
        p_fj = self.transcrição['fj']
        p_fk = self.transcrição['fk']
        p_rj = self.transcrição['rj']
        p_rk = self.transcrição['rk']
        for func in self.scoreboard:
            for k in self.scoreboard[func]:
                posA = self.transcrição['busy']
                if k[posA] == 0:
                    continue
                if unit[p_fi] == k[p_fj]:
                    if k[p_rj]:
                        hazard = True
                if unit[p_fi] == k[p_fk]:
                    if k[p_rk]:
                        hazard = True

        if not hazard and self.ciclo > cycle + n_cycle:
            return True
        return False


    def set_scoreboard(self):
        for i in self.units:
            for j in range(self.units[i][0]):
                self.scoreboard[i].append(self.score_clean.copy())
    
    def set_data(self):
        n = len(self.instructions)
        self.data['issue'] = [0] * n
        self.data['read'] = [0] * n
        self.data['execute'] = [0] * n
        self.data['write'] = [0] * n
    
    def set_parser(self, inst):
        self.parser = inst
    
    def show(self):
        print('+' + '-' * 22 + '+' + '-' * 9 + '+' + '-' * 9 + '+' + '-' * 11 + '+' + '-' * 9 + '+')
        print(f"| {'Instrucoes':^20} | {'Issue':^7} | {'Read':^7} | {'Execute':^9} | {'Write':^7} |")
        print('+' + '-' * 22 + '+' + '-' * 9 + '+' + '-' * 9 + '+' + '-' * 11 + '+' + '-' * 9 + '+')

        for i in range(len(self.data['instrucoes'])):
            print(f"| {self.data['instrucoes'][i]:<20} | {self.data['issue'][i]:^7} | {self.data['read'][i]:^7} | {self.data['execute'][i]:^9} | {self.data['write'][i]:^7} |")

        print('+' + '-' * 22 + '+' + '-' * 9 + '+' + '-' * 9 + '+' + '-' * 11 + '+' + '-' * 9 + '+')
    
    def show_units(self):
        print(f"Unit: {'int'}, Quantity: {self.units['int'][0]}, Cycles: {self.units['int'][1]}")
        print(f"Unit: {'mult'}, Quantity: {self.units['mult'][0]}, Cycles: {self.units['mult'][1]}")
        print(f"Unit: {'add'}, Quantity: {self.units['add'][0]}, Cycles: {self.units['add'][1]}")
        print(f"Unit: {'div'}, Quantity: {self.units['div'][0]}, Cycles: {self.units['div'][1]}")
        print(self.instructions)
        print(self.scoreboard)
    
    def show_scoreboard(self):
        for op in self.scoreboard:
            for k in self.scoreboard[op]:
                print(k)
