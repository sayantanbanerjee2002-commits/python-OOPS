
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import uuid
import threading

# --- Domain Models ---

@dataclass
class Instructor:
    instructor_id: str
    name: str
    subjects: List[str] = field(default_factory=list)
    courses_teaching: List[str] = field(default_factory=list)  # course_ids
    rating: Optional[float] = None
    experience_years: int = 0

    def assign_course(self, course_id: str) -> None:
        if course_id not in self.courses_teaching:
            self.courses_teaching.append(course_id)


@dataclass
class Student:
    student_id: str
    name: str
    enrolled_courses: List[str] = field(default_factory=list)  # course_ids
    attendance_record: Dict[str, List[datetime]] = field(default_factory=dict)  # course_id -> timestamps present
    grades: Dict[str, float] = field(default_factory=dict)  # course_id -> current grade
    learning_progress: Dict[str, float] = field(default_factory=dict)  # course_id -> percent

    def enroll(self, course_id: str) -> None:
        if course_id not in self.enrolled_courses:
            self.enrolled_courses.append(course_id)


@dataclass
class ThreadReply:
    reply_id: str
    author_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiscussionThread:
    thread_id: str
    title: str
    author_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    replies: List[ThreadReply] = field(default_factory=list)

    def add_reply(self, author_id: str, message: str) -> ThreadReply:
        r = ThreadReply(reply_id=str(uuid.uuid4()), author_id=author_id, message=message)
        self.replies.append(r)
        return r


@dataclass
class LiveSession:
    session_id: str
    course_id: str
    date_time: datetime
    duration_minutes: int
    recording_url: Optional[str] = None
    attendees: List[str] = field(default_factory=list)  # student_ids present
    chat_log: List[Dict[str, Any]] = field(default_factory=list)  # simple chat records

    def mark_attendance(self, student_id: str) -> None:
        if student_id not in self.attendees:
            self.attendees.append(student_id)

    def post_chat(self, student_id: str, message: str) -> None:
        self.chat_log.append({'student_id': student_id, 'message': message, 'time': datetime.utcnow()})


# -------------------- Assessments (Abstract) --------------------

class Assessment(ABC):
    @abstractmethod
    def is_submittable(self) -> bool:
        pass

    @abstractmethod
    def grade_submission(self, submission: 'Submission') -> float:
        pass


@dataclass
class Assignment(Assessment):
    assignment_id: str
    course_id: str
    title: str
    description: str
    deadline: datetime
    max_marks: float
    weight: float  # relative weight in final grade (e.g., 0.3)

    def is_submittable(self) -> bool:
        return True

    def grade_submission(self, submission: 'Submission') -> float:
        # For demo: if marks_obtained provided, use it; otherwise 0
        return submission.marks_obtained if submission.marks_obtained is not None else 0.0


@dataclass
class Submission:
    submission_id: str
    student_id: str
    assignment_id: str
    submitted_date: datetime
    file_url: Optional[str] = None
    marks_obtained: Optional[float] = None
    feedback: Optional[str] = None

# -------------------- Course --------------------

@dataclass
class Course:
    course_id: str
    title: str
    instructor_id: str
    enrolled_students: List[str] = field(default_factory=list)  # student_ids
    schedule: List[LiveSession] = field(default_factory=list)
    syllabus: List[str] = field(default_factory=list)  # topics/lessons
    assignments: List[Assignment] = field(default_factory=list)
    discussions: List[DiscussionThread] = field(default_factory=list)

    # weighted components: dict like {'assignments': 0.4, 'quizzes': 0.2, 'exam': 0.4}
    grade_weights: Dict[str, float] = field(default_factory=lambda: {'assignments': 0.6, 'exam': 0.4})

    def enroll_student(self, student_id: str) -> None:
        if student_id not in self.enrolled_students:
            self.enrolled_students.append(student_id)

    def add_session(self, session: LiveSession) -> None:
        self.schedule.append(session)

    def add_assignment(self, assignment: Assignment) -> None:
        self.assignments.append(assignment)

    def add_discussion(self, thread: DiscussionThread) -> None:
        self.discussions.append(thread)

    def total_lessons(self) -> int:
        return len(self.syllabus)

