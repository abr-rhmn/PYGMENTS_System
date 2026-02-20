import itertools
import subprocess
import os

# Input Space
partitions = {
    "file_existence": ["exists", "missing"],
    "file_content": ["empty", "valid_py", "invalid_py", "random_text"],
    "lexer_flag": ["omitted", "valid_match", "invalid"],
    "formatter_flag": ["omitted", "valid", "invalid"]
}


content_data = {
    "empty": "",
    "valid_py": "def test():\n    return True",
    "invalid_py": "def test() return True", # Missing colon
    "random_text": "This is not code, just a normal sentence."
}

def generate_and_run():
    all_frames = list(itertools.product(*partitions.values()))
    
    for i, (f_exists, f_type, lex_flag, form_flag) in enumerate(all_frames):
        if f_exists == "missing" and f_type != "empty":
            continue

        # Case filling
        input_filename = "test_input.py" if f_exists == "exists" else "non_existent.py"
        
        if f_exists == "exists":
            with open(input_filename, "w") as f:
                f.write(content_data[f_type])

        # Command construction
        cmd = ["pygmentize"]
        
        if lex_flag == "valid_match": cmd += ["-l", "python"]
        elif lex_flag == "invalid": cmd += ["-l", "fakelexer"]
        
        if form_flag == "valid": cmd += ["-f", "html"]
        elif form_flag == "invalid": cmd += ["-f", "fakeformat"]

        cmd.append(input_filename)

        # execute and log
        print(f"Test Frame #{i+1}: File:{f_exists}, Content:{f_type}, Lexer:{lex_flag}")
        print(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            status = "PASS" if result.returncode == 0 else f"HANDLED_ERR (Code {result.returncode})"
            print(f"Result: {status}\n")
        except Exception as e:
            print(f"Result: CRASH - {e}\n")

        if os.path.exists("test_input.py"): os.remove("test_input.py")

if __name__ == "__main__":
    generate_and_run()