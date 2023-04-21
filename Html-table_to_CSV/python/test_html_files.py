from HtmlTable2Csv import *

result = [
# 0 - non-existent table
"",

# 1 - basic
"""\
A;B;C
1;2;3
4;5;6
""",

# 2 - colspan
"""\
A; ;B
1;2;3
4;5;6
""",

# 3 - rowspan
"""\
A;1
B;2
 ;3
""",

# 4 - colspan and rowspan
"""\
1;2; ; ; 
""",

# 5 - single line
"""\
A;B; ; ; 
""",

# 6 - two tables
"""\
A;B;C
1;2;3
4;5;6
D;E;F
7;8;9
 ;10;11
""",

# 7 - only table
"""\
A;B;C
1;2;3
4;5;6
""",

# 8 - broken table
"""\
A;B;C
1;2;3
4;5
""",

# 9 - broken tables
"""\
A;B;C
1;2;3
4;5
A;B;C
1;2;3
4;5
""",

# 10 - extra
"""\
1;2; ; ; 
 ;3;4;5;6
7;8;9;10;11
 ; ; ; ; ;12
""",

# 11 - <td></td>
"""\
AA;BB;CC
 ;  ;1111
"""

]

def test():

    for i in range(len(result)):
        print("Test", i, " ...")
        assert table2csv("../html/test" + str(i) + ".html") == result[i]

    print("Test delimiter ...")
    assert table2csv("../html/test1.html", '\t') == result[1].replace(';', '\t')

    print("Test string ...")
    html = """<table>
              <tr><th>AA</th><th>BB</th><th>CC</th></tr>
              <tr><td>11</td><td>22</td><td>33</td></tr>
              <tr><td>44</td><td>55</td><td>66</td></tr>
              </table>"""
    res = "AA\tBB\tCC\n11\t22\t33\n44\t55\t66\n"
    assert strTable2csv(html, '\t') == res

    html = "<table><th>AA</th><td>BB</td><td>CC</td></table>"
    res = "AA\tBB\tCC\n"
    assert strTable2csv(html, '\t') == res

    print("Test with incomplete tables ...")
    html = "<table><th>AA</th><td>Error!</table>"
    res = "AA\n"
    assert strTable2csv(html) == res

    html = """<table><th>AAA</th><td>Error
              <table>"""
    res = "AAA\n"
    assert strTable2csv(html, '\t') == res

    print("Everything is OK!")


if __name__ == '__main__':
    test()
