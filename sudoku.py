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

for i, row in sudoku_puzzles.iterrows():
  print('Testing Quiz #%s' % str(i+1))
  sudoku_problem, expected_solution = get_quiz_set(row)
  sudoku_problem = convert_to_soduku(sudoku_problem, 9)
  expected_solution = convert_to_soduku(expected_solution, 9)
 
  Vals, Rows, Cols, Sectors = define_constants(9)
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

