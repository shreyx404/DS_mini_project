# Student Database Management System Using Hashing

**Mini Project - Data Structures Laboratory**
Savitribai Phule Pune University (SPPU) - SE Computer Engineering

| | |
|---|---|
| **Student** | Shravani Pardeshi |
| **Roll No** | SECCOMP06 |
| **Batch** | S7 |
| **Guided by** | Prof. Omkar Bhalker |
| **College** | KJ College of Engineering, Pune |

## Description

A menu-driven student database implemented in **Python** using **hashing
with linear probing** as the collision resolution technique, exactly as
prescribed in the SPPU Data Structures syllabus.

The program maintains **two hash tables in parallel** - one using
**linear probing WITHOUT replacement** and one using **linear probing
WITH replacement** - so that the collision counts and search comparison
counts of both techniques can be compared directly at runtime.

- **Hash function** : division method, `h(rollNo) = rollNo mod 15`
- **Table size** : 15 slots (syllabus requires at least 15 records)
- **Record fields** : Roll No (key), Name, DSA Marks, Division
- **Record storage** : list of `Student` dataclass objects (the
  "array of structures" of the syllabus, in Python form)
- **Deletion** : tombstone technique (DELETED marker) so probe chains
  of other records are never broken; deleted slots are reused on insert

## Features

1. Insert a new student record
2. Search a student by Roll No (reports comparisons used in both tables)
3. Modify a student record
4. Delete a student record
5. Display the hash table(s) - index, home position, record, status
6. Compare the two collision handling techniques (collisions during
   insertion + average comparisons per successful search)
7. Input validation for every field (re-prompts after bad input),
   duplicate-key rejection, full-table guard

## How to Run

Python 3.8 or above is required - no third-party packages are needed.

```bash
python3 student_database.py
```

On Windows: `python student_database.py`. Using an IDE (VS Code /
PyCharm / IDLE): open `student_database.py` and run the single source
file.

## Sample Session

See `sample_output.txt` for a captured session in which 8 students are
inserted (several colliding at home index 10), one record is modified
and one deleted, and the two techniques are compared (captured with
`python3 student_database.py < demo_input.txt`):

| Technique | Collisions | Avg comparisons per successful search |
|---|---|---|
| Linear probing WITHOUT replacement | 13 | 2.67 |
| Linear probing WITH replacement | 15 | 1.67 |

With replacement, a record that is displaced from its home slot is
swapped back when the rightful owner arrives, so more records stay near
their home position and successful searches need fewer comparisons -
the small extra insertion cost is paid back by faster searches.

## Syllabus Alignment

- SPPU SE (Computer Engineering) - Data Structures & Algorithms:
  searching and hashing - hash functions, collision resolution
  strategies (linear probing with and without replacement, quadratic
  probing, chaining, double hashing)
- SPPU SE laboratory assignment statement: student database of the SE
  class with fields Roll No, Name and Marks (array of structures)
  implemented using linear probing with and without replacement
  (realised here as a Python list of `Student` objects)
