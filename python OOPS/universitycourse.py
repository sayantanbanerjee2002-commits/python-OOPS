from datetime import datetime
from typing import List, Dict, Optional


class Course:
    """Represents a university course with enrollment management"""
    
    def __init__(self, course_code: str, name: str, credits: int, 
                 instructor: 'Instructor', max_students: int, 
                 prerequisites: List[str] = None):
        self.course_code = course_code
        self.name = name
        self.credits = credits
        self.instructor = instructor
        self.max_students = max_students
        self.prerequisites = prerequisites or []
        self.enrolled_students = []
        self.waiting_list = []
    
    def is_full(self) -> bool:# return boolean variable
        """Check if course has reached maximum capacity"""
        return len(self.enrolled_students) >= self.max_students
    
    def add_to_waiting_list(self, student: 'Student') -> bool: # return boolean value
        """Add student to waiting list when course is full"""
        if student not in self.waiting_list:
            self.waiting_list.append(student)
            return True
        return False
    
    def enroll_student(self, student: 'Student') -> bool:
        """Enroll a student if space available"""
        if not self.is_full() and student not in self.enrolled_students:
            self.enrolled_students.append(student)
            return True
        return False
    
    def remove_student(self, student: 'Student'):
        """Remove student and promote from waiting list if available"""
        if student in self.enrolled_students:
            self.enrolled_students.remove(student)
            # Promote first student from waiting list
            if self.waiting_list:
                next_student = self.waiting_list.pop(0)
                self.enroll_student(next_student)
    
    def __str__(self):
        return f"{self.course_code}: {self.name} ({self.credits} credits)"


class Student:
    """Represents a student with enrollment and academic records  tracking"""
    
    def __init__(self, student_id: str, name: str, major: str):
        self.student_id = student_id
        self.name = name
        self.major = major
        self.enrolled_courses = []  # Current enrollments
        self.completed_courses = {}  # course_code: grade mapping
        self.gpa = 0.0
    
    def has_prerequisite(self, course: Course) -> bool:
        """Check if student has completed all prerequisites"""
        for prereq in course.prerequisites:
            if prereq not in self.completed_courses:
                return False
        return True
    
    def calculate_gpa(self):
        """Automatically calculate GPA based on completed courses with grades"""
        grade_points = {'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 
                       'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7,
                       'D': 1.0, 'F': 0.0}
        
        total_points = 0
        total_credits = 0
        
        for course_code, grade in self.completed_courses.items():
            if grade in grade_points:
                # Find the course to get credits
                for enrollment in self.enrolled_courses:
                    if enrollment.course.course_code == course_code:
                        credits = enrollment.course.credits
                        total_points += grade_points[grade] * credits
                        total_credits += credits
                        break
        
        self.gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
        return self.gpa
    
    def get_transcript(self) -> str:
        """Generate formatted transcript for the student"""
        transcript = f"\n{'='*60}\n"
        transcript += f"OFFICIAL TRANSCRIPT\n"
        transcript += f"{'='*60}\n\n"
        transcript += f"Student ID: {self.student_id}\n"
        transcript += f"Name: {self.name}\n"
        transcript += f"Major: {self.major}\n"
        transcript += f"Cumulative GPA: {self.gpa}\n\n"
        transcript += f"{'='*60}\n"
        transcript += f"COMPLETED COURSES\n"
        transcript += f"{'='*60}\n"
        
        for course_code, grade in self.completed_courses.items():
            transcript += f"{course_code}: Grade {grade}\n"
        
        transcript += f"\n{'='*60}\n"
        return transcript
    
    def __eq__(self, other: 'Student') -> bool:
        """Compare students by GPA for equality"""
        if not isinstance(other, Student):
            return False
        return self.gpa == other.gpa
    
    def __lt__(self, other: 'Student') -> bool:
        """Compare students by GPA for sorting (less than)"""
        return self.gpa < other.gpa
    
    def __str__(self):
        return f"{self.name} ({self.student_id}) - GPA: {self.gpa}"


class Instructor:
    """Represents a course instructor"""
    
    def __init__(self, employee_id: str, name: str, department: str):
        self.employee_id = employee_id
        self.name = name
        self.department = department
        self.courses_teaching = []
        self.ratings = []
    
    def assign_course(self, course: Course):
        """Assign a course to this instructor"""
        if course not in self.courses_teaching:
            self.courses_teaching.append(course)
    
    def add_rating(self, rating: float):
        """Add a student rating (scale 1-5)"""
        if 1 <= rating <= 5:
            self.ratings.append(rating)
    
    def average_rating(self) -> float:
        """Calculate average rating"""
        return round(sum(self.ratings) / len(self.ratings), 2) if self.ratings else 0.0
    
    def __str__(self):
        return f"Prof. {self.name} ({self.department})"


