Module Test_HtmlTable2Csv

    Sub Test_Table2Csv()

        Dim html As String
        Dim exp As String
        Dim res As String

        Dim home As String = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\html\"

        ' 0 - non-existent table
        html = Load(home + "test0.html")
        exp = ""
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 1 - basic
        html = Load(home + "test1.html")
        exp = "A;B;C" + EOL + "1;2;3" + EOL + "4;5;6" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 2 - colspan
        html = Load(home + "test2.html")
        exp = "A; ;B" + EOL + "1;2;3" + EOL + "4;5;6" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 3 - rowspan
        html = Load(home + "test3.html")
        exp = "A;1" + EOL + "B;2" + EOL + " ;3" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 4 - colspan and rowspan
        html = Load(home + "test4.html")
        exp = "1;2; ; ; " + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 5 - single line
        html = Load(home + "test5.html")
        exp = "A;B; ; ; " + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 6 - two tables
        html = Load(home + "test6.html")
        exp = "A;B;C" + EOL + "1;2;3" + EOL + "4;5;6" + EOL + "D;E;F" + EOL + "7;8;9" + EOL + " ;10;11" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 7 - only table
        html = Load(home + "test7.html")
        exp = "A;B;C" + EOL + "1;2;3" + EOL + "4;5;6" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 8 - broken table
        html = Load(home + "test8.html")
        exp = "A;B;C" + EOL + "1;2;3" + EOL + "4;5" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 9 - broken tables
        html = Load(home + "test9.html")
        exp = "A;B;C" + EOL + "1;2;3" + EOL + "4;5" + EOL + "A;B;C" + EOL + "1;2;3" + EOL + "4;5" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 10 - extra
        html = Load(home + "test10.html")
        exp = "1;2; ; ; " + EOL + " ;3;4;5;6" + EOL + "7;8;9;10;11" + EOL + " ; ; ; ; ;12" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        ' 11 - <td></td>
        html = Load(home + "test11.html")
        exp = "AA;BB;CC" + EOL + " ;  ;1111" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        Console.WriteLine("Test delimiter ...")
        html = Load(home + "test1.html")
        exp = "A" + TAB + "B" + TAB + "C" + EOL +
              "1" + TAB + "2" + TAB + "3" + EOL +
              "4" + TAB + "5" + TAB + "6" + EOL
        res = StrTable2Csv(html, TAB)
        Debug.Assert(exp = res)

        Console.WriteLine("Test string ...")
        html = "<table><tr><th>AA</th><th>BB</th><th>CC</th></tr>" +
               "<tr><td>11</td><td>22</td><td>33</td></tr>" +
               "<tr><td>44</td><td>55</td><td>66</td></tr>" +
               "</table>"
        exp = "AA" + TAB + "BB" + TAB + "CC" + EOL +
              "11" + TAB + "22" + TAB + "33" + EOL +
              "44" + TAB + "55" + TAB + "66" + EOL
        res = StrTable2Csv(html, TAB)
        Debug.Assert(exp = res)

        html = "<table><th>AA</th><td>BB</td><td>CC</td></table>"
        exp = "AA" + TAB + "BB" + TAB + "CC" + EOL
        res = StrTable2Csv(html, TAB)
        Debug.Assert(exp = res)

        Console.WriteLine("Test with incomplete tables ...")
        html = "<table><th>AA</th><td>Error!</table>"
        exp = "AA" + EOL
        res = StrTable2Csv(html)
        Debug.Assert(exp = res)

        html = "<table><th>AAA</th><td>Error" + EOL + "<table>"
        exp = "AAA" + EOL
        res = StrTable2Csv(html, TAB)
        Debug.Assert(exp = res)

        Console.WriteLine("Everything is OK!")

    End Sub

    Sub Test_ChackTag()

        ' Test <td> and <th> tag
        Dim arr() As String = {"0", "0", ""}
        Debug.Assert(IsArrayEqual(CheckTag("", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("<", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("<>", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("<t >", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("<tr>", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("<t d >", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("      <td>", True), arr))
        Debug.Assert(IsArrayEqual(CheckTag("<td></td>", True), {"1", "0", ""}))
        Debug.Assert(IsArrayEqual(CheckTag("<th>   </th>", True), {"1", "0", "   "}))
        Debug.Assert(IsArrayEqual(CheckTag("<td   >Text</td>", True), {"1", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<th   >Text</th>", True), {"1", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<td   >Text</th>", True), {"1", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<th   >Text</td>", True), {"1", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<td>" + EOL + "Text" + EOL + "</td>", True), {"1", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<td bgcolor=""#000000"">Text</td>", True), {"1", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<td colspan=""5"">Text</td>", True), {"5", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<th colspan=""5"">Text</th>", True), {"5", "0", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<td colspan=""5"" rowspan=""25"">Text</td>", True), {"5", "25", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<th colspan=""5"" rowspan=""25"">Text</th>", True), {"5", "25", "Text"}))
        Debug.Assert(IsArrayEqual(CheckTag("<td bgcolor=""#FFFFFF"" rowspan=""2"">Text Text</td>", True), {"1", "2", "Text Text"}))
        Console.WriteLine("CheckTag() is OK!")

    End Sub

    Private Function IsArrayEqual(arr1 As Array, arr2 As Array) As Boolean

        Dim result As Boolean
        result = (arr1.Length >= 3 And arr2.Length >= 3) And
            (arr1(0) = arr2(0) And arr1(1) = arr2(1) And arr1(2) = arr2(2))
        If Not result Then
            Console.WriteLine(String.Format("Expected: [{0}, {1}, {2}]", arr2(0), arr2(1), arr2(2)))
            Console.WriteLine(String.Format("Result  : [{0}, {1}, {2}]", arr1(0), arr1(1), arr1(2)))
        End If

        IsArrayEqual = result

    End Function

End Module
