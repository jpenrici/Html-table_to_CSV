Imports System.IO
Imports System.Text
Imports System.Text.RegularExpressions

'
' HTML Table to CSV
'

Friend Module HtmlTable2Csv

    Public Const EOL As String = vbLf
    Public Const TAB As String = vbTab
    Public Const DELIM As String = ";"
    Public Const SPACE As String = " "

    Public Sub Main(args As String())

        'HtmlTable2Csv
        Run(args)

        'Test
        'Test_HtmlTable2Csv.Test_ChackTag()
        'Test_HtmlTable2Csv.Test_Table2Csv()

    End Sub

    Private Sub Run(args As String())

        Dim msg As String
        msg = "Use: HtmlTable2Csv.exe if=inputfile of=outputfile.csv delim=delimiter"

        Dim msgHelp As String
        msgHelp = "For delimiters with special characters use quotation marks. " +
                  "For example: delim='\\t' or delim=TAB"

        If args.Length < 1 Then
            Console.WriteLine(msg)
            Exit Sub
        End If

        Dim fileIn As String = ""
        Dim fileOut As String = ""
        Dim delimiter As String = ""

        For Each arg In args
            If arg.StartsWith("if=") And fileIn = "" Then
                fileIn = arg.Substring(3)
            End If
            If arg.StartsWith("of=") And fileOut = "" Then
                fileOut = arg.Substring(3)
            End If
            If arg.StartsWith("delim=") And delimiter = "" Then
                delimiter = arg.Substring(6)
            End If
            If arg.StartsWith("--help") Or arg.StartsWith("-h") Then
                Console.WriteLine(msg)
                Console.WriteLine(msgHelp)
                Exit Sub
            End If
        Next

        If fileIn = "" Then
            Console.WriteLine(msg)
            Exit Sub
        End If

        If fileOut = "" Then
            fileOut = fileIn.Replace(".", "_") + ".csv"
        End If

        Console.WriteLine("Input : " + fileIn)
        Console.WriteLine("Output: " + fileOut)

        msg = "Delimiter: [" + delimiter + "] "
        If delimiter = "" Then
            delimiter = DELIM
            msg += "(Empty! Use Default '" + delimiter + "')"
        End If
        If delimiter = "\\t" Or delimiter.ToLower = "tab" Then
            delimiter = TAB
            msg += "Tab"
            Console.WriteLine(msg)
        End If

        Dim text As String = Table2Csv(fileIn, delimiter)
        If Len(text) = 0 Then
            Console.WriteLine("Invalid file or does not html table!")
        Else
            'Output
            Save(fileOut, text)
        End If

        Console.WriteLine("Finished.")

    End Sub

    Public Function CheckTag(ByVal line As String, Optional ByVal viewResult As Boolean = False) As Array
        'Check string and get data if it's an <td> or <th> tag

        'Standard return
        '{column, currentRow, text}
        Dim data() As String = {"0", "0", ""}

        'Prepare
        line = line.Replace(EOL, "")
        line = RTrim(LTrim(line))

        Dim result As Boolean
        result = (Len(line) > 0) And (line.StartsWith("<td") Or line.StartsWith("<th")) And
            (line.EndsWith("</td>") Or line.EndsWith("</th>"))

        If result Then
            'Find cell span
            data = {"1", "0", ""}
            Dim cellSpan() As String = {"colspan", "rowspan"}
            For i = 0 To 1
                Try
                    Dim pattern = cellSpan(i) + "=\""[0-9]+"""
                    Dim m As Match = Regex.Match(line, pattern, RegexOptions.IgnoreCase)
                    If m.Success Then
                        Dim substr As String = m.Value
                        Dim num As String = Regex.Match(substr, "[0-9]+").Value
                        data(i) = num
                    End If
                Catch
                    Console.WriteLine("Regex Error!")
                End Try
            Next i
            'Find value
            data(2) = Regex.Replace(line, "<.?t[d,h].*?>", "")
        End If

        'Result
        If viewResult Then
            Console.WriteLine(line)
            Console.WriteLine(String.Format("[{0}, {1}, {2}]", data(0), data(1), data(2)))
        End If

        CheckTag = data

    End Function

    Public Function StrTable2Csv(ByVal text As String, Optional ByVal delimiter As String = DELIM) As String
        'input : string (Html), output : string (CSV)

        Dim csv As String = ""

        If Len(text) = 0 Then
            Console.WriteLine("Empty text!")
        Else
            'Check <table> tag
            If Not Regex.IsMatch(text, "<table.*?>", RegexOptions.IgnoreCase) Then
                Console.WriteLine("Html table not found!")
            Else
                Console.WriteLine("Html Table found! Build CSV ... ")

                'Prepare
                text = text.Replace(TAB, "")
                text = text.Replace("></td>", "> </td>")
                text = text.Replace("</table>", EOL + "</table>")
                text = text.Replace("><", ">" + EOL + "<")

                'Process    
                Dim table As New ArrayList
                Dim rows As Integer = 0
                Dim maxCols As Integer = 0
                Dim maxRows As Integer = 0
                Dim flagTable As Boolean = False

                Dim lines() As String = Split(text, EOL)
                For i = 0 To lines.Length - 1
                    'Prepare
                    Dim line As String = lines(i).Replace(EOL, "")
                    line = RTrim(LTrim(line))
                    'Read
                    If flagTable = False Then
                        'Check <table> tag
                        If line.StartsWith("<table") Then
                            rows = 0
                            table.Clear()
                            flagTable = True
                            Continue For
                        End If
                    End If
                    If flagTable = True Then
                        'Check <tr> tag
                        If line.StartsWith("<tr") Then
                            maxRows += 1
                            Continue For
                        End If
                        If line.StartsWith("</tr>") Then
                            rows += 1
                            Continue For
                        End If
                        'Check <td> And <th> tag
                        If line.StartsWith("<td") Or line.StartsWith("<th") Then
                            Dim data As Array = CheckTag(line, False)
                            maxCols += Convert.ToDecimal(data(0))
                            maxRows += Convert.ToDecimal(data(1))
                            Dim col() As String = {data(0), data(1), data(2), rows}
                            table.Add(col)
                            Continue For
                        End If
                        'Check other cases
                        Dim state As Integer
                        state = If(line.StartsWith("<table"), 1, 0)      'table reopened            
                        state = If(line.StartsWith("</table"), 2, state) 'table closed 
                        state = If(i >= lines.Length - 2, 3, state)      'end of text  
                        'Table To CSV
                        If state > 0 Then
                            flagTable = (state = 1)
                            'Rebuild table
                            Dim matrix(,) As String = Array2D(maxRows + 1, maxCols + 1, "")
                            'ViewArray(matrix, maxRows, maxCols)
                            Dim y As Integer = 0
                            Dim x As Integer = 0
                            Dim currentRow As Integer = 0
                            For Each currentCol In table
                                Dim colspan As Integer = currentCol(0)
                                Dim rowspan As Integer = currentCol(1)
                                Dim value As String = currentCol(2)
                                If currentRow <> currentCol(3) Then
                                    currentRow = currentCol(3)
                                    y += 1
                                    x = 0
                                End If
                                While Len(matrix(y, x)) > 0 And x < maxCols '!Empty
                                    x += 1
                                End While
                                If colspan > 0 And rowspan = 0 Then         'only colspan
                                    For dx = 0 To colspan - 1
                                        matrix(y, x + dx) = SPACE
                                    Next dx
                                End If
                                If colspan = 0 And rowspan > 0 Then         'only rowspan
                                    For dy = 0 To rowspan - 1
                                        matrix(y + dy, x) = SPACE
                                    Next dy
                                End If
                                If colspan > 0 And rowspan > 0 Then         'colspan And rowspan
                                    For dx = 0 To colspan - 1
                                        For dy = 0 To rowspan - 1
                                            matrix(y + dy, x + dx) = SPACE
                                        Next dy
                                    Next dx
                                End If
                                matrix(y, x) = value
                                x += colspan
                            Next currentCol
                            'ViewArray(matrix, maxRows, maxCols)
                            'Convert CSV
                            csv += Array2Str(matrix, Math.Min(rows, maxRows), maxCols, delimiter)
                            table.Clear()
                        End If
                    End If
                Next i
            End If
        End If

        Console.WriteLine(csv)

        StrTable2Csv = csv

    End Function

    Public Function Table2Csv(ByVal path As String, ByVal delimiter As String) As String
        'input : file text (Html), output : string (CSV)

        Console.WriteLine("Load: " + path)
        Dim text As String = Load(path)
        Dim csv As String = ""

        If Len(text) < 0 Then
            Console.WriteLine("Empty file!")
        Else
            csv = StrTable2Csv(text, delimiter)
        End If

        Table2Csv = csv

    End Function

    Public Function Load(ByVal filename As String) As String

        Dim text As String = ""

        If Len(filename) > 0 Then
            Try
                Dim fileReader As String
                fileReader = FileIO.FileSystem.ReadAllText(filename, Encoding.UTF8)
                text = fileReader
            Catch
                Console.WriteLine("Error: " + filename)
            End Try
        End If

        Load = text

    End Function

    Private Sub Save(ByVal filename As String, ByVal text As String)

        If Len(filename) > 0 And Len(text) > 0 Then
            Try
                Dim path As String = filename
                Dim file As StreamWriter
                file = FileIO.FileSystem.OpenTextFileWriter(path, True)
                file.WriteLine(text)
                file.Close()
                Console.WriteLine("Save: " + filename)
            Catch
                Console.WriteLine("Error saving " + filename + " ...")
            End Try
        End If

    End Sub

    Private Sub ViewArray(ByVal arr As Array, ByVal rows As Integer, ByVal cols As Integer)

        Try
            For r = 0 To rows
                Dim text As String = ""
                For c = 0 To cols
                    text += """" + arr(r, c) + """" + ","
                Next c
                text = text.TrimEnd(",")
                Console.WriteLine("({0})[{1}]", r, text)
            Next r
        Catch
            Console.WriteLine("Error: Array!")
        End Try

    End Sub

    Private Function Array2Str(ByVal arr As Array, ByVal rows As Integer, ByVal cols As Integer,
                               Optional ByVal delimiter As String = DELIM) As String

        Dim text As String = ""
        Dim temp As String
        Try
            For r = 0 To rows
                temp = ""
                For c = 0 To cols
                    temp += arr(r, c) + delimiter
                Next c
                temp = temp.TrimEnd(delimiter)
                If temp <> "" Then
                    text += temp + EOL
                End If
            Next r
        Catch
            Console.WriteLine("Error: Array!")
        End Try

        Array2Str = text

    End Function

    Private Function Array2D(ByVal rows As Integer, ByVal cols As Integer,
        ByVal value As String) As Array

        Dim arr(rows, cols) As String
        For r = 0 To rows
            For c = 0 To cols
                arr(r, c) = value
            Next c
        Next r

        Array2D = arr

    End Function

End Module
