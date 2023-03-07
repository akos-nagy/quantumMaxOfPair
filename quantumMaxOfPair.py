from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile    # libraries for building the circuit
from qiskit.providers.aer import QasmSimulator                                      # simulator



def find_the_largest_number(number_1: int, number_2: int) -> int:

    sign_1 = number_1 >> (32 - 1)                                                   # 0 if positive, - 1 if negative
    sign_2 = number_2 >> (32 - 1)                                                   # note: this works Python's (signed) 'int' type
                                                                                    # for other signed integer types 32 needs to be replaced by the appropriate power

    a = number_1                                                                    # dummy variables to use for computing the classical bits
    b = number_2                                                                    #

    bits = []                                                                       # array to store the classical information

    while a != sign_1 or b != sign_2:                                               # computing the classical information in reverse order
        bits.append([a&1, b&1])                                                     #
        a >>= 1                                                                     #
        b >>= 1                                                                     #

    bits.append([sign_1 + 1, sign_2 + 1])                                           # adding the sign information; 1 if positive, 0 if negative

    qc = QuantumCircuit(QuantumRegister(0),ClassicalRegister(1,'c'))                # creating our circuit and adding a classical register to store the result of the measurement

    i = 0                                                                           # extra variable for labeling
                                                                                    # also useful to distinguish between the first and latter cases
    for x in bits[::-1]:
        qc.add_register(QuantumRegister(1,'a_' + str(i)))                           # setting up a quantum registers for each bit of number_1
        qc.initialize([1 - x[0], x[0]], 3 * i)                                      # storing the bit in the qubit

        qc.add_register(QuantumRegister(1,'b_' + str(i)))                           # setting up a quantum registers for each bit of number_2
        qc.initialize([1 - x[1], x[1]], 3 * i + 1)                                  # storing the bit in the qubit: i |-> |i>

        qc.add_register(QuantumRegister(1,'extra_' + str(i)))                       # extra quantum register to store computational results
        qc.initialize([1, 0], 3 * i + 2)                                            # initialized to |0>

        qc.x(3 * i)                                                                 # implementing the U_< gate
        qc.ccx(3 * i, 3 * i + 1, 3 * i + 2)                                         #
        qc.cx(3 * i, 3 * i + 1)                                                     #

        if i > 0:                                                                   # adding the U_0 gates and XORs

            if i == 1:
                qc.ccx(1, 5, 2)
            else:
                qc.ccx(3 * i - 1, 3 * i + 2, 2)

            if i + 1 < len(bits):                                                   # this 'if' is just cosmetic; the last U_0 and XOR appear after the measurement, thus unnecessary

                qc.x(3 * i + 1)
                qc.ccx(3 * i, 3 * i + 1, 3 * i + 2)
                qc.x(3 * i + 1)

                if i == 1:
                    qc.ccx(1, 4, 5)
                else:
                    qc.ccx(3 * i - 1, 3 * i + 1, 3 * i + 2)

        i += 1

    qc.measure(2, 0)                                                                # the state on register 2 is |1> exactly if number_1 < number_2, and |0> otherwise

    simulator = QasmSimulator()                                                     # starting the simulator

    shot_number = 1                                                                 # since the initialization and the gates are 'idealized' (without error),
                                                                                    # AND the measured register always ends up in either |0> or |1>, a single shot is enough.
                                                                                    # in more realistic scenarios, this number should be higher (depending on the architecture)

    compiled_qc = transpile(qc, simulator)                                          # transpiling the circuit to the simulator

    job = simulator.run(compiled_qc, shots=shot_number)                             # running the simulation

    result = job.result()                                                           # getting the results of the simulation

    counts = result.get_counts(compiled_qc)                                         # the only need information for us is the count of outcomes (numbers of measured |0>'s and |1>'s)

    print(qc.draw())                                                                # printing the circuit

    if ('0' in counts):                                                             # recall: the state on register 2 is |1> exactly if number_1 < number_2, and |0> otherwise; with probability 1
        return number_1
    else:
        return number_2