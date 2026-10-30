#=====================================================================
#  MINI PROJECT : STUDENT DATABASE MANAGEMENT SYSTEM USING HASHING
#  ---------------------------------------------------------------
#  University : Savitribai Phule Pune University (SPPU)
#  College    : KJ College of Engineering, Pune
#  Department : Computer Engineering
#  Class      : SE Computer (Data Structures Laboratory)
#
#  Student    : Shravani Pardeshi
#  Roll No    : SECCOMP06        Batch : S7
#  Guided by  : Prof. Omkar Bhalker
#
#  PROBLEM STATEMENT (as per SPPU syllabus) :
#      Consider a student database of the SE class (at least 15
#      records). The database contains fields of every student like
#      Roll No, Name and Marks (array of structures). Implement the
#      student database using hashing with linear probing as the
#      collision resolution technique :
#          (a) Linear probing WITHOUT replacement
#          (b) Linear probing WITH replacement
#
#  DESCRIPTION :
#      The program maintains TWO hash tables in parallel, one for
#      each collision handling technique. Every record inserted is
#      stored in both tables so that the number of collisions during
#      insertion and the number of comparisons required during
#      searching can be compared side by side.
#
#      Hash function used :  h(key) = key % TABLE_SIZE  (division method)
#      Table size         :  15  (as required - at least 15 records)
#      Deletion           :  tombstone (DELETED marker) so that the
#                            probe chains of other records are preserved.
#
#  HOW TO RUN :
#      python3 student_database.py        (Python 3.8 or above)
#=====================================================================

from dataclasses import dataclass

#----------------------- Global constants ---------------------------#
TABLE_SIZE = 15                        # at least 15 records (syllabus)

# Status of every slot of the hash table
EMPTY, OCCUPIED, DELETED = 0, 1, 2

#----------------------- Student record -----------------------------#
@dataclass
class Student:
    """One student record (the 'structure' of the syllabus)."""
    roll_no: int                       # key used for hashing
    name: str                          # student name
    marks: float                       # DSA marks (out of 100)
    division: str                      # class / division (e.g. A, B)


