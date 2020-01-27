import json
import PySimpleGUI as sg
import random
import string
import copy

BOX_SIZE = 140
PLAYER1 = "PLAYER1"
PLAYER2 = "PLAYER2"

# Keys
CURR_PLAYER_KEY = "-CURR-PLAYER-KEY-"
TIC_TOC_GRAPH_KEY = "-TIC-TOC-GRAPH-KEY-"
TIC_TOC_RECT_KEY = "-TIC-TOC-RECT-KEY-"

# One can take that info from conf json
NUM_OF_ROWS = 3
NUM_OF_COLS = 3


# IO Read, unpredictable function
def read_conf_file(path="game_conf.json"):
    with open(path) as json_file:
        return json.load(json_file)


# Window/GUI functions
def initial_layout():
    layout = [
        [sg.Text("Tic-Toc-Toe using Func Python")],
        [
            sg.Text(
                "                                                            ",
                key=CURR_PLAYER_KEY,
            )
        ],
        [
            sg.Graph(
                (750, 750),
                (0, 425),
                (425, 0),
                key=TIC_TOC_GRAPH_KEY,
                change_submits=True,
                drag_submits=False,
            )
        ],
        [sg.Button("Restart"), sg.Button("Exit")],
    ]
    return layout


def main_window(layout):
    return sg.Window("Tic Toc Toe", layout, finalize=True)


def graph_in_window(main_window, graph_key=TIC_TOC_GRAPH_KEY):
    return main_window[graph_key]


def draw_tic_toc_toe_table(graph_window, rows=NUM_OF_ROWS, cols=NUM_OF_COLS):
    for row in range(rows):
        for col in range(cols):
            graph_window.draw_rectangle(
                (col * BOX_SIZE + 5, row * BOX_SIZE + 3),
                (col * BOX_SIZE + BOX_SIZE + 5, row * BOX_SIZE + BOX_SIZE + 3),
                line_color="black",
            )


def draw_symbols(
    graph_window, letter_location, symbol=random.choice(string.ascii_uppercase)
):
    graph_window.draw_text("{}".format(symbol), letter_location, font="Courier 25")


def clear_graph_data(graph_window):
    graph_window.Erase()


# End Window/GUI functions

# Event related functions


def current_status(player):
    return "                                  {} Turn".format(player)


def update_current_player_window_status(main_window, status, curr_key=CURR_PLAYER_KEY):
    main_window[curr_key].update(status)


def restart_game(graph_window):
    clear_graph_data(graph_window)
    draw_tic_toc_toe_table(graph_window)


def letter_location(box_x, box_y, bx_size=BOX_SIZE):
    return (box_x * bx_size + 70, box_y * bx_size + 70)


def box_x_y_co_ordinates(mouse, bx_size=BOX_SIZE):
    box_x = mouse[0] // bx_size
    box_y = mouse[1] // bx_size
    return box_x, box_y


def process_player_keys(values, graph_window, state, game_conf):
    mouse = values[TIC_TOC_GRAPH_KEY]
    if mouse == (None, None):
        return state

    box_x_cord, box_y_cord = box_x_y_co_ordinates(mouse)
    curr_player, curr_symbol = player_symbol_from_state(state, game_conf)
    if can_player_play(curr_player, curr_symbol, state, box_x_cord, box_y_cord):
        draw_symbols(graph_window, letter_location(box_x_cord, box_y_cord), curr_symbol)
        new_board = update_board(
            state["board_state"], box_x_cord, box_y_cord, curr_symbol
        )
        if winning_cond(new_board, curr_symbol):
            sg.Popup("Player wins game, restarting ")
            restart_game(graph_window)
            update_current_player_window_status(main_window, "")
            return initial_game_state(game_conf)
        elif game_over_cond(new_board):
            sg.Popup("Game Over ")
            restart_game(graph_window)
            update_current_player_window_status(main_window, "")
            return initial_game_state(game_conf)
        else:
            new_player = change_player(curr_player)
            new_state = update_state(state, new_board, new_player)
            return new_state
    return state


def event_loop(main_window, graph_window, state, game_conf):
    event, values = main_window.read()

    if event in (None, "Exit"):
        return
    elif event in (None, "Restart"):
        restart_game(graph_window)
        new_state = initial_game_state(game_conf)
        update_current_player_window_status(
            main_window, current_status(new_state["curr_player"])
        )
        event_loop(main_window, graph_window, new_state, game_conf)
    elif event == TIC_TOC_GRAPH_KEY:
        new_state = process_player_keys(values, graph_window, state, game_conf)
        update_current_player_window_status(
            main_window, current_status(new_state["curr_player"])
        )
        event_loop(main_window, graph_window, new_state, game_conf)


# End Event related functions

