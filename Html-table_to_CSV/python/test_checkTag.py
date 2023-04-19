from HtmlTable2Csv import *

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
    print("CheckTag() is OK!")


if __name__ == '__main__':
    test_checkTag()