# -------------------- Manager / Services --------------------

class EducationPlatform:
    LATE_PENALTY_PER_DAY = 0.10  # 10% per day late
    PASS_PERCENTAGE = 50.0

    def __init__(self):
        self.instructors: Dict[str, Instructor] = {}
        self.students: Dict[str, Student] = {}
        self.courses: Dict[str, Course] = {}
        self.submissions: Dict[str, Submission] = {}  # submission_id -> Submission
        # simple notification registry: mapping timer id to threading.Timer
        self.notifications: Dict[str, threading.Timer] = {}

    # ----- CRUD helpers -----

    def add_instructor(self, name: str, subjects: Optional[List[str]] = None, experience: int = 0) -> Instructor:
        iid = str(uuid.uuid4())
        inst = Instructor(instructor_id=iid, name=name, subjects=subjects or [], experience_years=experience)
        self.instructors[iid] = inst
        return inst

    def add_student(self, name: str) -> Student:
        sid = str(uuid.uuid4())
        student = Student(student_id=sid, name=name)
        self.students[sid] = student
        return student

    def create_course(self, title: str, instructor_id: str, syllabus: Optional[List[str]] = None) -> Course:
        cid = str(uuid.uuid4())
        course = Course(course_id=cid, title=title, instructor_id=instructor_id, syllabus=syllabus or [])
        self.courses[cid] = course
        # register course with instructor
        inst = self.instructors.get(instructor_id)
        if inst:
            inst.assign_course(cid)
        return course

    # ----- Enrollment & attendance -----

    def enroll_student(self, student_id: str, course_id: str) -> None:
        student = self.students[student_id]
        course = self.courses[course_id]
        student.enroll(course_id)
        course.enroll_student(student_id)

    def auto_mark_attendance(self, course_id: str, session_id: str) -> None:
        # When session ends or recording processed, mark attendance for present attendees in session
        course = self.courses[course_id]
        session = next((s for s in course.schedule if s.session_id == session_id), None)
        if not session:
            return
        for sid in session.attendees:
            student = self.students.get(sid)
            if student:
                student.attendance_record.setdefault(course_id, []).append(datetime.utcnow())

    def calculate_student_progress(self, student_id: str, course_id: str) -> float:
        student = self.students[student_id]
        course = self.courses[course_id]
        total = course.total_lessons()
        if total == 0:
            return 0.0
        # For demo: progress = lessons 'attended' / total
        # Use attendance count for course as proxy for lessons completed
        completed = len(student.attendance_record.get(course_id, []))
        pct = round((completed / total) * 100, 2)
        student.learning_progress[course_id] = pct
        return pct

    # ----- Submissions & grading -----

    def submit_assignment(self, student_id: str, assignment_id: str, file_url: Optional[str] = None, marks_obtained: Optional[float] = None, submitted_date: Optional[datetime] = None) -> Submission:
        submitted_date = submitted_date or datetime.utcnow()
        sub_id = str(uuid.uuid4())
        # find assignment and course
        assignment = None
        course = None
        for c in self.courses.values():
            for a in c.assignments:
                if a.assignment_id == assignment_id:
                    assignment = a
                    course = c
                    break
            if assignment:
                break
        if not assignment:
            raise ValueError('Assignment not found')

        # compute late penalty
        days_late = max(0, (submitted_date.date() - assignment.deadline.date()).days)
        penalty_pct = min(1.0, days_late * EducationPlatform.LATE_PENALTY_PER_DAY)
        effective_marks = marks_obtained if marks_obtained is not None else None
        if effective_marks is not None:
            effective_marks = max(0.0, effective_marks * (1.0 - penalty_pct))

        submission = Submission(submission_id=sub_id, student_id=student_id, assignment_id=assignment_id, submitted_date=submitted_date, file_url=file_url, marks_obtained=effective_marks)
        self.submissions[sub_id] = submission
        return submission

    def calculate_course_grade_for_student(self, student_id: str, course_id: str) -> float:
        course = self.courses[course_id]
        student = self.students[student_id]
        # For demo: only assignments and 'exam' (not implemented) - use assignments average
        assignment_weight = course.grade_weights.get('assignments', 0.6)
        exam_weight = course.grade_weights.get('exam', 0.4)

        # average percent across assignments for this student
        assignment_scores = []
        for a in course.assignments:
            # find latest submission by this student for this assignment
            subs = [s for s in self.submissions.values() if s.assignment_id == a.assignment_id and s.student_id == student_id]
            if not subs:
                continue
            latest = max(subs, key=lambda x: x.submitted_date)
            if latest.marks_obtained is not None and a.max_marks > 0:
                pct = (latest.marks_obtained / a.max_marks) * 100
                assignment_scores.append(pct)
        assignment_avg_pct = (sum(assignment_scores) / len(assignment_scores)) if assignment_scores else 0.0

        # exam component: assume 0 for demo
        exam_pct = 0.0

        final_pct = assignment_avg_pct * assignment_weight + exam_pct * exam_weight
        # store grade
        student.grades[course_id] = round(final_pct, 2)
        return round(final_pct, 2)

    # ----- Analytics -----

    def average_attendance(self, course_id: str) -> float:
        course = self.courses[course_id]
        if not course.schedule or not course.enrolled_students:
            return 0.0
        totals = []
        for s in course.schedule:
            totals.append(len(s.attendees))
        avg = sum(totals) / len(course.schedule) if course.schedule else 0.0
        # return as percent of enrolled students
        pct = (avg / len(course.enrolled_students) * 100) if course.enrolled_students else 0.0
        return round(pct, 2)

    def pass_rate(self, course_id: str) -> float:
        course = self.courses[course_id]
        passed = 0
        for sid in course.enrolled_students:
            grade = self.students[sid].grades.get(course_id, 0.0)
            if grade >= EducationPlatform.PASS_PERCENTAGE:
                passed += 1
        total = len(course.enrolled_students)
        return round((passed / total * 100), 2) if total else 0.0

    def topic_performance(self, course_id: str) -> Dict[str, float]:
        # For demo: map topic -> average attendance as proxy for performance
        course = self.courses[course_id]
        result = {}
        total_lessons = course.total_lessons()
        if total_lessons == 0:
            return {t: 0.0 for t in course.syllabus}
        # naive: performance per topic = (#students who attended sessions)/enrolled
        for i, topic in enumerate(course.syllabus):
            # assume session index maps to topic index if schedule length matches
            if i < len(course.schedule):
                sess = course.schedule[i]
                pct = (len(sess.attendees) / len(course.enrolled_students) * 100) if course.enrolled_students else 0.0
                result[topic] = round(pct, 2)
            else:
                result[topic] = 0.0
        return result

    # ----- Discussion forum -----

    def create_thread(self, course_id: str, author_id: str, title: str, message: str) -> DiscussionThread:
        course = self.courses[course_id]
        t = DiscussionThread(thread_id=str(uuid.uuid4()), title=title, author_id=author_id, message=message)
        course.add_discussion(t)
        return t

    def reply_thread(self, course_id: str, thread_id: str, author_id: str, message: str) -> ThreadReply:
        course = self.courses[course_id]
        thread = next((th for th in course.discussions if th.thread_id == thread_id), None)
        if not thread:
            raise ValueError('Thread not found')
        return thread.add_reply(author_id, message)

    # ----- Certificates -----

    def generate_certificate(self, student_id: str, course_id: str) -> Optional[Dict[str, Any]]:
        student = self.students[student_id]
        grade = student.grades.get(course_id, 0.0)
        if grade >= EducationPlatform.PASS_PERCENTAGE:
            cert = {
                'certificate_id': str(uuid.uuid4()),
                'student_id': student_id,
                'course_id': course_id,
                'date_issued': datetime.utcnow().isoformat(),
                'grade': grade,
                'message': f'Certificate of completion for {self.courses[course_id].title}'
            }
            return cert
        return None

    # ----- Notifications -----

    def schedule_notification(self, when: datetime, payload: Dict[str, Any]) -> str:
        delay = max(0, (when - datetime.utcnow()).total_seconds())
        nid = str(uuid.uuid4())
        timer = threading.Timer(delay, self._send_notification, args=(nid, payload))
        timer.start()
        self.notifications[nid] = timer
        return nid

    def _send_notification(self, nid: str, payload: Dict[str, Any]) -> None:
        # In real system: push to queue / send email / websocket. Here we print.
        print(f"[NOTIFICATION] {datetime.utcnow().isoformat()} -> {payload}")
        # remove timer reference
        self.notifications.pop(nid, None)

    def cancel_notification(self, nid: str) -> None:
        timer = self.notifications.pop(nid, None)
        if timer:
            timer.cancel()

