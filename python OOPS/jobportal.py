from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


# CLASS 1: JobSeeker (People looking for jobs)

class JobSeeker:
    """Represents a person looking for a job"""
    
    # Class variable to store all job seekers (like a database)
    all_seekers = []
    
    def __init__(self, user_id: int, name: str, resume: str, skills_list: List[str], 
                 experience: int, education: str):
        """
        Initialize a new job seeker
        user_id: unique number for each person
        name: person's full name
        resume: text of their resume
        skills_list: list of skills like ["Python", "Communication"]
        experience: years of experience (number)
        education: degree like "Bachelor's in Computer Science"
        """
        self.user_id = user_id
        self.name = name
        self.resume = resume
        self.skills_list = [skill.lower() for skill in skills_list]  # Convert to lowercase for matching
        self.experience = experience
        self.education = education
        self.applications = []  # List to store all applications made by this person
        self.saved_jobs = []  # Jobs bookmarked by the user
        self.notifications = []  # Messages for the user
        self.job_alerts = []  # Preferences for job alerts
        
        # Add this seeker to the list of all seekers
        JobSeeker.all_seekers.append(self)
    
    def parse_resume(self, resume_text: str):
        """
        Extract skills and experience from resume text
        This simulates AI parsing (in real apps, this is complex!)
        """
        # Convert resume to lowercase for easier searching
        resume_lower = resume_text.lower()
        
        # Common skills to look for (simplified version)
        common_skills = ["python", "java", "javascript", "react", "sql", "communication",
                        "leadership", "teamwork", "project management", "excel"]
        
        # Find which skills are mentioned in the resume
        found_skills = []
        for skill in common_skills:
            if skill in resume_lower:
                found_skills.append(skill)
        
        # Update the skills list
        self.skills_list = list(set(self.skills_list + found_skills))  # Remove duplicates
        
        # Try to find experience (look for patterns like "3 years" or "5 years experience")
        experience_pattern = r'(\d+)\s*(?:years?|yrs?)'
        matches = re.findall(experience_pattern, resume_lower)
        if matches:
            # Take the highest number found
            self.experience = max([int(match) for match in matches])
        
        return f"Extracted {len(found_skills)} skills from resume"
    
    def apply_to_job(self, job_posting, cover_letter: str = ""):
        """
        Apply to a specific job
        Creates a new Application object
        """
        # Check if already applied
        for app in self.applications:
            if app.job.job_id == job_posting.job_id:
                return "You have already applied to this job!"
        
        # Create new application
        application = Application(
            application_id=len(Application.all_applications) + 1,
            job=job_posting,
            candidate=self,
            cover_letter=cover_letter
        )
        
        # Add to this seeker's applications list
        self.applications.append(application)
        
        # Add notification
        self.add_notification(f"You successfully applied to {job_posting.title} at {job_posting.employer.company_name}")
        
        return f"Application submitted successfully! Application ID: {application.application_id}"
    
    def save_job(self, job_posting):
        """Bookmark a job for later"""
        if job_posting not in self.saved_jobs:
            self.saved_jobs.append(job_posting)
            return f"Job saved: {job_posting.title}"
        return "Job already in saved list"
    
    def set_job_alert(self, keywords: List[str], location: str = None, min_salary: int = None):
        """
        Set preferences for job alerts
        System will notify when matching jobs are posted
        """
        alert = {
            "keywords": [k.lower() for k in keywords],
            "location": location.lower() if location else None,
            "min_salary": min_salary,
            "created_date": datetime.now()
        }
        self.job_alerts.append(alert)
        return "Job alert created successfully!"
    
    def add_notification(self, message: str):
        """Add a notification to user's inbox"""
        self.notifications.append({
            "message": message,
            "date": datetime.now(),
            "read": False
        })
    
    def get_unread_notifications(self):
        """Get all unread notifications"""
        return [n for n in self.notifications if not n["read"]]
    
    def __str__(self):
        return f"JobSeeker({self.name}, {self.experience} yrs exp, Skills: {len(self.skills_list)})"


