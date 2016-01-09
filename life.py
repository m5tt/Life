#!/usr/bin/python

import argparse
from tkinter import *
from random import randint

## Globals and constants

live = 1
dead = 0

colors = ["midnightblue", "deepskyblue", "green", "seagreen", "yellow", "orangered", "red", "magenta", "violet"]


arg_parser = argparse.ArgumentParser(description="Conway's Game Of Life")
arg_parser.add_argument('--patternfile', required=True, type=str)
arg_parser.add_argument('--speedstep', required=False, default=50, type=int)
arg_parser.add_argument('--scrollincr', required=False, default=15, type=int)
arg_parser.add_argument('--win_x', required=False, default=1000, type=int)
arg_parser.add_argument('--win_y', required=False, default=1000, type=int)
arg_parser.add_argument('--initspeed', required=False, default=500, type=int)
arg_parser.add_argument('--cell_dif', required=False, default=12, type=int)
arg_parser.add_argument('--cell_size', required=False, default=7, type=int)
arg_parser.add_argument('--color', required=False, default="red", type=str)
arg_parser.add_argument('--multicolor', required=False, default=False, type=bool)



args = arg_parser.parse_args()
patternfile = args.patternfile

speedstep = args.speedstep
scrollincr = args.scrollincr

win_x = args.win_x
win_y = args.win_y
speed = args.initspeed

cell_dif = args.cell_dif
point_dif = args.cell_size
color = args.color

scrollregion_x = 999999
scrollregion_y = 999999

multicolor = args.multicolor

## Midpoints for scroll region and window, used to center things - no need to add x1, y1 since there 0 
mpscroll_x, mpscroll_y = scrollregion_x / 2, scrollregion_y / 2
mpwin_x, mpwin_y = win_x / 2, win_y / 2



def get_neighbors(x, y):

    for hor in [-1, 0, 1]:

        for ver in [-1, 0, 1]:

            if not hor == ver == 0 and ((0 <= (x + hor) < scrollregion_x) and (0 <= (y + ver) < scrollregion_y)):
                yield (x + hor, y + ver)



def calc_gen(old_livecells, cand_cells):

    new_livecells = set()

    for x, y in cand_cells:
        liveneighbor_count = 0

        for neighbor_x, neighbor_y in get_neighbors(x, y):
            if (neighbor_x, neighbor_y) in old_livecells: ## If neighbor is live
                liveneighbor_count += 1


        if ((x, y) in old_livecells) and (1 < liveneighbor_count < 4):
            new_livecells.add((x, y))
        elif (not ((x, y) in old_livecells)) and (liveneighbor_count == 3):
            new_livecells.add((x, y))

    return new_livecells


def get_candcells(live_cells):

    ## Candidate cells (candidate to be live/dead) - all live cells plus there neighbors

    cand_cells = set()
    cand_cells.update(live_cells)

    for x, y in live_cells:
        for neighbor_x, neighbor_y in get_neighbors(x, y):
            cand_cells.add((neighbor_x, neighbor_y))

    return cand_cells



def draw_cells(canvas, live_cells):

    global color
    canvas.delete("all")

    for x, y in live_cells:
        x = (x * cell_dif)
        y = (y * cell_dif)

        if multicolor: 
            color = colors[randint(0, len(colors) - 1)]
        
        canvas.create_rectangle(x, y, x + point_dif, y + point_dif, fill=color)
    


def init_game():

    live_cells = set()
    
    with open(patternfile, 'r') as pattern_fh:
 
        for line_num, pattern_line in enumerate(pattern_fh):
            pattern_line = pattern_line.rstrip('\n')

            ## Comments and blank lines
            if not pattern_line or pattern_line[0] == '!':
                continue
            
            for cell_num, cell in enumerate(pattern_line):

                if cell == 'O':

                    ## Put pattern somewhere in middle of board
                    x = int(cell_num + (mpscroll_x / cell_dif) - 20)
                    y = int(line_num + (mpscroll_y / cell_dif) - 10)

                    live_cells.add((x, y))


    return live_cells






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

canvas.focus_set()
canvas.pack()



live_cells = init_game()


## Needs to go here so we can have canvas and live_cells in scope
def update():
    global live_cells

    draw_cells(canvas, live_cells)
    live_cells = calc_gen(live_cells, get_candcells(live_cells))

    master.after(speed, update)


master.after(speed, update)
master.mainloop()
