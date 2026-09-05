// Headless post-script: decompile functions listed in a file and dump C plus callers/callees.
// Usage: analyzeHeadless <proj> gt5 -process EBOOT.elf -noanalysis -scriptPath <dir> -postScript DumpFuncs.java <listfile> <outfile>
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class DumpFuncs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        List<String> lines = Files.readAllLines(Paths.get(args[0]));
        PrintWriter out = new PrintWriter(new FileWriter(args[1]));
        DecompInterface ifc = new DecompInterface();
        DecompileOptions opts = new DecompileOptions();
        ifc.setOptions(opts);
        ifc.openProgram(currentProgram);
        FunctionManager fm = currentProgram.getFunctionManager();
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] parts = line.split("\\s+");
            Address a = toAddr(Long.parseLong(parts[0].replace("0x", ""), 16));
            Function f = fm.getFunctionContaining(a);
            out.println("////////////////////////////////////////////////////////////////");
            if (f == null) {
                out.println("// " + a + ": no function (creating)");
                f = createFunction(a, null);
                if (f == null) { out.println("// failed"); continue; }
            }
            if (parts.length > 1) {
                try { f.setName(parts[1], SourceType.USER_DEFINED); } catch (Exception e) {}
            }
            out.println("// " + f.getName() + " @ " + f.getEntryPoint() + "  size=" + f.getBody().getNumAddresses());
            StringBuilder callers = new StringBuilder();
            for (Function c : f.getCallingFunctions(monitor)) callers.append(c.getName()).append("@").append(c.getEntryPoint()).append(" ");
            out.println("// callers: " + callers);
            StringBuilder callees = new StringBuilder();
            for (Function c : f.getCalledFunctions(monitor)) callees.append(c.getName()).append("@").append(c.getEntryPoint()).append(" ");
            out.println("// callees: " + callees);
            DecompileResults res = ifc.decompileFunction(f, 120, monitor);
            if (res != null && res.getDecompiledFunction() != null) out.println(res.getDecompiledFunction().getC());
            else out.println("// decompile failed: " + (res == null ? "null" : res.getErrorMessage()));
            out.flush();
        }
        out.close();
        ifc.dispose();
    }
}