# ==============================================
# CLASS 2: Employer (Companies hiring people)
# ==============================================
class Employer:
    """Represents a company that posts jobs"""
    
    # Class variable to store all employers
    all_employers = []
    
    def __init__(self, company_id: int, company_name: str, industry: str, employees_count: int):
        """
        Initialize a new employer
        company_id: unique number for each company
        company_name: name of the company
        industry: type of business (e.g., "Technology", "Healthcare")
        employees_count: total number of employees in the company
        """
        self.company_id = company_id
        self.company_name = company_name
        self.industry = industry
        self.jobs_posted = []  # List of all jobs posted by this company
        self.employees_count = employees_count
        self.employee_referrals = []  # Track employee referrals
        
        # Add to list of all employers
        Employer.all_employers.append(self)
    
    def post_job(self, title: str, description: str, requirements: List[str], 
                 salary_range: tuple, location: str):
        """
        Create and post a new job opening
        Returns the JobPosting object
        """
        # Create a new job posting
        job = JobPosting(
            job_id=len(JobPosting.all_postings) + 1,
            employer=self,  # This job belongs to this company
            title=title,
            description=description,
            requirements=requirements,
            salary_range=salary_range,
            location=location
        )
        
        # Add to company's list of posted jobs
        self.jobs_posted.append(job)
        
        # Check for matching job alerts and notify users
        self._notify_matching_candidates(job)
        
        return job
    
    def _notify_matching_candidates(self, job):
        """
        Internal method to notify candidates with matching job alerts
        """
        # Check all job seekers' alerts
        for seeker in JobSeeker.all_seekers:
            for alert in seeker.job_alerts:
                # Check if job matches alert criteria
                keywords_match = any(keyword in job.title.lower() or 
                                   keyword in job.description.lower() 
                                   for keyword in alert["keywords"])
                
                location_match = (alert["location"] is None or 
                                alert["location"] in job.location.lower())
                
                salary_match = (alert["min_salary"] is None or 
                              job.salary_range[0] >= alert["min_salary"])
                
                # If all criteria match, send notification
                if keywords_match and location_match and salary_match:
                    seeker.add_notification(
                        f"New job alert: {job.title} at {self.company_name} - {job.location}"
                    )
    
    def refer_candidate(self, employee_name: str, candidate: JobSeeker, job_posting):
        """
        Employee refers a candidate for a job
        Referrals often get priority in hiring
        """
        referral = {
            "employee": employee_name,
            "candidate": candidate,
            "job": job_posting,
            "date": datetime.now(),
            "status": "pending"
        }
        self.employee_referrals.append(referral)
        
        # Notify the candidate
        candidate.add_notification(
            f"You've been referred by {employee_name} for {job_posting.title} at {self.company_name}!"
        )
        
        return f"Referral created for {candidate.name}"
    
    def get_applications_for_job(self, job_id: int):
        """Get all applications for a specific job"""
        for job in self.jobs_posted:
            if job.job_id == job_id:
                return job.applications
        return []
    
    def __str__(self):
        return f"Employer({self.company_name}, {self.industry}, {len(self.jobs_posted)} jobs posted)"


