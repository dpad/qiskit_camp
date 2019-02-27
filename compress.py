# Python
import logging
from copy import deepcopy

# Local

# External
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


def build_compression_model(orig_circuit):
    """ Given a circuit, builds a parametrised sub-circuit that runs in
    parallel with and approximately models (with compression) the original
    circuit.

    Return:
        QuantumCircuit: new combined circuit consisting of the original circuit
        and the model circuit.
    """

    # We assume all quantum registers of the original circuit are to be
    # modelled.
    new_registers = [reg.__class__(reg.size, '{}_model'.format(reg.name))
                     for reg in orig_circuit.qregs]
    model_circuit = QuantumCircuit(*new_registers)

    # TODO: Build the model's compression circuit here.
    # model_circuit.x(*new_registers)

    # Append the two circuits together.
    top_circuit = orig_circuit + model_circuit

    # Synchronisation barrier just so we know where the original circuits ends.
    top_circuit.barrier()

    # Performs a swap test between the compression model and original circuit.
    # ------------------------------------------------------------------------
    # Firstly, create an ancillary in superposition to store the swap test result.
    swap_tester = QuantumRegister(1, 'swap_tester')
    top_circuit.add_register(swap_tester)
    top_circuit.h(swap_tester)

    # Next, we perform controlled SWAPs using the swap tester.
    for orig_reg, model_reg in zip(orig_circuit.qregs, model_circuit.qregs):
        top_circuit.cswap(swap_tester, orig_reg, model_reg)

    # Finally, we re-interfere the branches and measure the swap tester.
    top_circuit.h(swap_tester)
    swap_test_result = ClassicalRegister(1, 'swap_test_result')
    top_circuit.add_register(swap_test_result)
    top_circuit.measure(swap_tester, swap_test_result)

    return top_circuit