#========================== HashTable ================================
#  One object of this class is one hash table. The class works for
#  both techniques; the behaviour (with / without replacement) is
#  selected by the bool passed to the constructor.
#=====================================================================
class HashTable:

    #--------------------------- constructor -------------------------#
    def __init__(self, with_replacement, technique_name):
        self.with_replacement = with_replacement    # technique selector
        self.technique_name = technique_name        # for display
        self.table = [None] * TABLE_SIZE            # array of records
        self.status = [EMPTY] * TABLE_SIZE          # EMPTY/OCCUPIED/DELETED

        # Counters used for the comparison of the two techniques
        self.records_stored = 0                     # OCCUPIED slots
        self.total_insert_collisions = 0            # probes hitting occupied
        self.search_count = 0                       # successful searches
        self.total_search_comparisons = 0           # comparisons of those
        self.last_search_comparisons = 0            # most recent search

    #------------------------ hash function --------------------------#
    # Division method : h(k) = k mod TABLE_SIZE
    def hash_function(self, key):
        return key % TABLE_SIZE

    #------------------------ utility query --------------------------#
    def is_full(self):
        return self.records_stored == TABLE_SIZE

    def get_last_search_comparisons(self):
        return self.last_search_comparisons

    #=====================================================================
    #  SEARCH
    #  Returns the index of the record if found, otherwise -1.
    #  Probing stops on : empty slot, full cycle, or key found.
    #  DELETED (tombstone) slots are SKIPPED - otherwise the probe
    #  chains of the records placed behind them would be cut off.
    #  Every occupied slot examined is counted as one comparison.
    #=====================================================================
    def search(self, key):
        home = self.hash_function(key)
        i = home
        comparisons = 0

        while self.status[i] != EMPTY:
            if self.status[i] == OCCUPIED:
                comparisons += 1
                if self.table[i].roll_no == key:
                    # statistics are maintained only for successful searches
                    self.search_count += 1
                    self.total_search_comparisons += comparisons
                    self.last_search_comparisons = comparisons
                    return i
            i = (i + 1) % TABLE_SIZE
            if i == home:                   # full cycle - table is full
                break

        self.last_search_comparisons = comparisons
        return -1                           # not present in the table

    #=====================================================================
    #  PLACE AT NEXT FREE SLOT (linear probing)
    #  Starting from 'start', find the first EMPTY / DELETED slot.
    #  Every probe that hits an OCCUPIED slot is a collision.
    #  Returns (index, collisions), or (-1, collisions) if table full.
    #=====================================================================
    def _next_free_slot(self, start):
        i = start
        collisions = 0
        while self.status[i] == OCCUPIED:
            collisions += 1
            i = (i + 1) % TABLE_SIZE
            if i == start:                  # came back - table full
                return -1, collisions
        return i, collisions

    #=====================================================================
    #  INSERT  (a) WITHOUT replacement :
    #              simply place the record at the first free slot.
    #          (b) WITH replacement :
    #              if the home slot is occupied by a record that does
    #              NOT belong there (its home position is different),
    #              the new record (which IS at its home position)
    #              replaces it, and the displaced record is re-inserted
    #              using linear probing starting from its own home.
    #  Returns True on success, False if duplicate / table full.
    #=====================================================================
    def insert(self, s):
        if self.is_full():
            print(f"  [{self.technique_name}] Table is FULL - cannot insert "
                  f"{s.roll_no}.")
            return False
        if self.find_record_index(s.roll_no) != -1:
            print(f"  [{self.technique_name}] Roll No {s.roll_no} already "
                  f"exists - duplicate rejected.")
            return False

        collisions = 0
        home = self.hash_function(s.roll_no)

        if self.status[home] != OCCUPIED:   # home slot is free
            self.table[home] = s
            self.status[home] = OCCUPIED
        elif (self.with_replacement and
              self.hash_function(self.table[home].roll_no) != home):
            # occupant does not belong to this slot -> replace it
            displaced = self.table[home]
            self.table[home] = s            # new record takes its home slot
            collisions += 1                 # probe hit an occupied slot

            # re-insert the displaced record from ITS home position
            displaced_home = self.hash_function(displaced.roll_no)
            free_idx, probed = self._next_free_slot(displaced_home)
            collisions += probed
            if free_idx == -1:
                # should not happen (full check done earlier)
                self.table[home] = displaced
                print(f"  [{self.technique_name}] Insert failed - table full.")
                return False
            self.table[free_idx] = displaced
            self.status[free_idx] = OCCUPIED
        else:                               # occupant belongs here OR
            free_idx, probed = self._next_free_slot(home)  # without-repl.
            collisions += probed
            if free_idx == -1:
                print(f"  [{self.technique_name}] Insert failed - table full.")
                return False
            self.table[free_idx] = s
            self.status[free_idx] = OCCUPIED

        self.records_stored += 1
        self.total_insert_collisions += collisions

        print(f"  [{self.technique_name}] Roll No {s.roll_no} : home index = "
              f"{home}, final position = {self.find_record_index(s.roll_no)}, "
              f"collisions = {collisions}")
        return True

    #---------------------------------------------------------------------
    # Small helper : current index of a key that is already inserted.
    # Does not modify the statistics. Tombstones are skipped.
    #---------------------------------------------------------------------
    def find_record_index(self, key):
        home = self.hash_function(key)
        i = home
        while self.status[i] != EMPTY:
            if self.status[i] == OCCUPIED and self.table[i].roll_no == key:
                return i
            i = (i + 1) % TABLE_SIZE
            if i == home:
                break
        return -1

    #=====================================================================
    #  DELETE - tombstone technique.
    #  The slot is marked DELETED instead of EMPTY, because simply
    #  emptying it would break the probe chains of records that were
    #  placed later during collision resolution. A DELETED slot is
    #  skipped while searching and can be reused while inserting.
    #=====================================================================
    def remove(self, key):
        idx = self.find_record_index(key)
        if idx == -1:
            print(f"  [{self.technique_name}] Roll No {key} not found - "
                  f"cannot delete.")
            return False
        self.status[idx] = DELETED
        self.records_stored -= 1
        print(f"  [{self.technique_name}] Roll No {key} deleted from index "
              f"{idx} (slot marked DELETED).")
        return True

    #=====================================================================
    #  MODIFY - update name / marks / division of an existing record
    #=====================================================================
    def modify(self, key, new_name, new_marks, new_division):
        idx = self.find_record_index(key)
        if idx == -1:
            print(f"  [{self.technique_name}] Roll No {key} not found - "
                  f"cannot modify.")
            return False
        self.table[idx].name = new_name
        self.table[idx].marks = new_marks
        self.table[idx].division = new_division
        print(f"  [{self.technique_name}] Record at index {idx} updated "
              f"successfully.")
        return True

    #=====================================================================
    #  DISPLAY - shows every slot of the hash table
    #=====================================================================
    def display(self):
        print(f"\n  HASH TABLE : {self.technique_name}")
        print("  " + "-" * 79)
        print(f"  | {'Idx':>4} | {'Home':>4} | {'Roll No':>7} | "
              f"{'Name':<14} | {'Marks':>6} | {'Div':>4} | {'Status':>9} |")
        print("  " + "-" * 79)

        for i in range(TABLE_SIZE):
            if self.status[i] == OCCUPIED:
                rec = self.table[i]
                st = "OCCUPIED"
                roll_cell = f"{rec.roll_no:>7}"
                name_cell = f"{rec.name:<14}"
                marks_cell = f"{rec.marks:>6.1f}"
                div_cell = f"{rec.division:>4}"
            else:
                st = "DELETED" if self.status[i] == DELETED else "EMPTY"
                roll_cell = f"{'-':>7}"
                name_cell = f"{'-':<14}"
                marks_cell = f"{'-':>6}"
                div_cell = f"{'-':>4}"
            print(f"  | {i:>4} | {i:>4} | {roll_cell} | {name_cell} | "
                  f"{marks_cell} | {div_cell} | {st:>9} |")

        print("  " + "-" * 79)
        print(f"  Total records stored : {self.records_stored} / {TABLE_SIZE}")

    #=====================================================================
    #  STATISTICS of this table (used by the compare option)
    #=====================================================================
    def print_stats(self):
        if self.search_count > 0:
            avg = self.total_search_comparisons / self.search_count
            avg_cell = f"{avg:.2f}"
        else:
            avg_cell = "-"
        print(f"  | {self.technique_name:<36} | {self.records_stored:>8} | "
              f"{self.total_insert_collisions:>10} | {avg_cell:>12} |")


