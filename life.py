#!/usr/bin/python

import os
import argparse
from tkinter import *
from random import randint

## Globals and constants

live = 1
dead = 0

cell_dist = 10
cell_width = 10

cellwidth_min = 2
cellwidth_max = 10
scale_factor = 1

colors = ["midnightblue", "deepskyblue", "green", "seagreen", "yellow", "orangered", "red", "magenta", "violet"]


arg_parser = argparse.ArgumentParser(description="Conway's Game Of Life")
arg_parser.add_argument('--patternfile', '-p', required=True, type=str)
arg_parser.add_argument('--speedstep', required=False, default=50, type=int)
arg_parser.add_argument('--scrollincr', required=False, default=15, type=int)
arg_parser.add_argument('--win_x', '-wx', required=False, default=1000, type=int)
arg_parser.add_argument('--win_y', '-wy', required=False, default=1000, type=int)
arg_parser.add_argument('--initspeed', '-s', required=False, default=500, type=int)
arg_parser.add_argument('--color', '-c', required=False, default="red", type=str)
arg_parser.add_argument('--multicolor', required=False, default=False, type=bool)


args = arg_parser.parse_args()
patternfile = args.patternfile
speedstep = args.speedstep
scrollincr = args.scrollincr
win_x = args.win_x
win_y = args.win_y
speed = args.initspeed
color = args.color
multicolor = args.multicolor


scrollregion_x = 999999
scrollregion_y = 999999

## Midpoints for scroll region and window, used to center things - no need to add x1, y1 since there 0 
mpscroll_x, mpscroll_y = int(scrollregion_x / 2), int(scrollregion_y / 2)
mpwin_x, mpwin_y = int(win_x / 2), int(win_y / 2)

cell_offset = mpscroll_x


## Main data structure, keeps track of live cells, set() to keep things unique
live_cells = set()


def get_neighbors(x, y):
    for hor in [-1, 0, 1]:

        for ver in [-1, 0, 1]:

            if not hor == ver == 0 and ((0 <= (x + hor) < scrollregion_x) and (0 <= (y + ver) < scrollregion_y)):
                yield (x + hor, y + ver)



def calc_gen(cand_cells):
    new_livecells = set()

    for x, y in cand_cells:
        liveneighbor_count = 0

        for neighbor_x, neighbor_y in get_neighbors(x, y):
            if (neighbor_x, neighbor_y) in live_cells: ## If neighbor is live
                liveneighbor_count += 1


        if ((x, y) in live_cells) and (1 < liveneighbor_count < 4):
            new_livecells.add((x, y))
        elif (not ((x, y) in live_cells)) and (liveneighbor_count == 3):
            new_livecells.add((x, y))

    return new_livecells


def get_candcells():
    ## Candidate cells (candidate to be live/dead) - all live cells plus there neighbors

    cand_cells = set()
    cand_cells.update(live_cells)

    for x, y in live_cells:
        for neighbor_x, neighbor_y in get_neighbors(x, y):
            cand_cells.add((neighbor_x, neighbor_y))

    return cand_cells



def draw_cells(canvas):
    global color
    canvas.delete("all")

    for x, y in live_cells:
        draw_x = ((x - cell_offset) * cell_dist) + cell_offset
        draw_y = ((y - cell_offset) * cell_dist) + cell_offset
       
        if multicolor: 
            color = colors[randint(0, len(colors) - 1)]
        
        canvas.create_rectangle(draw_x, draw_y, draw_x + cell_width, draw_y + cell_width, fill=color) 


def is_int(char):

    try:
        int(char)
        return True
    except:
        return False

## Parse files in rle format
def parse_rle(pattern_fh):
    return 0;
    ## TODO
    
## Parse pattern files in .cells format
def parse_cells(pattern_fh): 
    for y, pattern_line in enumerate(pattern_fh):
        pattern_line = pattern_line.rstrip('\n')

        ## Comments and blank lines
        if not pattern_line or pattern_line[0] == '!':
            continue
        
        for x, cell in enumerate(pattern_line):
            if cell == 'O':    
                yield (x, y)


def init_game(): 
    with open(patternfile, 'r') as pattern_fh:
        
        parse_func = None
        file_extension = os.path.splitext(patternfile)[1]

        if file_extension == '.cells':
            parse_func = parse_cells
        elif file_extension == '.rle':
            parse_func = parse_rle
        else:
            print("Error invalid file format")
            exit(1)

        for x, y in parse_func(pattern_fh):
            live_cells.add((x + cell_offset, y + cell_offset)) ## Put in middle


## Callbacks

def quit_callback(event):
    exit(1)

def speedup_callback(event):
    global speed

    if (speed - speedstep) >  0:
        speed -= speedstep

def speeddown_callback(event):
    global speed
    speed += speedstep


def scrollup_callback(event):
    event.widget.yview_scroll(-1, UNITS)

def scrolldown_callback(event):
    event.widget.yview_scroll(1, UNITS)

def scrollright_callback(event):
    event.widget.xview_scroll(1, UNITS)

def scrollleft_callback(event):
    event.widget.xview_scroll(-1, UNITS)


def zoom_in(event):
    global cell_dist
    global cell_width

    if (cell_width + scale_factor) <= cellwidth_max:
        cell_width += scale_factor
        cell_dist = cell_width
        
def zoom_out(event):
    global cell_dist
    global cell_width

    if (cell_width - scale_factor) >= cellwidth_min:
        cell_width -= scale_factor 
        cell_dist = cell_width



#### GUI setup

master = Tk()
canvas = Canvas(master, width=win_x, height=win_y, scrollregion=(0, 0, scrollregion_x, scrollregion_y))

## Place window at center of scroll region
canvas.configure(xscrollincrement=(mpscroll_x - mpwin_x), yscrollincrement=(mpscroll_y - mpwin_y))
canvas.xview_scroll(1, UNITS)
canvas.yview_scroll(1, UNITS)


## Now change scroll increment to a normal number for user scrolling
canvas.configure(xscrollincrement=scrollincr, yscrollincrement=scrollincr)


canvas.bind('q', quit_callback)
canvas.bind('u', speedup_callback)
canvas.bind('d', speeddown_callback)

canvas.bind('<Up>', scrollup_callback)
canvas.bind('<Down>', scrolldown_callback)
canvas.bind('<Left>', scrollleft_callback)
canvas.bind('<Right>', scrollright_callback)

canvas.bind('i', zoom_in)
canvas.bind('o', zoom_out)

canvas.focus_set()
canvas.pack()


init_game()

def update():
    global live_cells

    draw_cells(canvas)
    live_cells = calc_gen(get_candcells())

    master.after(speed, update)


master.after(speed, update)
master.mainloop()