class Enrollment:
    """Represents a student's enrollment in a specific course"""
    
    def __init__(self, student: Student, course: Course, semester: str):
        self.student = student
        self.course = course
        self.semester = semester
        self.grade = None
        self.attendance_percentage = 0.0
    
    def assign_grade(self, grade: str):
        """Assign grade and update student's records"""
        self.grade = grade
        # Add to completed courses
        self.student.completed_courses[self.course.course_code] = grade
        # Recalculate GPA
        self.student.calculate_gpa()
    
    def update_attendance(self, percentage: float):
        """Update attendance percentage"""
        if 0 <= percentage <= 100:
            self.attendance_percentage = percentage
    
    def __str__(self):
        return f"{self.student.name} enrolled in {self.course.name} ({self.semester})"


class Semester:
    """Manages enrollments for a specific semester"""
    
    MAX_CREDITS = 20  # Maximum credits allowed per semester
    
    def __init__(self, name: str, year: int):
        self.name = name  # e.g., "Fall", "Spring"
        self.year = year
        self.enrollments = []
    
    def enroll_student(self, student: Student, course: Course) -> tuple[bool, str]:
        """
        Enroll a student in a course with validation
               """
        # Check if already enrolled
        for enrollment in self.enrollments:
            if enrollment.student == student and enrollment.course == course:
                return False, "Already enrolled in this course"
        
        # Check prerequisites
        if not student.has_prerequisite(course):
            missing = [p for p in course.prerequisites if p not in student.completed_courses]
            return False, f"Missing prerequisites: {', '.join(missing)}"
        
        # Check credit limit
        current_credits = self.get_student_credits(student)
        if current_credits + course.credits > self.MAX_CREDITS:
            return False, f"Credit limit exceeded (current: {current_credits}, adding: {course.credits}, max: {self.MAX_CREDITS})"
        
        # Check if course is full
        if course.is_full():
            course.add_to_waiting_list(student)
            return False, f"Course is full. Added to waiting list (position: {len(course.waiting_list)})"
        
        # Enroll the student
        enrollment = Enrollment(student, course, f"{self.name} {self.year}")
        self.enrollments.append(enrollment)
        student.enrolled_courses.append(enrollment)
        course.enroll_student(student)
        
        return True, "Enrollment successful"
    
    def get_student_credits(self, student: Student) -> int:
        """Calculate total credits for a student in this semester"""
        total = 0
        for enrollment in self.enrollments:
            if enrollment.student == student:
                total += enrollment.course.credits
        return total
    
    def get_student_enrollments(self, student: Student) -> List[Enrollment]:
        """Get all enrollments for a specific student"""
        return [e for e in self.enrollments if e.student == student]
    
    def generate_semester_report(self) -> str:
        """Generate report for the semester"""
        report = f"\n{'='*70}\n"
        report += f"SEMESTER REPORT: {self.name} {self.year}\n"
        report += f"{'='*70}\n\n"
        report += f"Total Enrollments: {len(self.enrollments)}\n\n"
        
        # Group by student
        student_dict = {}
        for enrollment in self.enrollments:
            if enrollment.student not in student_dict:
                student_dict[enrollment.student] = []
            student_dict[enrollment.student].append(enrollment)
        
        for student, enrollments in student_dict.items():
            report += f"\n{student.name} ({student.student_id})\n"
            report += f"{'-'*50}\n"
            total_credits = 0
            for enr in enrollments:
                report += f"  • {enr.course.course_code}: {enr.course.name} ({enr.course.credits} credits)\n"
                total_credits += enr.course.credits
            report += f"  Total Credits: {total_credits}\n"
        
        report += f"\n{'='*70}\n"
        return report
    
    def __str__(self):
        return f"{self.name} {self.year} Semester"


# ============================================================================
# DEMONSTRATION PROGRAM
# ============================================================================

