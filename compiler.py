import re

def formatFile(input):
    operators = set(['+', '-', '*', '/', '(', ')', '=', ",", ":"])
    
    with open(input, "r") as original_file:
        lines = original_file.readlines()

    modified_lines = []
    inside_comment = False
    in_quotes = False
    count = 0

    check_parentheses(lines)
    check_write_spelling(lines)

    for line in lines:

        if "integer" in line:
            parse_line(line)

        count += 1
  
        # Rule a: Remove comments
        if(line[:2] == "(*"):
            inside_comment = True
            continue

        line = line.split('(*')[0].strip()

        # Rule b: Remove blank lines also removes the comment if it ends in *)
        if line:
            if(line[-2:] == "*)"):
                inside_comment = False
                continue
            if(inside_comment == True):
                continue

            # Rule c: Remove extra spaces then adds spaces according to listed operators above
            modified_line = ''.join(line.split())
            if(modified_line[:7] == "program"):
                modified_line = modified_line[:7] + " " + modified_line[7:]
          
            #For removing spaces after operators
            i = 0

            while i < len(modified_line):

                #To ignore formatting quotes
                if(modified_line[i] == '"'):
                    i+=1
                    while(modified_line[i] != '"'):
                        i+=1
                    i+=1

                if(modified_line[i] in operators):
                    if(i+1 < len(modified_line) and in_quotes == False):
                        if(modified_line[i] == '"'):
                            in_quotes = not in_quotes
                            i += 1
                            continue
                        modified_line = modified_line[:i+1] + " " + modified_line[i+1:]
                    i+=1
                i += 1

            #For removing spaces before operators
            i = 0

            while i < len(modified_line):

                #To ignore formatting quotes
                if(modified_line[i] == '"'):
                    i+=1
                    while(modified_line[i] != '"'):
                        i+=1
                    i+=1
                
                if(modified_line[i] in operators):
                    modified_line = modified_line[:i] + " " + modified_line[i:]
                    i+=1
                i += 1
            
            #In the chance that ";" has formatting issues, it will be fixed. This happens because of ")" adding spaces
            if(modified_line[-1] == ";" and modified_line[-2] != " "):
                modified_line = modified_line[:len(modified_line)-1] + " ;"
            
            if modified_line[-1] != ";" and "begin" not in modified_line and "end." not in modified_line and "var" not in modified_line:
                print("Expected ; or mispelled Keyword(s) at line ", count)
                exit()
            modified_lines.append(modified_line)


    # Write the modified content to a new file
    with open("final23.txt", "w") as modified_file:
        modified_file.write('\n'.join(modified_lines))

    print("File 'final23.txt' parsed successfully.")

def check_write_spelling(lines):

    for line_number, line in enumerate(lines, start=1):
        words = line.split()

        for word in words:
            # Check if the word is "write" with exact case-sensitive comparison
            if word == "write":
                print(f"Error: Possible misspelling of 'write' at line {line_number}")


def parse_line(line):
    
    variables = []
    commas = []
    word = ""

    for l in line:

        if l == ",":
            commas.append(",")

            if "," not in word:
                if word.isspace() == False:
                    variables.append(word)
            word = ""
            continue
        
        if l == ":" or l == ";":
            continue
        
        if "integer" in word:
            continue

        word += l

        if "integer" not in word and l.isspace():
            if len(word)>=1 and word.isspace() == False:
                variables.append(word)
            word = ""
            continue

    if len(variables)-1 != len(commas):
        print("Check commas by declarations.")
        exit()

        
def check_parentheses(lines):
    stack = []

    for line_number, line in enumerate(lines, start=1):
        for char_number, char in enumerate(line, start=1):
            if char == '(':
                stack.append((line_number, char_number, '('))
            elif char == ')':
                if not stack or stack[-1][2] != '(':
                    print(f"Error: Expected '(' at line {line_number}, character {char_number}")
                    exit()
                else:
                    stack.pop()

    for line_number, char_number, expected_char in stack:
        print(f"Error: Expected '{expected_char}' at line {line_number}, character {char_number}")
        exit()

