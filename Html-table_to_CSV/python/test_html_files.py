from HtmlTable2Csv import *

result = [
"",

"""\
A;B;C
1;2;3
4;5;6
""",

"""\
A; ;B
1;2;3
4;5;6
""",

"""\
A;1
B;2
 ;3
""",

"""\
1;2; ; ; 
""",

"""\
A;B; ; ; 
""",

"""\
A;B;C
1;2;3
4;5;6
D;E;F
7;8;9
 ;10;11
"""
]

def test():
    for i in range(len(result)):
        assert table2csv("../html/test" + str(i + 1) + ".html") == result[i]
    print("Everything is OK!")


if __name__ == '__main__':
    test()