# Business rules


def can_player_play(curr_player, curr_symbol, state, x_cord, y_cord):
    board_state = state["board_state"]
    curr_symbol = board_state[x_cord][y_cord]
    # Corrsponding symbol is empty means player can play
    # one can define complex rules such if one player tried to modify
    # opponents symbol
    if curr_symbol == "":
        return True
    return False


def horizontal_cond(board, curr_symbol):
    for row in board:
        row_len = len(row)
        curr_symbol_count = row.count(curr_symbol)
        if curr_symbol_count == row_len:
            return True
    return False


def vertical_cond(board, curr_symbol):
    for vertical_row in zip(*board):
        vertical_row_count = vertical_row.count(curr_symbol)
        row_len = len(vertical_row)
        if vertical_row_count == row_len:
            return True
    return False


def _left_diagonal_rows(board):
    num_of_rows = len(board)
    left_diagonal_rows = []

    for horizontal_row_num in range(0, num_of_rows):
        left_diagonal_rows.append(board[horizontal_row_num][horizontal_row_num])

    return left_diagonal_rows


def left_diagonale_cond(board, curr_symbol):
    left_diagonal_rows = _left_diagonal_rows(board)
    left_diagonal_rows_count = left_diagonal_rows.count(curr_symbol)
    if left_diagonal_rows_count == len(left_diagonal_rows):
        return True
    return False


def _right_diagonal_rows(board):
    num_of_rows = len(board)
    right_diagonal_rows = []

    for x, y in zip(range(0, num_of_rows), range(num_of_rows - 1, -1, -1)):
        right_diagonal_rows.append(board[x][y])

    return right_diagonal_rows


# Right and Left cond are similar, only diff is how to travese
# One can write abstraction for it
def right_diagonale_cond(board, curr_symbol):
    right_diagonal_rows = _right_diagonal_rows(board)
    right_diagonal_rows_count = right_diagonal_rows.count(curr_symbol)
    if right_diagonal_rows_count == len(right_diagonal_rows):
        return True
    return False


def winning_cond(board, curr_symbol):
    # traverse array horizontaly and see each row has consecative symbol
    if horizontal_cond(board, curr_symbol):
        return True
    elif vertical_cond(board, curr_symbol):
        return True
    elif left_diagonale_cond(board, curr_symbol):
        return True
    elif right_diagonale_cond(board, curr_symbol):
        return True
    return False


def game_over_cond(board):
    # this can be writen using list comprehension but I prefer readabilty
    for row in board:
        for item in row:
            if item == "":
                return False
    return True


def change_player(curr_player):
    return PLAYER1 if curr_player == PLAYER2 else PLAYER2


# End Business rules

# State functions
def player_symbol_from_curr_player(curr_player, game_conf):
    if curr_player == PLAYER1:
        return game_conf["player_one_symbol"]
    return game_conf["player_two_symbol"]


def player_symbol_from_state(state, game_conf):
    curr_player = state["curr_player"]
    symbol = player_symbol_from_curr_player(curr_player, game_conf)
    return curr_player, symbol


def initial_game_state(game_conf, current_player=PLAYER1):
    return {
        "board_state": copy.deepcopy(game_conf["initial_board_state"]),
        "curr_player": current_player,
    }


def update_board(board, x, y, symbol):
    # Make copy, in Python list can be modified
    new_board = copy.deepcopy(board)
    new_board[x][y] = symbol
    return new_board


def update_state(state, new_board, new_player):
    new_state = copy.deepcopy(state)
    new_state["board_state"] = new_board
    new_state["curr_player"] = new_player
    return new_state


if __name__ == "__main__":
    game_conf_options = read_conf_file()

    main_window = main_window(initial_layout())
    graph_window = graph_in_window(main_window)

    draw_tic_toc_toe_table(graph_window)

    event_loop(
        main_window,
        graph_window,
        initial_game_state(game_conf_options),
        game_conf_options,
    )


# This can be done with infinite loop
# However passing state is difficult, one can keep state global and mutate that state
# def event_loop(main_window, graph_window):
#     while True:
#         event, values = main_window.read()

#         if event in (None, 'Exit'):
#             break

#         if event in (None, 'Restart'):
#             clear_graph_data(graph_window)
#             draw_tic_toc_toe_table(graph_window)

#         mouse = values[TIC_TOC_GRAPH_KEY]

#         if event == TIC_TOC_GRAPH_KEY:
#             if mouse == (None, None):
#                 continue
#             box_x = mouse[0]//BOX_SIZE
#             box_y = mouse[1]//BOX_SIZE
#             letter_location = (box_x * BOX_SIZE + 70, box_y * BOX_SIZE + 70)

#             draw_symbols(graph_window, letter_location)