def compiler(tokens):
    #Parsing table

    states = {
        'A':{"program": ["program","B",";","var","D","begin","H","end."]},

        'B':{"a": ["X","C"], "b": ["X","C"], "c": ["X","C"], "d": ["X","C"], "w": ["X","C"], "f": ["X","C"],},

        'C':{"a": ["X","C"], "b": ["X","C"], "c": ["X","C"], "d": ["X","C"], "w": ["X","C"], "f": ["X","C"], "0": ["W","C"],
             "1": ["W","C"], "2": ["W","C"], "3": ["W","C"], "4": ["W","C"], "5": ["W","C"], "6": ["W","C"], "7": ["W","C"], "8": ["W","C"], 
             "9": ["W","C"], "/": None, ";": None, ":": None, ",": None, "=": None, '"': None, "+": None, "-": None, "*": None, ")": None
             },

        'D':{"a": ["E",":","G",";"], "b": ["E",":","G",";"], "c": ["E",":","G",";"], "d": ["E",":","G",";"], "w": ["E",":","G",";"], 
             "f": ["E",":","G",";"], 
             },

        'E':{"a": ["B","F"], "b": ["B","F"], "c": ["B","F"], "d": ["B","F"], "w": ["B","F"], "f": ["B","F"],},

        'F':{":": None, ",": [",","E"], },
    
        'G':{"integer":["integer"] },

        'H':{"a": ["J","I"], "b": ["J","I"], "c": ["J","I"], "d": ["J","I"], "w": ["J","I"], "f": ["J","I"], "write": ["J","I"], },

        'I':{"a": ["H"], "b": ["H"], "c": ["H"], "d": ["H"], "w": ["H"], "f": ["H"], "end.": None, "write": ["H"]},

        'J':{"a": ["N"], "b": ["N"], "c": ["N"], "d": ["N"], "w": ["N"], "f": ["N"], "write": ["K"]},

        'K':{"write": ["write", "(", "L"]},

        'L':{"a": ["B",")", ";"], "b": ["B",")", ";"], "c": ["B",")", ";"], "d": ["B",")", ";"], "w": ["B",")", ";"], "f": ["B",")", ";"], 
             '"value="' : ["M", "B", ")", ";"]},

        'M':{'"value="': ['"value="', ","], },

        'N':{"a": ["B","=","O",";"], "b": ["B","=","O",";"], "c": ["B","=","O",";"], "d": ["B","=","O",";"], "w": ["B","=","O",";"], 
             "f": ["B","=","O",";"], "+": ["Q","P"], "-": ["Q","P"], "-": ["Q","P"]},

        'O':{"a": ["Q","P"], "b": ["Q","P"], "c": ["Q","P"], "d": ["Q","P"], "w": ["Q","P"], "f": ["Q","P"], "0": ["Q","P"], 
             "1": ["Q","P"], "2": ["Q","P"], "3": ["Q","P"], "4": ["Q","P"], "5": ["Q","P"], "6": ["Q","P"], "7": ["Q","P"], 
             "8": ["Q","P"], "9": ["Q","P"],"+": ["Q","P"],"-": ["Q","P"], "(": ["Q","P"],},

        'P':{"+": ["+","Q","P"], "-": ["-","Q","P"], ";": None, ")": None},

        'Q':{"a":["S","R"], "b":["S","R"], "c":["S","R"], "d":["S","R"], "w":["S","R"], "f":["S","R"], "0":["S","R"], "1":["S","R"], "2":["S","R"], "3":["S","R"], 
             "4":["S","R"], "5":["S","R"], "6":["S","R"], "7":["S","R"], "8":["S","R"], "9":["S","R"], "+": ["S","R"],"-": ["S","R"], "(": ["S","R"],},
        
        'R':{"/": ["/", "S", "R"], ";": None, ",": None, "+": None, "-": None, "*": ["*","S","R"], ")": None},

        'S':{"a": ["B"], "b": ["B"], "c": ["B"], "d": ["B"], "w": ["B"], "f": ["B"], "0": ["T"], "1": ["T"], "2": ["T"], "3": ["T"], 
             "4": ["T"], "5": ["T"], "6": ["T"], "7": ["T"], "8": ["T"], "9": ["T"], "(": ["(","O",")"] },

        'T':{"0": ["W","U"], "1": ["W","U"], "2": ["W","U"], "3": ["W","U"], "4": ["W","U"], "5": ["W","U"], "6": ["W","U"], 
             "7": ["W","U"], "8": ["W","U"], "9": ["W","U"], "+": ["V", "W", "U"], "-": ["V", "W", "U"],},

        'U':{"0": ["W","U"], "1": ["W","U"], "2": ["W","U"], "3": ["W","U"], "4": ["W","U"], "5": ["W","U"], "6": ["W","U"], 
             "7": ["W","U"], "8": ["W","U"], "9": ["W","U"], "/": None, ";": None, ",": None, "+": None, "-": None, "*": None, ")": None},

        'V':{"+": ["+"], "-": ["-"]},

        'W':{"0":["0"], "1":["1"], "1":["1"], "2":["2"], "3":["3"], "4":["4"], "5":["5"], "6":["6"], "7":["7"], "8":["8"], "9":["9"], },

        'X':{"a":["a"], "b":["b"], "c":["c"], "d":["d"], "w":["w"], "f":["f"], },

    }

    reserved = {"program", "var", "begin", "end.", "integer", "write", '"value="'}


    stack = ['A']

    for token in tokens:
        while stack:
            current = stack.pop()
            
            if current == token:
                break

            #Treating multi-char tokens as a single token, check validity block
       
            if current in states and token not in reserved:
                istack = [current]
                for itoken in token:
                    while istack:
                        icurrent = istack.pop()
                        if icurrent == itoken:
                            break
                        if itoken not in states[icurrent]:
                            print("Expected: ",end = "")
                            for item in states[icurrent]:
                                print("'",item,"'", " or " ,end = "")
                            print("But received ", "'", itoken ,"'")
                            return False
                
                        goto = states[icurrent][itoken]
                        if goto is not None:
                            goto = goto[::-1]
                            for state in goto:
                                if state is not None:
                                    istack.append(state)
                if istack:
                    for i in istack:
                        stack.append(i)
                    break  

            else:
                if token not in states[current]:
                    print("Expected: ",end = "")
                    for item in states[current]:
                        print("'",item,"'", " or " ,end = "")
                    print("But received ", "'", token ,"'")
                    return False
            
                goto = states[current][token]

                if goto is not None:
                    for state in reversed(goto):
                        if state is not None:
                            stack.append(state)
    if not stack:
        return True
            


def tokenization(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    array_of_lines = []

    for line in lines:
        words = line.split()
        array_of_lines.extend(words)

    return array_of_lines

def convert(input):
    print("converted code: \n")
    with open(input, "r") as original_file:
        lines = original_file.readlines()
    reserved = {"program", "var", "begin", "end.", "integer", "write"}
    for line in lines:
        if "program" in line or "var" in line or "end." in line or "begin" in line or "integer" in line:
            continue
        print(line.replace(";", "").replace("write", "print"))
        
    
if __name__ == "__main__":
    parsed = formatFile("finalv1.txt")

    formatted = "final23.txt"

    tokens = tokenization(formatted)


    #must haves
    reserved = {"program", "var", "begin", "end.", "integer"}
    failed = False

    for word in reserved:
        if word not in tokens:
            print("Error, the keyword " ,word, " was expected.")
            failed = True
        if word == "end." and word not in tokens:
            print("Missing '.' ")



    if failed == False:
        compiled = compiler(tokens)
        if compiled:
            print("File ", formatted, " compiled successfully")
            convert(formatted)

    



