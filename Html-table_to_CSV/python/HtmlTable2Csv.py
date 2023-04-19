# -*- Mode: Python; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-

'''
    HTML Table to CSV
    
    Use:
        python3 HtmlTable2Csv.py if=inputfile of=outputfile.csv delim=delimiter
        python3 HtmlTable2Csv.py --help

'''

import os
import re
import sys

EOL = '\n'
TAB = '\t'
DELIM = ';'
SPACE  = ' '
IGNORE = ["\x00", "\n"]


def load(filename):
    data = ""
    try:
        f = open(filename, 'rb')
        lines = f.readlines()
        for line in lines:
            text = "".join([(chr(x) if not chr(x) in IGNORE else "") for x in line])
            data += text.lstrip().rstrip() + EOL
        f.close()
    except IOError:
         print("Error:", filename)
    return data  # string


def save(filename, text):
    if len(filename) == 0:
        print("Empty file name!")
        return

    try:
        f = open(filename, "w")
        f.write(text)
        f.close()
        print("Save:", filename)
    except Exception:
        print("Error saving " + filename + " ...")


def checkTag(line):
    '''Check string and get data if it's an <td> or <th> tag'''

    # Standard return
    # [column, row, text]
    data = [0, 0, ""]

    # Prepare
    line = line.replace(EOL, "")
    line = line.lstrip().rstrip()
    if len(line) == 0:
        return data
    
    # Check <td> or <th> tag
    if not line.startswith("<td") and not line.startswith("<th"):
        return data
    if not line.endswith("</td>") and not line.endswith("</th>"):
        return data

    # Find cell span
    data = [1, 0, ""]
    cellSpan = ["colspan", "rowspan"]
    for i in range(0, 2):
        result = re.search(cellSpan[i] + "=\"[0-9]+\"", line)
        if result:
            pos = result.span()
            substr = line[pos[0]:pos[1]]
            result = re.search("[0-9]+", substr)
            pos = result.span()
            data[i] = int(substr[pos[0]:pos[1]])

    # Find value
    data[2] = re.sub("<.?t[d,h].*?>", "", line)

    # Result
    # print(data)

    return data


def strTable2csv(text, delimiter=DELIM):
    ''' input : string (Html), output : string (CSV) '''

    if len(text) == 0:
        print("Empty text!")
        return ""

    # Check <table> tag
    if len(re.findall("<table.*?>", text)) < 1:
        print("Html table not found!")
        return ""

    # Prepare
    text = text.replace("></td>", "> </td>")
    text = text.replace("><", ">" + EOL + "<") 

    # Process    
    print("Html Table found! Build CSV ... ")

    csv = ""
    row = []
    table = []
    maxCols = 0
    maxRows = 0
    flagTable = False
    flagRow = False

    lines = text.split(EOL)
    for i in range(len(lines)):
        # Prepare
        line = lines[i].replace(EOL, "")
        line = line.lstrip().rstrip()
        # Read
        if flagTable == False:
            # Check <table> tag
            if re.search("<table.*?>", line):
                table = []
                flagTable = True
                continue
        if flagTable == True:
            # Check <tr> tag
            if line.startswith("<tr"):
                row = []
                maxRows += 1
                flagRow = True
                continue
            if line.startswith("</tr>"):
                table += [row]
                flagRow = False
                continue
            # Check <td> and <th> tag
            if line.startswith("<td") or line.startswith("<th"):       
                data = checkTag(line)
                maxCols += data[0]
                maxRows += data[1]
                row += [data]
                continue
            # Check other cases
            case = 1 if line.startswith("<table") else 0      # table reopened            
            case = 2 if line.startswith("</table") else case  # table closed 
            case = 3 if i == len(lines) - 1 else case         # is on the finish line  
            # Table to CSV      
            if case > 0:
                flagTable = case == 1
                if flagRow:  # last line is open
                    table += [row]              
                # Rebuild table
                matrix = [["" for x in range(maxCols)] for y in range(maxRows)]
                y = 0
                for row in table:
                    x = 0
                    for col in row:
                        colspan, rowspan, text = col
                        while len(matrix[y][x]) > 0:      # !Empty
                            x += 1
                        if colspan > 0 and rowspan == 0:  # only colspan
                            for dx in range(colspan):
                                matrix[y][x + dx] = SPACE 
                        if colspan == 0 and rowspan > 0:  # only rowspan
                            for dy in range(rowspan):
                                matrix[y + dy][x] = SPACE 
                        if colspan > 0 and rowspan > 0:   # colspan and rowspan
                            for dx in range(colspan):
                                for dy in range(rowspan):
                                    matrix[y + dy][x + dx] = SPACE 
                        matrix[y][x] = text
                        x += colspan
                    y += 1                       
                # Convert CSV
                txtTable = ""
                for i in range(min(len(table), len(matrix))):
                    txtRow = ""
                    for j in range(len(matrix[i])):
                        txtRow += matrix[i][j] + delimiter
                    txtTable += txtRow.rstrip(delimiter) + EOL
                csv += txtTable
                table = []

    print(csv)

    return csv


def table2csv(path, delimiter=DELIM):
    ''' input : file text (Html), output : string (CSV) '''

    # Load
    print("Load:", path)
    text = load(path)

    if len(text) == 0:
        print("Empty file!")
        return ""

    return strTable2csv(text, delimiter)


def main(argv):
    msg = """Use:
    python3 HtmlTable2Csv.py if=inputfile of=outputfile.csv delim=delimiter
    """
    msgHelp = """
    For delimiters with special characters use quotation marks.
    For example: delim='\\t' or delim=TAB
    """
    if (len(argv) < 1):
        print (msg)
        exit(0)
    fileIn, fileOut, delimiter = "", "", ""
    for arg in argv:
        if arg.startswith("if=") and fileIn == "":
            fileIn = arg[3::]
        if arg.startswith("of=") and fileOut == "":
            fileOut = arg[3:]
        if arg.startswith("delim=") and delimiter == "":
            delimiter = arg[6::]
        if arg.startswith("--help") or arg.startswith("-h"):
            print(msg)
            print(msgHelp)
            exit(0)            

    if (fileIn == ""):
        print (msg)
        exit(0)

    if (fileOut == ""):
        fileOut = fileIn + ".csv"
      
    print("Input : " + fileIn)
    print("Output: " + fileOut)

    msg = "Delimiter: [" + delimiter + "] "
    if (delimiter == ""):
        delimiter = DELIM
        msg += "(Empty! Use Default '" + delimiter + "')"
    if (delimiter == '\t' or delimiter == "\\t" or delimiter.lower() == "tab"):
        delimiter = TAB
        msg += "Tab"
    print(msg)

    text = table2csv(fileIn, delimiter)
    if len(text) == 0:
        print ("Invalid file or does not html table!")
    else:
        # Output
        save(fileOut, text)

    print("Finished.")


if __name__ == "__main__":
   main(sys.argv[1:])
