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

"""\
1;2; ; ; 
 ;3;4;5;6
7;8;9;10;11
 ; ; ; ; ;12
"""

]

def test():
    for i in range(len(result)):
        print("Test", i)
        assert table2csv("../html/test" + str(i) + ".html") == result[i]
    print("Everything is OK!")


if __name__ == '__main__':
    test()
