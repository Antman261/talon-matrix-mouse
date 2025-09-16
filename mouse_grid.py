from functools import reduce
from enum import Enum, auto
import math
from typing import List
from talon import Module, Context, ui, canvas, actions
from talon.skia import Rect


mod = Module()
mod.tag("matrix_mouse", desc="Moving mouse with matrix")
mod.tag("matrix_mouse_subgrid_active", desc="Matrix mouse subgrid active")
ctx = Context()
mcanvas = None


class Status(Enum):
    idle = auto()
    open = auto()
    zone = auto()
    cell = auto()


status: Status = Status.idle
mouse_action = None
cells = {}
subcells = {}
active_zone = "000"
active_cell = "000"
num_columns = 25
num_rows = 30
grid_key_map = {}
screenWidth = 0
screenHeight = 0
cell_width = 0
cell_height = 0
subgrid_num_columns = 7
subgrid_num_rows = 3
subgrid_width = 0
subgrid_height = 0
subgrid_cell_width = 0
subgrid_cell_height = 0


letter_matrix = [
    ["A", "B", "C", "D", "E"],
    ["F", "G", "H", "I", "J"],
    ["K", "L", "M", "N", "O"],
    ["P", "Q", "R", "S", "T"],
    ["U", "V", "W", "X", "Y"],
    ["Z", "0", "1", "2", "3"],
]
alpha = reduce(list.__add__, letter_matrix)


def redraw():
    if mcanvas == None:
        return
    mcanvas.resume()
    mcanvas.pause()


def to_grid_key(row_index, column_index):
    letter_one = letter_matrix[math.floor(row_index / 5)][math.floor(column_index / 5)]
    letter_two = letter_matrix[row_index % 5][column_index % 5]
    return f"{letter_one}{letter_two}"


for idx in range(0, num_rows * num_columns):
    column_index = idx % num_columns
    row_index = math.floor(idx / num_columns)
    grid_key = to_grid_key(row_index, column_index)
    grid_key_map[grid_key] = (row_index, column_index)


def calc_subgrid(grid_x_start, grid_x_end, grid_y_start, grid_y_end):
    global subgrid_cell_width, subgrid_cell_height, subgrid_width, subgrid_height
    subgrid_width = grid_x_end - grid_x_start
    subgrid_height = grid_y_end - grid_y_start
    subgrid_cell_width = round(subgrid_width / (subgrid_num_columns))
    subgrid_cell_height = round(subgrid_height / (subgrid_num_rows))
    idx = 0
    for row_index in range(0, subgrid_num_rows):
        for column_index in range(0, subgrid_num_columns):
            letter = alpha[idx]
            idx += 1
            cell_x_start = grid_x_start + round(column_index * subgrid_cell_width)
            cell_x_centre = cell_x_start + (subgrid_cell_width / 2)
            cell_y_start = grid_y_start + round(row_index * subgrid_cell_height)
            cell_y_centre = (
                cell_y_start + subgrid_cell_height - (subgrid_cell_height / 2)
            )
            subcells[letter] = (cell_x_centre, cell_y_centre)


def clear_active_cell():
    global active_cell, active_zone
    active_zone = "000"
    active_cell = "000"


def get_active_cell_grid_key():
    return f"{active_zone}{active_cell}"


def get_active_cell_tuple():
    return cells[get_active_cell_grid_key()]


def calc_grid():
    global mcanvas, screenWidth, screenHeight, cell_width, cell_height
    if mcanvas != None:
        print("Canvas already exists ")
        return
    screens = ui.screens()
    screen = screens[0]
    mcanvas = canvas.Canvas.from_screen(screen)
    screenWidth = screen.width
    screenHeight = screen.height
    cell_width = round(screenWidth / (num_columns))
    cell_height = round(screenHeight / (num_rows))
    for row_index in range(0, num_rows):
        for column_index in range(0, num_columns):
            x_start = round(column_index * cell_width)
            x_end = x_start + cell_width
            x_centre = x_end - (cell_width / 2)
            y_start = round(row_index * cell_height)
            y_end = y_start + cell_height
            y_centre = y_end - (cell_height / 2)
            cells[to_grid_key(row_index, column_index)] = (
                x_start,
                x_end,
                x_centre,
                y_start,
                y_end,
                y_centre,
            )


theme = {
    "zone_bg": "30214499",
    "cell_text": "ccccccdf",
    "grid_line": "7945ab60",
    "grid_bg": "00002244",
}


def draw_subgrid(c):
    (grid_x_start, grid_x_end, _, grid_y_start, __, ___) = get_active_cell_tuple()
    c.paint.textsize = round(min(subgrid_cell_height * 0.7, subgrid_cell_width * 0.7))
    c.paint.color = theme["grid_line"]
    for idx in range(1, subgrid_num_columns):
        x_offset = grid_x_start + round(idx * subgrid_cell_width)
        c.draw_line(x_offset, grid_y_start, x_offset, grid_y_start + subgrid_height)
    for idx in range(1, subgrid_num_rows):
        y_offset = grid_y_start + round(idx * subgrid_cell_height)
        c.draw_line(grid_x_start, y_offset, grid_x_end, y_offset)
    for idx in range(0, subgrid_num_rows * subgrid_num_columns):
        letter = alpha[idx]
        textrect = c.paint.measure_text(letter)[1]
        (x_centre, y_centre) = subcells[letter]
        x_offset = x_centre - (textrect.width / 2)
        y_offset = y_centre + (textrect.height / 2)
        c.paint.color = theme["cell_text"]
        c.draw_text(letter, x_offset, y_offset)


