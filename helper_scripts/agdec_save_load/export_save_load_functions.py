# Ghidra Python script: export save/load function disassembly and refs to JSON.
# Run via execute-script (agdec-http). Output is JSON printed to stdout.
# Usage: script is invoked with current program; addresses are hardcoded for K1.


# K1 save/load core addresses (from KOTOR_SAVE_LOAD_RE_REPORT.md)
K1_ADDRESSES = [
    0x00401080,  # DoSaveGameScreenShot
    0x004B2520,  # HasEnoughDiskSpaceForSaveGame
    0x004AE6E0,  # SaveGame (thunk)
    0x004AE6F0,  # LoadGame (thunk)
    0x004B58A0,  # SaveGame (CServerExoAppInternal)
    0x004BA640,  # LoadGame (CServerExoAppInternal)
    0x004B95B0,  # LoadModule
]


def to_hex(addr):
    if addr is None:
        return None
    return addr.toString()


def main():
    program = currentProgram()
    fm = program.getFunctionManager()
    listing = program.getListing()
    refMgr = program.getReferenceManager()
    addr_factory = program.getAddressFactory()

    result = {"program": program.getName(), "functions": []}

    for addr_val in K1_ADDRESSES:
        addr = toAddr(addr_val)
        func = fm.getFunctionAt(addr)
        if not func:
            result["functions"].append(
                {"address": to_hex(addr), "name": None, "error": "no function at address"}
            )
            continue

        # Signature
        sig = str(func.getSignature()) if func.getSignature() else None

        # Disassembly (instruction strings)
        disasm = []
        body = func.getBody()
        if body:
            insn_iter = listing.getInstructions(body, True)
            while insn_iter.hasNext():
                insn = insn_iter.next()
                disasm.append(insn.toString())

        # Callers: references TO this function's entry point
        callers = []
        for ref in refMgr.getReferencesTo(addr):
            callers.append(to_hex(ref.getFromAddress()))

        # Callees: from each instruction in the function, collect call targets
        callees = []
        seen = set()
        if body:
            insn_iter = listing.getInstructions(body, True)
            while insn_iter.hasNext():
                insn = insn_iter.next()
                for ref in refMgr.getReferencesFrom(insn.getAddress()):
                    if ref.getReferenceType().isCall():
                        to_addr = ref.getToAddress()
                        key = to_hex(to_addr)
                        if key and key not in seen:
                            seen.add(key)
                            callees.append(key)

        result["functions"].append(
            {
                "address": to_hex(addr),
                "name": func.getName(),
                "signature": sig,
                "disassembly": disasm,
                "callers": callers,
                "callees": callees,
            }
        )

    # Return for execute-script (agdec-http): assign to __result__ for MCP response
    globals()["__result__"] = result


main()