# -------------------- Demo / Example usage --------------------

if __name__ == "__main__":
    platform = EducationPlatform()

    # Create instructor and course
    inst = platform.add_instructor('Dr. Meera', subjects=['Math', 'CS'], experience=8)
    course = platform.create_course('Intro to Algorithms', inst.instructor_id, syllabus=['Sorting', 'Searching', 'Graphs'])

    # Create students
    s1 = platform.add_student('Arjun')
    s2 = platform.add_student('Priya')

    # Enroll students
    platform.enroll_student(s1.student_id, course.course_id)
    platform.enroll_student(s2.student_id, course.course_id)

    # Add live sessions (one per topic) and auto-mark attendance for s1
    now = datetime.utcnow()
    sess1 = LiveSession(session_id=str(uuid.uuid4()), course_id=course.course_id, date_time=now, duration_minutes=60)
    sess2 = LiveSession(session_id=str(uuid.uuid4()), course_id=course.course_id, date_time=now + timedelta(days=7), duration_minutes=60)
    course.add_session(sess1)
    course.add_session(sess2)

    # s1 attends session 1
    sess1.mark_attendance(s1.student_id)
    sess1.post_chat(s1.student_id, "Hello, excited to learn sorting!")

    # Auto-mark attendance into student record (simulate end of session)
    platform.auto_mark_attendance(course.course_id, sess1.session_id)

    # Add an assignment
    assign = Assignment(assignment_id=str(uuid.uuid4()), course_id=course.course_id, title='Sorting Assignment', description='Implement quicksort', deadline=now + timedelta(days=3), max_marks=100.0, weight=0.6)
    course.add_assignment(assign)

    # s1 submits on time, s2 submits late
    sub1 = platform.submit_assignment(s1.student_id, assign.assignment_id, file_url='http://files/sub1.zip', marks_obtained=90.0, submitted_date=now + timedelta(days=1))
    sub2 = platform.submit_assignment(s2.student_id, assign.assignment_id, file_url='http://files/sub2.zip', marks_obtained=95.0, submitted_date=now + timedelta(days=5))  # late 2 days -> 20% penalty

    print(f"S1 effective marks: {sub1.marks_obtained}, S2 effective marks (penalized): {sub2.marks_obtained}")

    # Calculate grades
    g1 = platform.calculate_course_grade_for_student(s1.student_id, course.course_id)
    g2 = platform.calculate_course_grade_for_student(s2.student_id, course.course_id)
    print(f"Grades -> {s1.name}: {g1}%, {s2.name}: {g2}%")

    # Generate certificate if passed
    cert1 = platform.generate_certificate(s1.student_id, course.course_id)
    cert2 = platform.generate_certificate(s2.student_id, course.course_id)
    print('Certificate S1:', cert1)
    print('Certificate S2:', cert2)

    # Discussion forum
    thread = platform.create_thread(course.course_id, s1.student_id, 'Question about quicksort', 'Can someone explain partition step?')
    r = platform.reply_thread(course.course_id, thread.thread_id, s2.student_id, 'Sure — I can explain with an example.')
    print('Discussion thread replies:', len(thread.replies))

    # Analytics
    print('Average attendance (%):', platform.average_attendance(course.course_id))
    print('Pass rate (%):', platform.pass_rate(course.course_id))
    print('Topic performance:', platform.topic_performance(course.course_id))

    # Schedule notification for upcoming session (5 seconds from now for demo)
    when = datetime.utcnow() + timedelta(seconds=5)
    nid = platform.schedule_notification(when, {'type': 'session_reminder', 'course_id': course.course_id, 'session_id': sess2.session_id, 'message': 'Live session starting soon'})

    print('Demo running — waiting for notification (5s)...')
    # keep main thread alive briefly to let timer fire
    threading.Event().wait(6)
    print('Demo complete.')
