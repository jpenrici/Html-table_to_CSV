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
EMPTY = ' '
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
    try:
        f = open(filename, "w")
        f.write(text)
        f.close()
        print("Save:", filename)
    except Exception:
        print("Error saving " + filename + " ...")
        exit(0) 


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


def prepare(path):
    # Load
    print("Load:", path)
    txt = load(path)

    # Check <table> tag
    if len(re.findall("<table.*?>", txt)) < 1:
        return ""

    # Process    
    print("File with Html Table ...")

    csv = ""
    row = []    
    table = []
    maxCols = 0
    maxRows = 0
    countCols = 0
    flag = False

    for line in txt.split(EOL):
        # Prepare
        line = line.replace(EOL, "")
        line = line.lstrip().rstrip()
        # Read
        if flag == False:
            # Check <table> tag
            if re.search("<table.*?>", line):
                flag = True
                continue
        if flag == True:
            # Start table reading
            if re.search("</table>", line):
                # Stop table reading
                flag = False
                # Rebuild table
                matrix = [["" for x in range(maxCols)] for y in range(maxRows)]
                print("Table: {0} x {1}".format(maxRows, maxCols))
                currentCol = 0
                currentRow = 0
                for row in table:
                    currentCol = 0
                    for col in row:
                        # print(col)
                        while len(matrix[currentRow][currentCol]) > 0:
                            currentCol += 1
                        if col[0] > 0 and col[1] == 0:  # only colspan
                            for dx in range(col[0]):
                                matrix[currentRow][currentCol + dx] = EMPTY
                        if col[0] == 0 and col[1] > 0:  # only rowspan
                            for dy in range(col[1]):
                                matrix[currentRow + dy][currentCol] = EMPTY
                        if col[0] > 0 and col[1] > 0:   # colspan and rowspan
                            for dx in range(col[0]):
                                for dy in range(col[1]):
                                    matrix[currentRow + dy][currentCol + dx] = EMPTY
                        matrix[currentRow][currentCol] = col[2]
                        currentCol += col[0]
                    currentRow += 1                       
                # print(matrix)
                # Convert CSV
                txt = ""
                for i in range(len(matrix)):
                    for j in range(len(matrix[i])):
                        txt += matrix[i][j] + DELIM
                    txt += EOL
                csv = txt
                continue
            # Check <tr> tag
            if line.startswith("<tr"):
                # Start reading a line structure
                row = []
                maxRows += 1
                countCols = 0
                continue
            if line.startswith("</tr>"):
                # Stop reading a line structure
                table += [row]
                continue
            # Check <td> and <th> tag
            if line.startswith("<td") or line.startswith("<th"):          
                # Check spans
                data = checkTag(line)
                row += [data]
                countCols += data[0]
                if maxCols < countCols:
                    maxCols = countCols
                maxRows += data[1]

    return csv


def test_checkTag():

    # Test <td> tag
    array = [0, 0, ""]
    assert checkTag("") == array
    assert checkTag("<") == array
    assert checkTag("<>") == array
    assert checkTag("<t >") == array
    assert checkTag("<tr>") == array
    assert checkTag("<t d >") == array
    assert checkTag("      <td>") == array
    assert checkTag("<td   >Text</td>") == [1, 0, "Text"]
    assert checkTag("<th   >Text</th>") == [1, 0, "Text"]
    assert checkTag("<td   >Text</th>") == [1, 0, "Text"]
    assert checkTag("<th   >Text</td>") == [1, 0, "Text"]
    assert checkTag("<td>" + EOL + "Text" + EOL + "</td>") == [1, 0, "Text"]
    assert checkTag("<td bgcolor=\"#000000\">Text</td>") == [1, 0, "Text"]
    assert checkTag("<td colspan=\"5\">Text</td>") == [5, 0, "Text"]
    assert checkTag("<th colspan=\"5\">Text</th>") == [5, 0, "Text"]
    assert checkTag("<td colspan=\"5\" rowspan=\"25\">Text</td>") == [5, 25, "Text"]
    assert checkTag("<th colspan=\"5\" rowspan=\"25\">Text</th>") == [5, 25, "Text"]
    assert checkTag("<td bgcolor=\"#FFFFFF\" rowspan=\"2\">Text Text</td>") == [1, 2, "Text Text"]
    print("CheckTag() is ok!")


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
    txt = prepare(fileIn)
    if len(txt) == 0:
        print ("Invalid file or does not html table!")
    else:
        # Terminal
        print(txt)
        # Output
        # save(fileOut, txt)
    print("Finished.")


if __name__ == "__main__":

   # Command Line
   #########################

   # main(sys.argv[1:])    

   # Checktag() function test
   ##########################

   test_checkTag()

   # File test
   ##########################
   
   main(["../html/test1.html"])
   main(["../html/test2.html"])
   main(["../html/test3.html"])
