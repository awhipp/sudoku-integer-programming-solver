# -*- coding: utf-8 -*-
"""
@author: Julie Carey and Alexander Whipp
"""

"""# Import and Global Variables"""

import pandas as pd
from pulp import *
import math

"""# Helper Functions to convert records to Soduku 2D-Arrays"""

# Grabs individual row and splits into quiz and solution
def get_quiz_set(row):
  return row.quizzes, row.solutions

# Convert sudoku string into 2D-Array
def convert_to_soduku(line, n):
  sudoku = []

  split = [
           line[i:i+n] for i in range(0, len(line), n)
  ]
  
  for r in split:
    sudoku.append(
        [
         int(r[i:i+1]) for i in range(0, len(r), 1)
        ]
    )
  return sudoku

# Compares 2D-Arrays for our solution and expected solution
def compare_solutions(input, expected):
  return input == expected

# Must be perfect square (ie: 4x4, 9x9, 16x16, 25x25, 100x100, etc.)
def subn_convert(n):
  root = math.sqrt(n)
  if int(root + 0.5) ** 2 == n:
    return int(root)
  else:
    raise Exception('[%s x %s] is not an allowable dimension. Must be a perfect square (ie: 9x9 or 25x25)' % (n, n))

"""
# Setup Constants Function"""

def define_constants(n):
  Vals = range(1, n+1)  # Sequence of 1 to n
  Rows = range(0, n)    # Sequence of 0 to n-1 (Since Python is 0-based)
  Cols = range(0, n)    # Sequence of 0 to n-1 (Since Python is 0-based)

  SubN = subn_convert(n)       
  Sectors = []

  for i in range(SubN):
      for j in range(SubN):
          Sectors += [
              [
                (
                    Rows[SubN*i+k],Cols[SubN*j+l]
                ) for k in range(SubN) for l in range(SubN)
              ]
            ]

  return Vals, Rows, Cols, Sectors

"""# Define Standard Constraints
* 1 Value per Option
* Single Value per Row, Column, and Sector
"""

def define_problem_and_constraints(Vals, Rows, Cols):
  problem = LpProblem("Sudoku", LpMinimize)
  # Objective Function is irrelevant as we are just looking for an optimal soln
  problem += 0

  options = LpVariable.dicts("Options", (Vals,Rows,Cols), 0, 1, LpInteger)
  
  # Constraint: Single Value per Option
  for r in Rows:
    for c in Cols:
        problem += lpSum(
            [options[v][r][c] for v in Vals]
        ) == 1

  # Constraint: Single Value per Row, Column, and Sector
  for v in Vals:
    for r in Rows:
        problem += lpSum(
            [options[v][r][c] for c in Cols]
        ) == 1
        
    for c in Cols:
        problem += lpSum(
            [options[v][r][c] for r in Rows]
        ) == 1

    for b in Sectors:
        problem += lpSum(
            [options[v][r][c] for (r,c) in b]
        ) == 1

  return problem, options

"""# Define Sudoku Problem and Solve
Also defines the individual value constraints by looping through the 2D-Array
"""

def define_values_and_solve(problem, options, values):
  for r_idx, row in enumerate(values):
    for c_idx, value in enumerate(row):
      if value > 0:
        problem += options[value][r_idx][c_idx] == 1
  
  problem.solve()

  if LpStatus[problem.status] != 'Optimal':
    raise Exception('Infeasible Problem.')

  return problem

"""# Grab Optimal Values and Conduct Python Array
Generates a 2D-Array from the LP Solution
"""

def construct_solution_matrix(Rows, Cols, Vals, options):
  soln = []
  n = len(Rows)

  for r in Rows:
      row = []

      for c in Cols:
          for v in Vals:
            if value(options[v][r][c]):
              row.append(v)
              
              if c == n-1:
                soln.append(row)
                row = []
  return soln

"""# Construct User-Readable Print-out
Makes it easier to read and print to console
"""

def pretty_print_solution(soln):
  n = len(soln)
  sub_n = subn_convert(n)

  line = 3*n*'-' + '\n'
  prnt = ''

  for r_idx, row in enumerate(soln):
    if r_idx % sub_n == 0:
      prnt += line

    for c_idx, value in enumerate(row):
      if c_idx % sub_n == 0:
        prnt += ' |'

      prnt += ' ' + str(value)
    prnt += ' |'


    prnt += '\n'
  prnt += line
  print(prnt)

"""# Iterate through 4x4 sudoku puzzles and compare output"""

print('Testing Quizes 4x4')

n = 4
sudoku_problems = [
  '1000000400200300',
  '0014000000010300',
  '0000013000240000'
]
expected_solutions = [
  '1432321441232341',
  '3214412324311342',
  '3241413213242413'
]