#====================== Global hash tables ===========================
#  Two tables are maintained in parallel so that the same set of
#  records is stored using both collision handling techniques and
#  their performance can be compared directly.
#=====================================================================
table_without = HashTable(False, "Linear Probing WITHOUT Replacement")
table_with = HashTable(True, "Linear Probing WITH Replacement")


#------------------------- input helpers -----------------------------#
def read_int(prompt):
    """Read an integer, re-prompting until the input is valid."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  Invalid input! Please enter an integer.")
        except EOFError:
            print("\nExiting... Thank you!")
            raise SystemExit(0)


def read_float(prompt):
    """Read a floating point number, re-prompting until the input is valid."""
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("  Invalid input! Please enter a number.")
        except EOFError:
            print("\nExiting... Thank you!")
            raise SystemExit(0)


def read_string(prompt):
    """Read one line of text."""
    try:
        return input(prompt).strip()
    except EOFError:
        print("\nExiting... Thank you!")
        raise SystemExit(0)


#========================= menu operations ===========================#
def insert_record():
    print("\n---------------- INSERT STUDENT RECORD ---------------")
    if table_without.is_full():
        print("Database is full (15 records) - insert not possible.")
        return
    roll_no = read_int("Enter Roll No (key)          : ")
    if table_without.find_record_index(roll_no) != -1:
        print(f"Record with Roll No {roll_no} already exists!")
        return
    name = read_string("Enter Name                   : ")
    marks = read_float("Enter DSA Marks (out of 100) : ")
    division = read_string("Enter Division (A/B/...)     : ")

    print()
    # the same record is stored in both tables
    table_without.insert(Student(roll_no, name, marks, division))
    table_with.insert(Student(roll_no, name, marks, division))


def search_record():
    print("\n---------------- SEARCH STUDENT RECORD ---------------")
    key = read_int("Enter Roll No to search      : ")
    print()
    i1 = table_without.search(key)
    i2 = table_with.search(key)
    result1 = (f"FOUND at index {i1} (comparisons : "
               f"{table_without.get_last_search_comparisons()})"
               if i1 != -1 else
               f"NOT FOUND (comparisons : "
               f"{table_without.get_last_search_comparisons()})")
    result2 = (f"FOUND at index {i2} (comparisons : "
               f"{table_with.get_last_search_comparisons()})"
               if i2 != -1 else
               f"NOT FOUND (comparisons : "
               f"{table_with.get_last_search_comparisons()})")
    print(f"  WITHOUT replacement : {result1}")
    print(f"  WITH replacement    : {result2}")


def modify_record():
    print("\n---------------- MODIFY STUDENT RECORD ---------------")
    key = read_int("Enter Roll No to modify      : ")
    if table_without.find_record_index(key) == -1:
        print(f"Record with Roll No {key} does not exist!")
        return
    new_name = read_string("Enter New Name               : ")
    new_marks = read_float("Enter New DSA Marks          : ")
    new_div = read_string("Enter New Division           : ")
    print()
    table_without.modify(key, new_name, new_marks, new_div)
    table_with.modify(key, new_name, new_marks, new_div)


def delete_record():
    print("\n---------------- DELETE STUDENT RECORD ---------------")
    key = read_int("Enter Roll No to delete      : ")
    print()
    table_without.remove(key)
    table_with.remove(key)


def compare_techniques():
    print("\n------------- COMPARISON OF TECHNIQUES ---------------")
    print("  (Same records stored using both collision handling methods)\n")
    print("  " + "-" * 74)
    print(f"  | {'Technique':<36} | {'Records':>8} | "
          f"{'Collisions':>10} | {'Avg Cmp/Srch':>12} |")
    print("  " + "-" * 74)
    table_without.print_stats()
    table_with.print_stats()
    print("  " + "-" * 74)
    print("  Collisions = probes that hit an occupied slot during insertion")
    print("  Avg Cmp/Srch = average comparisons per successful search")
    print("  With replacement keeps more records near their home slot, so")
    print("  successful searches usually need fewer comparisons.")


#============================= main ==================================#
def main():
    print("=" * 57)
    print("    STUDENT DATABASE MANAGEMENT SYSTEM USING HASHING")
    print("        (Linear Probing - with & without replacement)")
    print("=" * 57)
    print(f" Hash function : h(rollNo) = rollNo mod {TABLE_SIZE}")
    print(" Fields        : Roll No (key), Name, DSA Marks, Division")
    print("=" * 57)

    while True:
        print("\n=================== MAIN MENU ======================")
        print("  1. Insert a new student record")
        print("  2. Search a student (by Roll No)")
        print("  3. Modify a student record")
        print("  4. Delete a student record")
        print("  5. Display hash table(s)")
        print("  6. Compare collision handling techniques")
        print("  0. Exit")
        print("=" * 52)
        choice = read_int("Enter your choice : ")

        if choice == 1:
            insert_record()
        elif choice == 2:
            search_record()
        elif choice == 3:
            modify_record()
        elif choice == 4:
            delete_record()
        elif choice == 5:
            print("\nShow (1) Without replacement only, "
                  "(2) With replacement only, (3) Both : ", end="")
            opt = read_int("")
            print()
            if opt == 1:
                table_without.display()
            elif opt == 2:
                table_with.display()
            else:
                table_without.display()
                table_with.display()
        elif choice == 6:
            compare_techniques()
        elif choice == 0:
            print("\nExiting... Thank you!")
            break
        else:
            print("Invalid choice! Please try again.")


if __name__ == "__main__":
    main()
#=====================================================================
