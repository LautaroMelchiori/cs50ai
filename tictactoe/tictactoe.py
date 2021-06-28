"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

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
    x_count = 0
    o_count = 0

    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                x_count += 1
            elif board[i][j] == O:
                o_count += 1

    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)

    row, col = action

    if new_board[row][col] == EMPTY:
        new_board[row][col] = player(board)
    else:
        raise Exception

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    x_win = 'XXX'
    o_win = 'OOO'

    # check for diagonal wins
    diag_1 = [board[0][0]] + [board[1][1]] + [board[2][2]]
    if None not in diag_1:
        won = ''.join(diag_1)
        if won == x_win or won == o_win:
            return diag_1[0]

    diag_2 = [board[0][2]] + [board[1][1]] + [board[2][0]]
    if None not in diag_2:
        won = ''.join(diag_2)
        if won == x_win or won == o_win:
            return diag_2[0]

    # check for horizontal wins
    hor_1 = [board[0][0]] + [board[0][1]] + [board[0][2]]
    if None not in hor_1:
        won = ''.join(hor_1)
        if won == x_win or won == o_win:
            return hor_1[0]

    hor_2 = [board[1][0]] + [board[1][1]] + [board[1][2]]
    if None not in hor_2:
        won = ''.join(hor_2)
        if won == x_win or won == o_win:
            return hor_2[0]

    hor_3 = [board[2][0]] + [board[2][1]] + [board[2][2]]
    if None not in hor_3:
        won = ''.join(hor_3)
        if won == x_win or won == o_win:
            return hor_3[0]

    # check for vertical wins
    ver_1 = [board[0][0]] + [board[1][0]] + [board[2][0]]
    if None not in ver_1:
        won = ''.join(ver_1)
        if won == x_win or won == o_win:
            return ver_1[0]

    ver_2 = [board[0][1]] + [board[1][1]] + [board[2][1]]
    if None not in ver_2:
        won = ''.join(ver_2)
        if won == x_win or won == o_win:
            return ver_2[0]

    ver_3 = [board[0][2]] + [board[1][2]] + [board[2][2]]
    if None not in ver_3:
        won = ''.join(ver_3)
        if won == x_win or won == o_win:
            return ver_3[0]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    won = winner(board)

    if won == 'X':
        return 1
    elif won == 'O':
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    def max_value(state, alpha=math.inf):
        if terminal(state):
            return utility(state)

        v = -math.inf

        for action in actions(state):
            v = max(v, min_value(result(state, action), v))
            if v >= alpha:
                return alpha

        return v

    def min_value(state, alpha=-math.inf):
        if terminal(state):
            return utility(state)

        v = math.inf

        for action in actions(state):
            v = min(v, max_value(result(state, action), v))
            if v <= alpha:
                return alpha

        return v

    current_player = player(board)

    if current_player == 'X':
        # we try to maximize
        best_score = -math.inf
        for action in actions(board):
            res = min_value(result(board, action))

            # if we find an action that wins, just return it
            if res == 1:
                return action
            # else, keep looking for the best possible one
            elif res > best_score:
                best_score = res
                best_action = action
    else:
        # we try to minimize
        best_score = math.inf
        for action in actions(board):
            res = max_value(result(board, action))

            # if we find an action that wins, just return it
            if res == -1:
                return action
            # else, keep looking for the best possible one
            elif res < best_score:
                best_score = res
                best_action = action

    return best_action