for idx, p in enumerate(sudoku_problems):
  print('Testing Quiz #%s' % (idx+1))
  sudoku_problem = p
  expected_solution = expected_solutions[idx] 
  sudoku_problem = convert_to_soduku(sudoku_problem, n)
  expected_solution = convert_to_soduku(expected_solution, n)

  Vals, Rows, Cols, Sectors = define_constants(n)
  problem, options = define_problem_and_constraints(Vals, Rows, Cols)
  problem = define_values_and_solve(problem, options, sudoku_problem)
  solution = construct_solution_matrix(Rows, Cols, Vals, options)
  success = compare_solutions(solution, expected_solution)

  if not success:
    print('[Input]')
    pretty_print_solution(solution)
    print('[Output]')
    pretty_print_solution(expected_solution)    
    raise Exception('Failed to find correct solution')

"""# Iterate through 9x9 sudoku puzzles and compare output"""

# Ingests the sudoku.csv from https://www.kaggle.com/bryanpark/sudoku
# Be sure to have it uploaded into Colab or next to wherever this script is
sudoku_puzzles = pd.read_csv(r'sudoku.csv')
number_to_test = 10
n = 9

for i, row in sudoku_puzzles.iterrows():
  print('Testing Quiz #%s' % str(i+1))
  sudoku_problem, expected_solution = get_quiz_set(row)
  sudoku_problem = convert_to_soduku(sudoku_problem, n)
  expected_solution = convert_to_soduku(expected_solution, n)
 
  Vals, Rows, Cols, Sectors = define_constants(n)
  problem, options = define_problem_and_constraints(Vals, Rows, Cols)
  problem = define_values_and_solve(problem, options, sudoku_problem)
  solution = construct_solution_matrix(Rows, Cols, Vals, options)
  success = compare_solutions(solution, expected_solution)
 
  if not success:
    print('[Input]')
    pretty_print_solution(solution)
    print('[Output]')
    pretty_print_solution(expected_solution)    
    raise Exception('Failed to find correct solution')
  
  if i+1 == number_to_test:
    break

"""# Iterate through 16x16 sudoku puzzles and compare output"""

print('Testing Quizes 16x16')

n = 16
sudoku_problem = [
  [0,0,0,10,0,4,0,14,0,0,5,0,0,16,0,13],
  [13,0,0,0,11,0,0,0,6,0,0,1,0,0,12,0],
  [0,2,0,12,0,0,0,9,0,15,0,0,0,11,0,0],
  [4,0,3,0,0,6,0,15,0,0,0,13,0,0,0,1],
  [0,16,0,9,0,0,0,0,11,0,2,0,0,0,0,0],
  [12,0,5,0,13,0,1,0,0,8,0,0,0,7,0,10],
  [0,3,0,13,0,12,0,0,0,0,14,0,4,0,0,0],
  [1,0,8,0,0,0,0,6,0,12,0,0,0,0,15,0],
  [0,0,0,16,3,0,11,0,8,0,9,0,1,0,0,4],
  [0,0,0,0,1,9,0,5,0,0,3,2,0,0,10,0],
  [7,0,4,0,2,0,16,0,0,1,0,0,6,0,0,12],
  [0,9,0,5,0,0,0,13,0,0,12,0,0,0,14,0],
  [6,0,0,0,0,0,8,0,0,14,0,10,0,0,0,2],
  [0,5,0,0,15,0,0,10,0,0,11,0,0,9,0,0],
  [0,0,0,14,0,0,0,0,0,3,0,5,0,0,0,16],
  [2,0,15,0,0,11,0,0,12,0,16,0,14,0,6,0]
]
expected_solution = [
  [9,1,6,10,7,4,2,14,3,11,5,12,15,16,8,13],
  [13,15,16,7,11,5,10,3,6,2,8,1,9,4,12,14],
  [5,2,14,12,8,1,13,9,16,15,4,7,10,11,3,6],
  [4,11,3,8,16,6,12,15,14,9,10,13,7,2,5,1],
  [15,16,7,9,14,8,3,4,11,10,2,6,13,12,1,5],
  [12,14,5,6,13,2,1,11,4,8,15,9,3,7,16,10],
  [11,3,10,13,9,12,15,7,1,5,14,16,4,6,2,8],
  [1,4,8,2,10,16,5,6,13,12,7,3,11,14,15,9],
  [14,13,2,16,3,10,11,12,8,6,9,15,1,5,7,4],
  [8,6,12,15,1,9,14,5,7,4,3,2,16,13,10,11],
  [7,10,4,11,2,15,16,8,5,1,13,14,6,3,9,12],
  [3,9,1,5,6,7,4,13,10,16,12,11,2,8,14,15],
  [6,7,11,4,12,3,8,16,9,14,1,10,5,15,13,2],
  [16,5,13,1,15,14,6,10,2,7,11,8,12,9,4,3],
  [10,12,9,14,4,13,7,2,15,3,6,5,8,1,11,16],
  [2,8,15,3,5,11,9,1,12,13,16,4,14,10,6,7]
]

Vals, Rows, Cols, Sectors = define_constants(n)
problem, options = define_problem_and_constraints(Vals, Rows, Cols)
problem = define_values_and_solve(problem, options, sudoku_problem)
solution = construct_solution_matrix(Rows, Cols, Vals, options)
success = compare_solutions(solution, expected_solution)

if not success:
  print('[Input]')
  pretty_print_solution(solution)
  print('[Output]')
  pretty_print_solution(expected_solution)    
  raise Exception('Failed to find correct solution')
