"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count=0
    o_count=0
    for row in board:
        for symbol in row:
            x_count = x_count+1 if symbol=="X" else x_count
            o_count = o_count+1 if symbol=="O" else o_count
    if x_count-o_count == 0: return "X"
    else: return "O"
    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    set_of_actions=set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                set_of_actions.add((i,j))
    return set_of_actions
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board=copy.deepcopy(board)
    whose_turn=player(board)
    i=action[0]
    j=action[1]
    if i<0 or i>2 or j<0 or j>2:
        raise Exception
    if new_board[i][j] == EMPTY:
        new_board[i][j]=whose_turn
    else:
        raise Exception
    return new_board
    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #checking rows
    for row in board:
        if row[0] == row[1] == row[2]:
            if row[0] == "X": return "X"
            if row[0] == "O": return "O"
    #checking columns
    for column_index in range(3):
        if board[0][column_index] == board[1][column_index] == board[2][column_index]:
            if board[0][column_index] == "X": return "X"
            if board[0][column_index] == "O": return "O"
    #cheking diagonals manually
    if board[0][0] == board[1][1] == board[2][2]:
        if board[0][0] == "X": return "X"
        if board[0][0] == "O": return "O"
    if board[0][2] == board[1][1] == board[2][0]:
        if board[0][2] == "X": return "X"
        if board[0][2] == "O": return "O"
    return None
    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    all_filled = True
    for row in board:
        if EMPTY in row: all_filled = False
    if all_filled:
        return True
    return False
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
    if winner(board) == "O":
        return -1
    return 0
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board) == True:
        return None
    turn = player(board)
    if turn == "X":
        return max_value(board)[1]
    else:
        return min_value(board)[1]
    raise NotImplementedError

def max_value(board):
    result_boards_values={}
    for action in actions(board):
        current_result_board=result(board,action)
        if str(current_result_board) not in result_boards_values.keys():
            if terminal(current_result_board):
                result_boards_values[str(current_result_board)]=[utility(current_result_board),action]
            else:
                result_boards_values[str(current_result_board)]=[min_value(current_result_board)[0],action]
    desired_value=max(p[0] for p in result_boards_values.values())
    for key in result_boards_values.keys():
        if result_boards_values[key][0] == desired_value:
            taken_action = result_boards_values[key][1]
    return [desired_value, taken_action]

def min_value(board):
    result_boards_values={}
    for action in actions(board):
        current_result_board=result(board,action)
        if str(current_result_board) not in result_boards_values.keys():
            if terminal(current_result_board):
                result_boards_values[str(current_result_board)]=[utility(current_result_board),action]
            else:
                result_boards_values[str(current_result_board)]=[max_value(current_result_board)[0],action]
    desired_value=min(p[0] for p in result_boards_values.values())
    for key in result_boards_values.keys():
        if result_boards_values[key][0] == desired_value:
            taken_action = result_boards_values[key][1]
    return [desired_value, taken_action]

