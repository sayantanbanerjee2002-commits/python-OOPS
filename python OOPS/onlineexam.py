
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import uuid
import threading

# -- Domain classes --

@dataclass
class Question:
    question_id: str
    question_text: str
    options: List[str] = field(default_factory=list)  # for MCQ
    correct_answer: Any = None  # could be index for MCQ/TF or text for descriptive
    marks: float = 1.0
    question_type: str = "MCQ"  # 'MCQ', 'True-False', 'Descriptive'
    difficulty: str = "Medium"  # 'Easy', 'Medium', 'Hard'


@dataclass
class Exam:
    exam_id: str
    subject: str
    duration_minutes: int
    total_marks: float
    difficulty: str
    questions: List[Question] = field(default_factory=list)
    max_attempts: int = 2
    cooling_period_days: int = 1  # days between retries

    def add_question(self, q: Question) -> None:
        self.questions.append(q)

    def question_by_id(self, qid: str) -> Optional[Question]:
        for q in self.questions:
            if q.question_id == qid:
                return q
        return None


@dataclass
class Student:
    student_id: str
    name: str
    exams_taken: Dict[str, List['ExamAttempt']] = field(default_factory=dict)  # exam_id -> attempts
    scores_history: Dict[str, List['Result']] = field(default_factory=dict)

    def attempts_for_exam(self, exam_id: str) -> List['ExamAttempt']:
        return self.exams_taken.get(exam_id, [])