def get_zone_tuple():
    return (
        cells[f"{active_zone}A"],
        cells[f"{active_zone}Y"],
        cells[f"{active_zone}M"],
    )


def draw_zone(c):
    (start, end) = get_zone_tuple()[:2]
    x_start = start[0]
    y_start = start[3]
    x_end = end[1]
    y_end = end[4]
    zone_box = Rect(x_start, y_start, x_end - x_start, y_end - y_start)
    c.paint.color = theme["zone_bg"]
    c.draw_rect(zone_box)


def draw_grid():
    def on_draw(c):
        c.paint.stroke_width = 1
        c.paint.color = theme["grid_bg"]
        c.draw_rect(Rect(0, 0, screenWidth, screenHeight))
        c.paint.typeface = "arial"
        c.paint.textsize = round(min(cell_height * 0.5, cell_width * 0.5))
        if active_zone != "000":
            draw_zone(c)
        c.paint.color = theme["grid_line"]
        for idx in range(1, num_columns):
            x_offset = round(idx * cell_width)
            if x_offset == screenWidth:
                continue
            c.draw_line(x_offset, 0, x_offset, screenHeight)
        for idx in range(1, num_rows):
            y_offset = round(idx * cell_height)
            if y_offset == screenHeight:
                continue
            c.draw_line(0, y_offset, screenWidth, y_offset)
        for row_index in range(0, num_rows):
            for column_index in range(0, num_columns):
                grid_key = to_grid_key(row_index, column_index)
                if grid_key == get_active_cell_grid_key():
                    continue
                (_, __, x_centre, ___, ____, y_centre) = cells[grid_key]
                textrect = c.paint.measure_text(grid_key)[1]
                x_offset = x_centre - (textrect.width / 2)
                y_offset = y_centre + (textrect.height / 2)
                c.paint.color = theme["cell_text"]
                c.draw_text(grid_key, x_offset, y_offset)
        if active_cell != "000":
            draw_subgrid(c)

    mcanvas.register("draw", on_draw)
    mcanvas.pause()


def perform_mouse_action(x, y, mouse_action: str | None = None):
    control_enabled = actions.tracking.control_enabled()
    control1_enabled = actions.tracking.control1_enabled()
    if control_enabled:
        actions.tracking.control_toggle()
    if control1_enabled:
        actions.tracking.control1_toggle()
    actions.mouse_move(x, y)
    if mouse_action != None:
        match mouse_action:
            case "left":
                actions.mouse_click(0)
            case "right":
                actions.mouse_click(1)
    if control_enabled:
        actions.tracking.control_toggle()
    if control1_enabled:
        actions.tracking.control1_toggle()


def open_grid(input_length: int = 0):
    global status
    status = Status.open
    clear_active_cell()
    calc_grid()
    if input_length < 3:
        draw_grid()
    ctx.tags = ["user.matrix_mouse"]


def activate_zone(zone):
    global status, active_zone
    status = Status.zone
    active_zone = zone
    centre = get_zone_tuple()[2]
    perform_mouse_action(centre[2], centre[5])


def activate_cell(cell):
    global status, active_cell
    active_cell = cell
    status = Status.cell
    (x_start, x_end, x_centre, y_start, y_end, y_centre) = get_active_cell_tuple()
    calc_subgrid(x_start, x_end, y_start, y_end)
    perform_mouse_action(x_centre, y_centre)


def close_grid():
    global status, mcanvas, mouse_action
    status = Status.idle
    if mcanvas != None:
        mcanvas = mcanvas.close()
    clear_active_cell()
    mouse_action = None
    ctx.tags = []


def process_input(text, action="left"):
    global mouse_action
    input_length = len(text)
    letters: List[str] = list(text.upper())
    for letter in letters:
        match status:
            case Status.idle:
                open_grid(input_length)
                activate_zone(letter)
            case Status.open:
                activate_zone(letter)
            case Status.zone:
                activate_cell(letter)
            case Status.cell:
                if mouse_action is None:
                    mouse_action = action if action is not None else "left"
                else:
                    mouse_action = action if action is not None else mouse_action
                perform_mouse_action(*subcells[letter], mouse_action)
                close_grid()
    redraw()


@mod.action_class
class GridActions:
    def matrix_mouse_grid_start():
        """Display the full mouse grid"""
        open_grid()

    def matrix_mouse_grid_stop():
        """Clear the mouse grid and cancel any in-progress action"""
        close_grid()

    def matrix_mouse(letters: str, action: str | None = None):
        """Move the mouse to the grid position specified by letters and perform the action, if provided"""
        global mouse_action
        mouse_action = action if mouse_action is None else mouse_action
        process_input(letters, mouse_action)
