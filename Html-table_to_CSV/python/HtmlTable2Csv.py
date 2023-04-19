# -*- Mode: Python; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-

'''
    HTML Table to CSV
    
    Use:
        python3 HtmlTable2Csv.py <inputfile> <outputfile.csv>

'''

import os
import re
import sys

EOL = '\n'
DELIM = ';'
SPACE  = ' '
IGNORE = ["\x00", "\n"]


def load(filename):
    data = ""
    try:
        f = open(filename, 'rb')
        lines = f.readlines()
        for line in lines:
            txt = "".join([(chr(x) if not chr(x) in IGNORE else "") for x in line])
            data += txt.lstrip().rstrip() + EOL
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


def table2csv(path):
    # Load 
    print("Load:", path)
    txt = load(path)

    if len(txt) == 0:
        print("Empty file!")
        return ""

    # Check <table> tag
    if len(re.findall("<table.*?>", txt)) < 1:
        print("Html table not found!")
        return ""

    # Prepare
    txt = txt.replace("><", ">" + EOL + "<") 

    # Process    
    print("File with Html Table! Build CSV ... ")

    csv = ""
    row = []
    table = []
    maxCols = 0
    maxRows = 0
    flag = False

    for line in txt.split(EOL):
        # Prepare
        line = line.replace(EOL, "")
        line = line.lstrip().rstrip()
        # Read
        if flag == False:
            # Check <table> tag
            if re.search("<table.*?>", line):
                table = []
                flag = True
                continue
        if flag == True:
            # Check <tr> tag
            if line.startswith("<tr"):
                row = []
                maxRows += 1
                continue
            if line.startswith("</tr>"):
                table += [row]
                continue
            # Check <td> and <th> tag
            if line.startswith("<td") or line.startswith("<th"):          
                data = checkTag(line)
                maxCols += data[0]
                maxRows += data[1]
                row += [data]
                continue
            if re.search("</table>", line):
                flag = False
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
                        txtRow += matrix[i][j] + DELIM
                    txtTable += txtRow.rstrip(DELIM) + EOL
                csv += txtTable        

    return csv


def main(argv):
    if (len(argv) < 1):
        print ('Use => python3 HtmlTable2Csv.py <inputfile> <outputfile.csv>')
        exit(0)
    if (len(argv) == 1):
        fileIn = argv[0]
        fileOut = fileIn + ".csv"
    if (len(argv) > 1):
        fileIn = argv[0]
        fileOut = argv[1]       
    print ("Input : " + fileIn)
    print ("Output: " + fileOut)
    txt = table2csv(fileIn)
    if len(txt) == 0:
        print ("Invalid file or does not html table!")
    else:
        # Terminal
        print(txt)
        # Output
        save(fileOut, txt)

    print("Finished.")


if __name__ == "__main__":
   main(sys.argv[1:])