def main():
    print(" UNIVERSITY PORTAL SYSTEM DEMO\n")
    
    # Create instructors
    prof_ghosh = Instructor("EMP001", "Dr. Partha Ghosh", "Computer Science")
    prof_chowdhury = Instructor("EMP002", "Dr.Bikash Kumar Chowdhury", "Computer Science")
    prof_mahapatra = Instructor("EMP003", "Dr.Tanmoy Mahapatra", "Mathematics")
    
    # Create courses
    cs101 = Course("CS101", "Introduction to Programming", 3, prof_ghosh, 2, [])
    cs102 = Course("CS102", "Data Structures", 4, prof_chowdhury, 2, ["CS101"])
    cs201 = Course("CS201", "Algorithms", 4, prof_ghosh, 2, ["CS102"])
    math101 = Course("MATH101", "Calculus I", 4, prof_mahapatra, 3, [])
    
    # Assign courses to instructors
    prof_ghosh.assign_course(cs101)
    prof_chowdhury.assign_course(cs102)
    prof_ghosh.assign_course(cs201)
    prof_mahapatra.assign_course(math101)
    
    # Create students
    sayantan = Student("S001", "Sayantan Banerjee", "Computer Science")
    sourish = Student("S002", "Sourish Pati", "Computer Science")
    debasish = Student("S003", "Debasish Ghosh", "Computer Science")
    
    # Create semester
    fall_2025 = Semester("Fall", 2025)
    
    print("=" * 70)
    print("SCENARIO 1: Successful Enrollment")
    print("=" * 70)
    
    # Sayqantan enrolls in CS101
    success, message = fall_2025.enroll_student(sayantan, cs101)
    print(f" Sayantan enrolling in CS101: {message}\n")
    
    print("=" * 70)
    print("SCENARIO 2: Prerequisite Check")
    print("=" * 70)
    
    # Sourish tries to enroll in CS102 without completing CS101
    success, message = fall_2025.enroll_student(sourish, cs102)
    print(f" Sourish enrolling in CS102: {message}\n")
    
    print("=" * 70)
    print("SCENARIO 3: Course Full - Waiting List")
    print("=" * 70)
    
    # Fill up CS101 (max 2 students)
    fall_2025.enroll_student(sourish, cs101)
    print(" Sourish enrolled in CS101")
    
    # Debasish tries to enroll (course full)
    success, message = fall_2025.enroll_student(debasish, cs101)
    print(f" Debasish enrolling in CS101: {message}\n")
    
    print("=" * 70)
    print("SCENARIO 4: Credit Limit Validation")
    print("=" * 70)
    
    # Simulate Sayantan trying to overload credits
    sayantan.enrolled_courses[0].course.credits = 18  # Temporarily modify for demo
    success, message = fall_2025.enroll_student(sayantan, math101)
    print(f"Sayantan trying to add MATH101 (4 credits) when already at 18:")
    print(f" {message}\n")
    sayantan.enrolled_courses[0].course.credits = 3  # Reset
    
    # Now enroll properly
    fall_2025.enroll_student(sayantan, math101)
    print(" Sayantan successfully enrolled in MATH101\n")
    
    print("=" * 70)
    print("SCENARIO 5: Grading and GPA Calculation")
    print("=" * 70)
    
    # Complete CS101 for Sayantan and Sourish
    sayantan.enrolled_courses[0].assign_grade("A")
    print(f"Sayantan received 'A' in CS101")
    print(f"  Sayantan's GPA: {sayantan.gpa}\n")
    
    sourish.enrolled_courses[0].assign_grade("B+")
    print(f" Sourish received 'B+' in CS101")
    print(f"  Sourish's GPA: {sourish.gpa}\n")
    
    print("=" * 70)
    print("SCENARIO 6: Student Comparison by GPA")
    print("=" * 70)
    
    students = [sayantan, sourish, debasish]
    students.sort(reverse=True)  # Sort by GPA (highest first)
    print("Students ranked by GPA:")
    for i, student in enumerate(students, 1):
        print(f"{i}. {student}")
    print()
    
    print("=" * 70)
    print("SCENARIO 7: Transcript Generation")
    print("=" * 70)
    
    print(sayantan.get_transcript())
    
    print("=" * 70)
    print("SCENARIO 8: Semester Report")
    print("=" * 70)
    
    print(fall_2025.generate_semester_report())
    
    print("=" * 70)
    print("SCENARIO 9: Instructor Ratings")
    print("=" * 70)
    
    prof_ghosh.add_rating(4.5)
    prof_ghosh.add_rating(4.8)
    prof_ghosh.add_rating(4.6)
    print(f"Prof. ghosh's average rating: {prof_ghosh.average_rating()}/5.0\n")


if __name__ == "__main__":
    main()