# ==============================================
# CLASS 3: JobPosting (Individual job openings)
# ==============================================
class JobPosting:
    """Represents a single job opening"""
    
    # Class variable to store all job postings
    all_postings = []
    
    def __init__(self, job_id: int, employer: Employer, title: str, description: str,
                 requirements: List[str], salary_range: tuple, location: str):
        """
        Initialize a new job posting
        job_id: unique identifier
        employer: the Employer object that posted this job
        title: job title like "Software Engineer"
        description: detailed description of the job
        requirements: list of required skills
        salary_range: tuple like (60000, 80000) for min and max salary
        location: where the job is located
        """
        self.job_id = job_id
        self.employer = employer  # This creates the "belongs to" relationship
        self.title = title
        self.description = description
        self.requirements = [req.lower() for req in requirements]  # Lowercase for matching
        self.salary_range = salary_range  # (min, max)
        self.location = location
        self.posted_date = datetime.now()
        self.applications = []  # List of all applications for this job (has-many relationship)
        self.is_active = True  # Whether job is still open
        
        # Add to list of all postings
        JobPosting.all_postings.append(self)
    
    def calculate_match_percentage(self, candidate: JobSeeker) -> Dict:
        """
        Calculate how well a candidate matches this job
        Returns a dictionary with percentage and breakdown
        """
        # 1. SKILLS MATCHING (50% weight)
        matching_skills = []
        for req_skill in self.requirements:
            for candidate_skill in candidate.skills_list:
                if req_skill in candidate_skill or candidate_skill in req_skill:
                    matching_skills.append(req_skill)
                    break
        
        # Calculate skills match percentage
        if len(self.requirements) > 0:
            skills_match = (len(matching_skills) / len(self.requirements)) * 100
        else:
            skills_match = 100  # If no requirements, everyone matches
        
        # 2. EXPERIENCE MATCHING (30% weight)
        # Extract experience requirement from description (simplified)
        exp_required = 0
        description_lower = self.description.lower()
        if "entry level" in description_lower or "fresher" in description_lower:
            exp_required = 0
        elif "1 year" in description_lower or "1-2 years" in description_lower:
            exp_required = 1
        elif "3 years" in description_lower or "3-5 years" in description_lower:
            exp_required = 3
        elif "5 years" in description_lower or "5+ years" in description_lower:
            exp_required = 5
        
        # Calculate experience match
        if candidate.experience >= exp_required:
            experience_match = 100
        elif candidate.experience >= exp_required * 0.7:  # 70% of required experience
            experience_match = 70
        else:
            experience_match = max(0, (candidate.experience / max(exp_required, 1)) * 100)
        
        # 3. LOCATION MATCHING (20% weight)
        # Simple check: if "remote" is in job location or candidate is from same city
        location_match = 50  # Default neutral score
        if "remote" in self.location.lower():
            location_match = 100  # Remote jobs match everyone
        # In a real app, we'd compare candidate location with job location
        
        # CALCULATE WEIGHTED FINAL SCORE
        final_score = (
            skills_match * 0.5 +      # 50% weight
            experience_match * 0.3 +   # 30% weight
            location_match * 0.2       # 20% weight
        )
        
        return {
            "overall_match": round(final_score, 2),
            "skills_match": round(skills_match, 2),
            "experience_match": round(experience_match, 2),
            "location_match": round(location_match, 2),
            "matching_skills": matching_skills,
            "total_required_skills": len(self.requirements)
        }
    
    def get_top_candidates(self, top_n: int = 5):
        """
        Get top N candidates who applied, sorted by match percentage
        """
        if not self.applications:
            return []
        
        # Calculate match for each application
        candidates_with_scores = []
        for app in self.applications:
            match = self.calculate_match_percentage(app.candidate)
            candidates_with_scores.append({
                "application": app,
                "candidate": app.candidate,
                "match_score": match["overall_match"],
                "match_details": match
            })
        
        # Sort by match score (highest first)
        candidates_with_scores.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Return top N
        return candidates_with_scores[:top_n]
    
    def close_job(self):
        """Mark job as no longer accepting applications"""
        self.is_active = False
        # Notify all applicants
        for app in self.applications:
            if app.status == "applied":
                app.candidate.add_notification(
                    f"The position '{self.title}' at {self.employer.company_name} has been filled."
                )
    
    @classmethod
    def get_applications_per_job_stats(cls):
        """
        Class method: Calculate average applications per job posting
        Analytics for the platform
        """
        if not cls.all_postings:
            return {"average": 0, "total_jobs": 0, "total_applications": 0}
        
        total_apps = sum(len(job.applications) for job in cls.all_postings)
        total_jobs = len(cls.all_postings)
        
        return {
            "average": round(total_apps / total_jobs, 2),
            "total_jobs": total_jobs,
            "total_applications": total_apps,
            "most_applied": max(cls.all_postings, key=lambda j: len(j.applications)) if cls.all_postings else None
        }
    
    def __str__(self):
        return f"JobPosting({self.title} at {self.employer.company_name}, {len(self.applications)} applications)"