@dataclass
class ExamAttempt:
    attempt_id: str
    student: Student
    exam: Exam
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    answers_submitted: Dict[str, Any] = field(default_factory=dict)  # question_id -> answer
    score: Optional[float] = None
    auto_submitted: bool = False

    def duration_seconds(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class Result:
    exam_attempt: ExamAttempt
    marks_obtained: float
    percentage: float
    grade: str
    rank: Optional[int] = None


@dataclass
class Certificate:
    certificate_id: str
    student: Student
    exam: Exam
    date_issued: datetime
    grade: str
    message: str

# --- Exam Manager / Logic ---

class ExamManager:
    PASS_PERCENTAGE = 50.0

    def __init__(self):
        # store attempts by exam id
        self.attempts_by_exam: Dict[str, List[ExamAttempt]] = {}
        # analytics counters
        self.question_stats: Dict[str, Dict[str, int]] = {}  # qid -> {'attempts': n, 'correct': m}

    # ----- Attempt lifecycle -----

    def can_start_attempt(self, student: Student, exam: Exam, now: Optional[datetime] = None) -> Tuple[bool, str]:
        now = now or datetime.utcnow()
        attempts = student.attempts_for_exam(exam.exam_id)
        if len(attempts) >= exam.max_attempts:
            return False, "Maximum attempts reached."
        if attempts:
            last_end = attempts[-1].end_time
            if last_end:
                allowed_after = last_end + timedelta(days=exam.cooling_period_days)
                if now < allowed_after:
                    return False, f"Cooling period active until {allowed_after.isoformat()}."
        return True, "Allowed"

    def start_attempt(self, student: Student, exam: Exam) -> ExamAttempt:
        allowed, msg = self.can_start_attempt(student, exam)
        if not allowed:
            raise PermissionError(msg)
        attempt = ExamAttempt(attempt_id=str(uuid.uuid4()), student=student, exam=exam)
        attempt.start_time = datetime.utcnow()
        # record in student
        student.exams_taken.setdefault(exam.exam_id, []).append(attempt)
        # record globally
        self.attempts_by_exam.setdefault(exam.exam_id, []).append(attempt)
        # initialize question stats
        for q in exam.questions:
            self.question_stats.setdefault(q.question_id, {'attempts': 0, 'correct': 0})
        return attempt

    def submit_attempt(self, attempt: ExamAttempt, answers: Optional[Dict[str, Any]] = None, auto: bool = False) -> Result:
        # merge answers
        if answers:
            attempt.answers_submitted.update(answers)
        attempt.end_time = datetime.utcnow()
        attempt.auto_submitted = auto or attempt.auto_submitted
        # grade
        marks = self.grade_attempt(attempt)
        percentage = (marks / attempt.exam.total_marks * 100) if attempt.exam.total_marks else 0.0
        grade = self.assign_grade(percentage)
        res = Result(exam_attempt=attempt, marks_obtained=marks, percentage=round(percentage, 2), grade=grade)
        # record in student
        attempt.student.scores_history.setdefault(attempt.exam.exam_id, []).append(res)
        # update ranks for exam
        self._update_ranks(attempt.exam.exam_id)
        return res

    # ----- Grading -----

    def grade_attempt(self, attempt: ExamAttempt) -> float:
        total = 0.0
        for q in attempt.exam.questions:
            stats = self.question_stats.setdefault(q.question_id, {'attempts': 0, 'correct': 0})
            stats['attempts'] += 1
            ans = attempt.answers_submitted.get(q.question_id)
            if q.question_type == 'MCQ' or q.question_type == 'True-False':
                if ans is not None and ans == q.correct_answer:
                    total += q.marks
                    stats['correct'] += 1
            else:
                # Descriptive: leave for manual grading; for simple demo, 0 by default
                pass
        attempt.score = total
        return round(total, 2)

    def assign_grade(self, percentage: float) -> str:
        if percentage >= 90:
            return 'A'
        if percentage >= 75:
            return 'B'
        if percentage >= 60:
            return 'C'
        if percentage >= 50:
            return 'D'
        return 'F'

    # ----- Ranks & analytics -----

    def _update_ranks(self, exam_id: str) -> None:
        attempts = [res for att in self.attempts_by_exam.get(exam_id, []) for res in att.student.scores_history.get(exam_id, [])]
        # flatten unique latest results by student (use their best percentage)
        best_by_student: Dict[str, Result] = {}
        for r in attempts:
            sid = r.exam_attempt.student.student_id
            existing = best_by_student.get(sid)
            if (existing is None) or (r.percentage > existing.percentage):
                best_by_student[sid] = r
        # sort
        ranked = sorted(best_by_student.values(), key=lambda x: x.percentage, reverse=True)
        for i, r in enumerate(ranked, start=1):
            r.rank = i

    def get_rank_for_result(self, result: Result) -> Optional[int]:
        return result.rank

    def question_accuracy(self, exam: Exam) -> Dict[str, float]:
        # returns question_id -> accuracy percent
        out = {}
        for q in exam.questions:
            s = self.question_stats.get(q.question_id, {'attempts': 0, 'correct': 0})
            attempts = s['attempts']
            correct = s['correct']
            out[q.question_id] = (correct / attempts * 100) if attempts > 0 else 0.0
        return out

    def difficulty_analysis(self, exam: Exam) -> Dict[str, Dict[str, float]]:
        # group questions by difficulty and compute average accuracy
        groups: Dict[str, List[float]] = {}
        for q in exam.questions:
            acc = self.question_accuracy(exam).get(q.question_id, 0.0)
            groups.setdefault(q.difficulty, []).append(acc)
        result = {}
        for diff, accs in groups.items():
            result[diff] = {
                'num_questions': len(accs),
                'avg_accuracy': round(sum(accs) / len(accs), 2) if accs else 0.0
            }
        return result

    # ----- Certificates -----

    def generate_certificate_if_passed(self, result: Result) -> Optional[Certificate]:
        if result.percentage >= ExamManager.PASS_PERCENTAGE:
            cert = Certificate(certificate_id=str(uuid.uuid4()),
                               student=result.exam_attempt.student,
                               exam=result.exam_attempt.exam,
                               date_issued=datetime.utcnow(),
                               grade=result.grade,
                               message=f"Certificate of completion for {result.exam_attempt.exam.subject}")
            return cert
        return None

# --- Exam Session Context Manager ---

class ExamSession:
    """
    Use as a context manager.
    """

    def __init__(self, manager: ExamManager, student: Student, exam: Exam):
        self.manager = manager
        self.student = student
        self.exam = exam
        self.attempt: Optional[ExamAttempt] = None
        self._timer: Optional[threading.Timer] = None
        self._submitted = False

    def __enter__(self) -> ExamAttempt:
        self.attempt = self.manager.start_attempt(self.student, self.exam)
        # start auto-submit timer
        seconds = max(1, int(self.exam.duration_minutes * 60))
        self._timer = threading.Timer(seconds, self._auto_submit)
        self._timer.start()
        print(f"Exam started for {self.student.name}. Auto-submit in {seconds} seconds.")
        return self.attempt

    def submit(self, answers: Dict[str, Any]) -> Result:
        if self._submitted:
            raise RuntimeError("Already submitted")
        if not self.attempt:
            raise RuntimeError("No active attempt")
        res = self.manager.submit_attempt(self.attempt, answers=answers, auto=False)
        self._submitted = True
        # cancel timer if still running
        if self._timer:
            self._timer.cancel()
        print(f"Submitted by user at {res.exam_attempt.end_time.isoformat()}, score: {res.marks_obtained}")
        return res

    def _auto_submit(self):
        if self._submitted or not self.attempt:
            return
        print("Time expired — auto-submitting exam...")
        # auto-submit with whatever answers are present
        res = self.manager.submit_attempt(self.attempt, answers=None, auto=True)
        self._submitted = True
        print(f"Auto-submitted at {res.exam_attempt.end_time.isoformat()}, score: {res.marks_obtained}")

    def __exit__(self, exc_type, exc, tb):
        # if not yet submitted, submit automatically
        if not self._submitted and self.attempt:
            print("Exiting session — auto-submitting remaining answers.")
            self.manager.submit_attempt(self.attempt, answers=None, auto=True)
            self._submitted = True
        if self._timer:
            self._timer.cancel()
        return False  # don't suppress exceptions

# --- Demo ---

if __name__ == "__main__":
    # Create exam with questions
    q1 = Question(question_id='Q1', question_text='2+2=?', options=['1', '2', '3', '4'], correct_answer='4', marks=2, question_type='MCQ', difficulty='Easy')
    q2 = Question(question_id='Q2', question_text='The earth is flat.', options=['True', 'False'], correct_answer='False', marks=1, question_type='True-False', difficulty='Easy')
    q3 = Question(question_id='Q3', question_text='Explain polymorphism.', options=[], correct_answer=None, marks=5, question_type='Descriptive', difficulty='Hard')

    exam = Exam(exam_id='EX-001', subject='General Knowledge', duration_minutes=0.1, total_marks=8, difficulty='Mixed')
    exam.add_question(q1)
    exam.add_question(q2)
    exam.add_question(q3)

    # Create students
    s1 = Student(student_id='S1', name='Sayantan')
    s2 = Student(student_id='S2', name='Sourish')

    manager = ExamManager()

    # Student 1 session (will auto-submit because duration is short)
    with ExamSession(manager, s1, exam) as attempt1:
        # submit partial answers immediately
        answers1 = {'Q1': '4', 'Q2': 'False'}
        res1 = manager.submit_attempt(attempt1, answers=answers1)
        cert1 = manager.generate_certificate_if_passed(res1)
        print(f"Result S1: {res1.marks_obtained}, {res1.percentage}%, Grade: {res1.grade}")
        if cert1:
            print(f"Certificate issued: {cert1.certificate_id}")

    # Student 2 session - allow auto-submit after time expiry, no answers
    with ExamSession(manager, s2, exam) as attempt2:
        # don't submit; wait for auto-submit (timer length is small)
        pass

    # Analytics
    print('\nQuestion accuracy:')
    print(manager.question_accuracy(exam))

    print('\nDifficulty analysis:')
    print(manager.difficulty_analysis(exam))

    # Ranking
    # collect latest results for exam
    all_results = []
    for stud in [s1, s2]:
        res_list = stud.scores_history.get(exam.exam_id, [])
        if res_list:
            all_results.extend(res_list)

    # Print ranks (if assigned)
    for r in all_results:
        print(f"Student {r.exam_attempt.student.name}: {r.percentage}%, Rank: {r.rank}")

    print('\nDemo complete.')
