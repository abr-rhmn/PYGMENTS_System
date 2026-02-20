import itertools
import subprocess
import os
import sys
import csv

partitions = {
    "file_existence": ["exists", "missing"],
    "file_content": ["empty", "valid_syntax", "invalid_syntax"],
    "lexer": ["omitted", "valid_match", "valid_mismatch", "invalid"],
    "formatter": ["omitted", "valid", "invalid"],
    "output": ["stdout", "file_path", "restricted"]
}

def generate_test_suite(csv_file=None):
    """
    If csv_file is provided, loads All-Pairs frames from ACTS.
    Otherwise, generates All-Combinations using default logic.
    """
    if csv_file:
        print(f"Loading All-Pairs frames from: {csv_file}")
        with open(csv_file, "r") as f:
            # Filter out ACTS header comments starting with '#'
            reader = csv.DictReader(row for row in f if not row.startswith('#'))
            return [row for row in reader]
    
    print("No CSV provided. Generating All-Combinations (Exhaustive)...")
    test_frames = []
    all_combinations = itertools.product(*partitions.values())
    
    for combo in all_combinations:
        f_exists, f_content, lexer, formatter, output = combo
        if f_exists == "missing" and f_content != "empty":
            continue 

        test_frames.append({
            "file_existence": f_exists,
            "file_content": f_content,
            "lexer": lexer,
            "formatter": formatter,
            "output": output
        })
    return test_frames

def run_tests(frames):
    print(f"Starting execution of {len(frames)} Test Frames...\n")
    
    for i, frame in enumerate(frames):
        # Handle ACTS 'don't care' values by setting to a safe default
        for key in frame:
            if frame[key] == "*": frame[key] = "omitted"

        # 1. Setup Input File - Use .get() to check both potential key names
        test_file = "test_input.py"
        file_status = frame.get('file_existence') or frame.get('file')
        
        if file_status == "exists":
            with open(test_file, "w") as f:
                # Check both 'file_content' and 'content' keys
                content_type = frame.get('file_content') or frame.get('content')
                if content_type == "valid_syntax": 
                    f.write("print('hello')")
                elif content_type == "invalid_syntax": 
                    f.write("print('hello'")
                else: 
                    f.write("")
        else:
            test_file = "non_existent_file.py"

        # 2. Construct Pygmentize Command
        cmd = ["pygmentize"]
        
        l_val = frame.get('lexer')
        if l_val == "valid_match": cmd += ["-l", "python"]
        elif l_val == "valid_mismatch": cmd += ["-l", "c"]
        elif l_val == "invalid": cmd += ["-l", "fakelexer"]
        
        f_val = frame.get('formatter')
        if f_val == "valid": cmd += ["-f", "html"]
        elif f_val == "invalid": cmd += ["-f", "fakeformat"]
        
        o_val = frame.get('output')
        if o_val == "file_path": cmd += ["-o", "out.html"]
        
        cmd.append(test_file)

        # 3. Execute
        print(f"Test #{i+1}: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            status = "PASS" if result.returncode == 0 else f"CAUGHT_ERROR (Code {result.returncode})"
            print(f"Result: {status}")
        except Exception as e:
            print(f"Result: CRASH/FAIL - {e}")

        # Cleanup
        if os.path.exists("test_input.py"): os.remove("test_input.py")
        if os.path.exists("out.html"): os.remove("out.html")

if __name__ == "__main__":
    # Check if a CSV filename was passed as an argument
    input_csv = sys.argv[1] if len(sys.argv) > 1 else None
    
    suite = generate_test_suite(input_csv)
    run_tests(suite)