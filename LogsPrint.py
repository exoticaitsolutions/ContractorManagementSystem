from PyQt5.QtGui import QTextCursor

#  logs print function
def print_the_output_statement(output, message):
    output.append(f"<b>{message}</b> \n \n")
    output.moveCursor(QTextCursor.End)
    print(message)