# ==============================================
# CLASS 4: Application (When someone applies)
# ==============================================
class Application:
    """Represents a job application"""
    
    # Class variable to store all applications
    all_applications = []
    
    # Possible statuses for tracking
    STATUS_CHOICES = ["applied", "reviewed", "interview", "rejected", "offered"]
    
    def __init__(self, application_id: int, job: JobPosting, candidate: JobSeeker,
                 cover_letter: str = ""):
        """
        Initialize a new application
        application_id: unique identifier
        job: the JobPosting being applied to
        candidate: the JobSeeker who is applying
        cover_letter: optional cover letter text
        """
        self.application_id = application_id
        self.job = job
        self.candidate = candidate
        self.status = "applied"  # Start with "applied" status
        self.applied_date = datetime.now()
        self.resume = candidate.resume  # Copy of resume at time of application
        self.cover_letter = cover_letter
        self.status_history = [{"status": "applied", "date": datetime.now()}]  # Track changes
        self.interviews = []  # List of Interview objects
        
        # Add to the job's list of applications
        job.applications.append(self)
        
        # Add to list of all applications
        Application.all_applications.append(self)
    
    def update_status(self, new_status: str, notes: str = ""):
        """
        Change the application status and notify the candidate
        """
        if new_status not in self.STATUS_CHOICES:
            return f"Invalid status. Must be one of: {self.STATUS_CHOICES}"
        
        old_status = self.status
        self.status = new_status
        
        # Record in history
        self.status_history.append({
            "status": new_status,
            "date": datetime.now(),
            "notes": notes
        })
        
        # NOTIFICATION SYSTEM - Notify candidate of status change
        notification_messages = {
            "reviewed": f"Your application for {self.job.title} at {self.job.employer.company_name} is being reviewed!",
            "interview": f"Great news! You've been selected for an interview for {self.job.title} at {self.job.employer.company_name}!",
            "rejected": f"Thank you for your interest in {self.job.title} at {self.job.employer.company_name}. Unfortunately, we've decided to move forward with other candidates.",
            "offered": f"Congratulations! You've received a job offer for {self.job.title} at {self.job.employer.company_name}!"
        }
        
        if new_status in notification_messages:
            self.candidate.add_notification(notification_messages[new_status])
        
        return f"Status updated from '{old_status}' to '{new_status}'"
    
    def schedule_interview(self, scheduled_date: datetime, interviewer: str):
        """
        Schedule an interview for this application
        Creates an Interview object
        """
        # Update application status to interview
        if self.status != "interview":
            self.update_status("interview")
        
        # Create interview
        interview = Interview(
            application=self,
            scheduled_date=scheduled_date,
            interviewer=interviewer
        )
        
        self.interviews.append(interview)
        
        # Notify candidate
        self.candidate.add_notification(
            f"Interview scheduled for {self.job.title} on {scheduled_date.strftime('%B %d, %Y at %I:%M %p')} with {interviewer}"
        )
        
        return interview
    
    def get_time_in_current_status(self):
        """Calculate how long application has been in current status"""
        if self.status_history:
            last_change = self.status_history[-1]["date"]
            return datetime.now() - last_change
        return timedelta(0)
    
    @classmethod
    def calculate_time_to_hire(cls):
        """
        Class method: Calculate average time from application to offer
        Analytics for the platform
        """
        hired_applications = [app for app in cls.all_applications if app.status == "offered"]
        
        if not hired_applications:
            return {"average_days": 0, "total_hired": 0}
        
        total_days = 0
        for app in hired_applications:
            # Time from applied to offered
            applied_date = app.applied_date
            offered_date = next(
                (h["date"] for h in app.status_history if h["status"] == "offered"),
                datetime.now()
            )
            days = (offered_date - applied_date).days
            total_days += days
        
        return {
            "average_days": round(total_days / len(hired_applications), 2),
            "total_hired": len(hired_applications),
            "fastest_hire_days": min((datetime.now() - app.applied_date).days for app in hired_applications)
        }
    
    def __str__(self):
        return f"Application({self.candidate.name} -> {self.job.title}, Status: {self.status})"


# ==============================================
# CLASS 5: Interview (Scheduled meetings)
# ==============================================
class Interview:
    """Represents a job interview"""
    
    # Class variable to store all interviews
    all_interviews = []
    
    def __init__(self, application: Application, scheduled_date: datetime, interviewer: str):
        """
        Initialize a new interview
        application: the Application this interview is for
        scheduled_date: when the interview is scheduled
        interviewer: name of the person conducting the interview
        """
        self.application = application
        self.scheduled_date = scheduled_date
        self.interviewer = interviewer
        self.feedback = ""  # Interviewer's notes
        self.result = None  # "pass" or "fail"
        self.completed = False
        self.completed_date = None
        
        # Add to list of all interviews
        Interview.all_interviews.append(self)
    
    def complete_interview(self, feedback: str, result: str):
        """
        Record interview results
        result: "pass" or "fail"
        """
        if result not in ["pass", "fail"]:
            return "Result must be 'pass' or 'fail'"
        
        self.feedback = feedback
        self.result = result
        self.completed = True
        self.completed_date = datetime.now()
        
        # Update application status based on result
        if result == "pass":
            self.application.update_status("interview", "Interview passed, moving forward")
        else:
            self.application.update_status("rejected", "Did not pass interview stage")
        
        # Notify candidate
        if result == "pass":
            self.application.candidate.add_notification(
                f"You passed the interview for {self.application.job.title}! Next steps coming soon."
            )
        
        return f"Interview marked as complete with result: {result}"
    
    def reschedule(self, new_date: datetime):
        """Change interview date"""
        old_date = self.scheduled_date
        self.scheduled_date = new_date
        
        # Notify candidate
        self.application.candidate.add_notification(
            f"Your interview for {self.application.job.title} has been rescheduled to {new_date.strftime('%B %d, %Y at %I:%M %p')}"
        )
        
        return f"Interview rescheduled from {old_date} to {new_date}"
    
    def get_upcoming_interviews(days: int = 7):
        """
        Class method: Get all interviews scheduled in the next N days
        """
        cutoff_date = datetime.now() + timedelta(days=days)
        upcoming = [
            interview for interview in Interview.all_interviews
            if not interview.completed and interview.scheduled_date <= cutoff_date
        ]
        return sorted(upcoming, key=lambda i: i.scheduled_date)
    
    def __str__(self):
        status = "Completed" if self.completed else "Scheduled"
        return f"Interview({self.application.candidate.name}, {status}, {self.scheduled_date.strftime('%Y-%m-%d')})"


# ==============================================
# DEMONSTRATION / TESTING
# ==============================================
def demo_platform():
    """
    Demonstrate how the platform works with example data
    """
    print("=" * 60)
    print("LINKEDIN-LIKE JOB SEARCH PLATFORM DEMO")
    print("=" * 60)
    
    # 1. CREATE EMPLOYERS
    print("\n1️⃣  Creating Employers...")
    tech_corp = Employer(
        company_id=1,
        company_name="TechCorp Solutions",
        industry="Technology",
        employees_count=500
    )
    
    health_inc = Employer(
        company_id=2,
        company_name="HealthCare Inc",
        industry="Healthcare",
        employees_count=1200
    )
    print(f"   ✓ Created: {tech_corp}")
    print(f"   ✓ Created: {health_inc}")
    
    # 2. CREATE JOB POSTINGS
    print("\n2️⃣  Posting Jobs...")
    job1 = tech_corp.post_job(
        title="Junior Python Developer",
        description="We're looking for an entry level Python developer with 1-2 years experience. Great opportunity for freshers!",
        requirements=["Python", "SQL", "Git", "Communication"],
        salary_range=(50000, 70000),
        location="Remote"
    )
    
    job2 = tech_corp.post_job(
        title="Senior Software Engineer",
        description="Looking for a senior developer with 5+ years experience in full-stack development.",
        requirements=["Python", "JavaScript", "React", "SQL", "Leadership"],
        salary_range=(90000, 120000),
        location="New York, NY"
    )
    
    job3 = health_inc.post_job(
        title="Data Analyst",
        description="Analyze healthcare data to improve patient outcomes. 3 years experience required.",
        requirements=["SQL", "Excel", "Python", "Communication"],
        salary_range=(60000, 80000),
        location="Boston, MA"
    )
    print(f"   ✓ Posted: {job1.title} at {tech_corp.company_name}")
    print(f"   ✓ Posted: {job2.title} at {tech_corp.company_name}")
    print(f"   ✓ Posted: {job3.title} at {health_inc.company_name}")
    
    # 3. CREATE JOB SEEKERS
    print("\n3️⃣  Creating Job Seekers...")
    
    resume1 = """
    Recent graduate with strong Python programming skills. Built several projects using
    Python, SQL, and Git. Excellent communication skills and eager to learn. 1 year
    internship experience at a tech startup.
    """
    
    candidate1 = JobSeeker(
        user_id=1,
        name="Alice Johnson",
        resume=resume1,
        skills_list=["Python", "SQL", "Git"],
        experience=1,
        education="Bachelor's in Computer Science"
    )
    
    resume2 = """
    Experienced software engineer with 6 years in full-stack development. Expert in
    Python, JavaScript, React, and SQL. Led teams of 5+ developers. Strong leadership
    and project management skills.
    """
    
    candidate2 = JobSeeker(
        user_id=2,
        name="Bob Smith",
        resume=resume2,
        skills_list=["Python", "JavaScript", "React", "SQL", "Leadership", "Project Management"],
        experience=6,
        education="Master's in Computer Science"
    )
    
    resume3 = """
    Data analyst with 3 years experience in healthcare industry. Proficient in SQL,
    Excel, and Python for data analysis. Created dashboards and reports for executive
    team. Strong analytical and communication skills.
    """
    
    candidate3 = JobSeeker(
        user_id=3,
        name="Carol White",
        resume=resume3,
        skills_list=["SQL", "Excel", "Python", "Communication"],
        experience=3,
        education="Bachelor's in Statistics"
    )
    
    print(f"   ✓ Created: {candidate1}")
    print(f"   ✓ Created: {candidate2}")
    print(f"   ✓ Created: {candidate3}")
    
    # 4. PARSE RESUMES (Extract additional skills)
    print("\n4️⃣  Parsing Resumes...")
    result = candidate1.parse_resume(candidate1.resume)
    print(f"   Alice: {result} - Updated skills: {candidate1.skills_list}")
    
    # 5. SET JOB ALERTS
    print("\n5️⃣  Setting Job Alerts...")
    candidate1.set_job_alert(keywords=["Python", "Developer"], location="Remote", min_salary=40000)
    print(f"   Alice set alert for: Python, Developer jobs in Remote")
    
    # 6. CALCULATE JOB MATCHES
    print("\n6️⃣  Calculating Job Matches...")
    print(f"\n   Alice vs {job1.title}:")
    match1 = job1.calculate_match_percentage(candidate1)
    print(f"   Overall Match: {match1['overall_match']}%")
    print(f"   - Skills Match: {match1['skills_match']}% (Matched: {match1['matching_skills']})")
    print(f"   - Experience Match: {match1['experience_match']}%")
    print(f"   - Location Match: {match1['location_match']}%")
    
    print(f"\n   Bob vs {job2.title}:")
    match2 = job2.calculate_match_percentage(candidate2)
    print(f"   Overall Match: {match2['overall_match']}%")
    print(f"   - Skills Match: {match2['skills_match']}% (Matched: {match2['matching_skills']})")
    print(f"   - Experience Match: {match2['experience_match']}%")
    
    # 7. APPLY TO JOBS
    print("\n7️⃣  Candidates Applying to Jobs...")
    candidate1.apply_to_job(job1, "I'm excited about this entry-level position!")
    candidate1.save_job(job2)  # Save for later
    candidate2.apply_to_job(job2, "With 6 years of experience, I'm ready to lead your team!")
    candidate2.apply_to_job(job1, "Happy to mentor junior developers too!")
    candidate3.apply_to_job(job3, "My healthcare experience makes me perfect for this role!")
    
    print(f"   ✓ Alice applied to: {job1.title}")
    print(f"   ✓ Bob applied to: {job2.title} and {job1.title}")
    print(f"   ✓ Carol applied to: {job3.title}")
    print(f"   ✓ Alice saved {job2.title} for later")
    
    # 8. CHECK NOTIFICATIONS
    print("\n8️⃣  Checking Notifications...")
    alice_notifications = candidate1.get_unread_notifications()
    print(f"   Alice has {len(alice_notifications)} unread notifications:")
    for notif in alice_notifications[:3]:  # Show first 3
        print(f"   - {notif['message']}")
    
    # 9. EMPLOYER REVIEWS APPLICATIONS
    print("\n9️⃣  Employer Reviewing Applications...")
    
    # Get Alice's application
    alice_app = candidate1.applications[0]
    print(f"   Current status: {alice_app.status}")
    
    # Move to reviewed
    alice_app.update_status("reviewed", "Good candidate, scheduling interview")
    print(f"   ✓ Updated to: {alice_app.status}")
    
    # Get top candidates for job1
    print(f"\n   Top candidates for {job1.title}:")
    top_candidates = job1.get_top_candidates(top_n=3)
    for i, candidate_info in enumerate(top_candidates, 1):
        print(f"   {i}. {candidate_info['candidate'].name} - Match: {candidate_info['match_score']}%")
    
    # 10. SCHEDULE INTERVIEWS
    print("\n🔟 Scheduling Interviews...")
    interview_date = datetime.now() + timedelta(days=3)
    interview1 = alice_app.schedule_interview(
        scheduled_date=interview_date,
        interviewer="John Manager"
    )
    print(f"   ✓ Interview scheduled for Alice on {interview_date.strftime('%B %d, %Y')}")
    print(f"   Current application status: {alice_app.status}")
    
    # 11. COMPLETE INTERVIEW
    print("\n1️⃣1️⃣  Conducting Interview...")
    interview1.complete_interview(
        feedback="Great technical skills and enthusiasm. Good cultural fit.",
        result="pass"
    )
    print(f"   ✓ Interview completed with result: {interview1.result}")
    print(f"   Feedback: {interview1.feedback}")
    
    # 12. MAKE JOB OFFER
    print("\n1️⃣2️⃣  Making Job Offer...")
    alice_app.update_status("offered", "Extending offer at $65,000")
    print(f"   ✓ Job offer made to Alice!")
    print(f"   Final status: {alice_app.status}")
    
    # Check notifications again
    new_notifications = candidate1.get_unread_notifications()
    print(f"\n   Alice's new notifications ({len(new_notifications)}):")
    for notif in new_notifications[-2:]:  # Show last 2
        print(f"   - {notif['message']}")
    
    # 13. EMPLOYEE REFERRAL SYSTEM
    print("\n1️⃣3️⃣  Employee Referral System...")
    
    # Create a new candidate
    candidate4 = JobSeeker(
        user_id=4,
        name="David Brown",
        resume="Software developer with 2 years experience in Python and React.",
        skills_list=["Python", "React", "JavaScript"],
        experience=2,
        education="Bachelor's in Computer Science"
    )
    
    # Alice (now an employee) refers David
    tech_corp.refer_candidate(
        employee_name="Alice Johnson",
        candidate=candidate4,
        job_posting=job2
    )
    print(f"   ✓ Alice referred David for {job2.title}")
    print(f"   Total referrals at TechCorp: {len(tech_corp.employee_referrals)}")
    
    # 14. REJECTION SCENARIO
    print("\n1️⃣4️⃣  Handling Rejections...")
    bob_app_job1 = candidate2.applications[1]  # Bob's application to job1
    bob_app_job1.update_status("reviewed", "Overqualified for this position")
    bob_app_job1.update_status("rejected", "Better suited for senior roles")
    print(f"   ✓ Bob's application to {job1.title}: {bob_app_job1.status}")
    
    # 15. PLATFORM ANALYTICS
    print("\n1️⃣5️⃣  Platform Analytics...")
    
    # Applications per job
    app_stats = JobPosting.get_applications_per_job_stats()
    print(f"   Average applications per job: {app_stats['average']}")
    print(f"   Total jobs posted: {app_stats['total_jobs']}")
    print(f"   Total applications: {app_stats['total_applications']}")
    if app_stats['most_applied']:
        print(f"   Most popular job: {app_stats['most_applied'].title} ({len(app_stats['most_applied'].applications)} applications)")
    
    # Time to hire
    hire_stats = Application.calculate_time_to_hire()
    print(f"\n   Time to hire statistics:")
    print(f"   Average days to hire: {hire_stats['average_days']}")
    print(f"   Total hired: {hire_stats['total_hired']}")
    
    # 16. APPLICATION STATUS TRACKING
    print("\n1️⃣6️⃣  Application Tracking System...")
    print(f"\n   Alice's application history for {job1.title}:")
    for i, history in enumerate(alice_app.status_history, 1):
        print(f"   {i}. {history['status'].upper()} - {history['date'].strftime('%B %d, %Y at %I:%M %p')}")
        if history.get('notes'):
            print(f"      Notes: {history['notes']}")
    
    # 17. SAVED JOBS FEATURE
    print("\n 17.  Saved Jobs...")
    print(f"   Alice's saved jobs: {len(candidate1.saved_jobs)}")
    for saved_job in candidate1.saved_jobs:
        print(f"   - {saved_job.title} at {saved_job.employer.company_name}")
    
    # 18. UPCOMING INTERVIEWS
    print("\n 18.  Upcoming Interviews (Next 7 Days)...")
    
    # Schedule another interview for demonstration
    bob_app = candidate2.applications[0]  # Bob's application to job2
    bob_app.update_status("interview")
    interview_date_bob = datetime.now() + timedelta(days=5)
    interview2 = bob_app.schedule_interview(
        scheduled_date=interview_date_bob,
        interviewer="Sarah Director"
    )
    
    upcoming = Interview.get_upcoming_interviews(days=7)
    print(f"   Total upcoming interviews: {len(upcoming)}")
    for interview in upcoming:
        print(f"   - {interview.application.candidate.name} for {interview.application.job.title}")
        print(f"     Date: {interview.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}")
        print(f"     Interviewer: {interview.interviewer}")
    
    # 19. JOB ALERT MATCHING
    print("\19.  Job Alert System...")
    print(f"   Alice's job alerts: {len(candidate1.job_alerts)}")
    for alert in candidate1.job_alerts:
        print(f"   - Keywords: {alert['keywords']}")
        print(f"     Location: {alert['location']}")
        print(f"     Min Salary: ${alert['min_salary']}")
    
    # Post a new job to trigger alert
    print("\n   Posting new job to trigger alert...")
    job4 = tech_corp.post_job(
        title="Python Developer - Remote",
        description="Remote Python developer needed for exciting projects.",
        requirements=["Python", "Git"],
        salary_range=(55000, 75000),
        location="Remote"
    )
    print(f"   ✓ New job posted: {job4.title}")
    print(f"   ✓ Job alerts triggered and notifications sent!")
    
    # 20. FINAL SUMMARY
    print("\n" + "=" * 60)
    print("PLATFORM SUMMARY")
    print("=" * 60)
    print(f"Total Employers: {len(Employer.all_employers)}")
    print(f"Total Job Seekers: {len(JobSeeker.all_seekers)}")
    print(f"Total Job Postings: {len(JobPosting.all_postings)}")
    print(f"Total Applications: {len(Application.all_applications)}")
    print(f"Total Interviews: {len(Interview.all_interviews)}")
    
    print("\nApplication Status Breakdown:")
    status_count = {}
    for app in Application.all_applications:
        status_count[app.status] = status_count.get(app.status, 0) + 1
    for status, count in status_count.items():
        print(f"  {status.upper()}: {count}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully! ")
    print("=" * 60)


# Run the demonstration
if __name__ == "__main__":
    demo_platform()