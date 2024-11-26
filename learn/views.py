from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Course, Subject, Staff, Student, Question, Answer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import Staff, Course, Subject


def home(request):
    return render(request, 'index.html')

def service(request):
    return render(request, 'service.html')

def admin_dashboard(request):
    pending_staff = Staff.objects.filter(approved=False)
    pending_students = Student.objects.filter(approved=False)
    return render(request, 'admin_dashboard.html', {
        'pending_staff': pending_staff,
        'pending_students': pending_students,
    })  

def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')  

def student_dashboard(request):
    try:
        student = request.user.student
    except AttributeError:
        return HttpResponse("You are not authorized to access this page.")

    # Fetch purchased and available courses
    purchased_courses = student.purchased_courses.all()
    available_courses = Course.objects.all()

    selected_course = request.GET.get('course')
    selected_subject = request.GET.get('subject')

    # Mark the selected course for dropdown logic
    for course in purchased_courses:
        course.is_selected = selected_course and str(course.id) == selected_course

    subjects = None
    questions = None

    if selected_course:
        subjects = Subject.objects.filter(course_id=selected_course)
        for subject in subjects:
            subject.is_selected = selected_subject and str(subject.id) == selected_subject

    # Handle course purchase
    if request.method == "POST" and "purchase_course" in request.POST:
        course_id = request.POST.get('purchase_course')
        course = Course.objects.get(id=course_id)
        student.purchased_courses.add(course)
        return redirect('student_dashboard')

    # Handle course deletion
    if request.method == "POST" and "delete_course" in request.POST:
        course_id = request.POST.get('delete_course')
        course = Course.objects.get(id=course_id)
        student.purchased_courses.remove(course)
        return redirect('student_dashboard')

    context = {
        'available_courses': available_courses,
        'purchased_courses': purchased_courses,
        'selected_course': selected_course,
        'subjects': subjects,
        'selected_subject': selected_subject,
    }
    return render(request, 'student_dashboard.html', context)

def your_courses(request):
    # Ensure the user is a student
    try:
        student = request.user.student
    except AttributeError:
        return HttpResponse("You are not authorized to access this page.")
    
    # Fetch the purchased courses
    purchased_courses = student.purchased_courses.all()

    # Handle course deletion
    if request.method == 'POST' and 'delete_course' in request.POST:
        course_id = request.POST.get('delete_course')
        course = Course.objects.get(id=course_id)
        student.purchased_courses.remove(course)  # Remove course from student's purchased list

        # Redirect back to the courses page
        return redirect('your_courses')  # Assuming the URL name is 'your_courses'

    context = {
        'purchased_courses': purchased_courses,
    }
    return render(request, 'course/your_courses.html', context)

# Course Views
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course/course_list.html', {'courses': courses})

def course_create(request):
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        code = request.POST['code']
        price = request.POST['price']  # Get the price from the form
        Course.objects.create(name=name, description=description, code=code, price=price)
        return redirect('course_list')
    return render(request, 'course/create_course.html')

def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.name = request.POST['name']
        course.description = request.POST['description']
        course.code = request.POST['code']
        course.price = request.POST['price']  # Update the price
        course.save()
        return redirect('course_list')
    return render(request, 'course/create_course.html', {'course': course})

def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect('course_list')
    return render(request, 'course/course_delete.html', {'course': course})

# Subject Views

def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject/subject_list.html', {'subjects': subjects})

def subject_create(request):
    if request.method == "POST":
        name = request.POST['name']
        code = request.POST['code']
        course_id = request.POST['course']  # Assuming you get course ID from a dropdown
        course = get_object_or_404(Course, id=course_id)
        Subject.objects.create(name=name, code=code, course=course)
        return redirect('subject_list')
    courses = Course.objects.all()  # For the dropdown
    return render(request, 'subject/subject_form.html', {'courses': courses})

def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        subject.name = request.POST['name']
        subject.code = request.POST['code']
        course_id = request.POST['course']
        subject.course = get_object_or_404(Course, id=course_id)
        subject.save()
        return redirect('subject_list')
    courses = Course.objects.all()
    return render(request, 'subject/subject_form.html', {'subject': subject, 'courses': courses})

def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        subject.delete()
        return redirect('subject_list')
    return render(request, 'subject/subject_delete.html', {'subject': subject})

def staff_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        # Create the User
        user = User.objects.create_user(username=username, password=password, email=email)
        Staff.objects.create(user=user)  # Create the Staff profile
        return redirect('login')
    
    return render(request, 'staff_register.html')

def student_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        enrollment_number = request.POST['enrollment_number']
        
        # Create the User
        user = User.objects.create_user(username=username, password=password, email=email)
        Student.objects.create(user=user, enrollment_number=enrollment_number)  # Create the Student profile
        return redirect('login')
    
    return render(request, 'student_register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'staff'):
                if user.staff.approved:
                    return redirect('staff_dashboard')
                else:
                    return render(request, 'login.html', {'error_message': 'Staff account is not approved.'})
            elif hasattr(user, 'student'):
                if user.student.approved:
                    return redirect('student_dashboard')
                else:
                    return render(request, 'login.html', {'error_message': 'Student account is not approved.'})
            else:
                return redirect('home')
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    
    return render(request, 'login.html') 
    
from django.http import Http404

def approve_user(request, user_id, user_type):

    if request.method == "POST":
        try:
            if user_type == 'staff':
                user = Staff.objects.get(id=user_id)  # Use get instead of get_object_or_404
                user.approved = True
                user.save()
            elif user_type == 'student':
                user = Student.objects.get(id=user_id)  # Use get instead of get_object_or_404
                user.approved = True
                user.save()
            return redirect('admin_dashboard')
        except Staff.DoesNotExist:
            raise Http404("Staff user does not exist.")
        except Student.DoesNotExist:
            raise Http404("Student user does not exist.")
    return redirect('admin_dashboard')


def reject_user(request, user_id, user_type):
    if request.method == "POST":  # Ensure it only processes POST requests
        if user_type == 'staff':
            user = get_object_or_404(Staff, id=user_id)
            user.user.delete()  # Delete the user account
            user.delete()  # Delete the staff profile
        elif user_type == 'student':
            user = get_object_or_404(Student, id=user_id)
            user.user.delete()  # Delete the user account
            user.delete()  # Delete the student profile
        return redirect('admin_dashboard')  # Redirect back to the admin dashboard
    return redirect('admin_dashboard')  # Redirect if not a POST request

def logout_view(request):
    logout(request)
    return render(request,'login.html')

def staff_list(request):
    staffs=Staff.objects.all()
    return render(request, 'staff_list.html',{'staffs':staffs})
def course_list_view(request):
    courses=Course.objects.all()
    return render(request,'course_list_only.html',{'courses':courses})
def subject_list_view(request):
    subjects=Course.objects.all()
    return render(request,'subject/subject_list_only.html',{'subjects':subjects})
def question_list(request):
    questions=Question.objects.all()
    return render(request,'question_list.html',{'questions':questions})

def assign_course_and_subjects(request):
    courses = Course.objects.all()  # Get all available courses
    subjects = Subject.objects.all()  # Get all available subjects
    staffs = Staff.objects.all()  # Get all available staff members

    if request.method == 'POST':
        staff_id = request.POST.get('staff')  # Get selected staff member
        course_id = request.POST.get('course')
        subject_ids = request.POST.getlist('subjects')  # List of selected subject IDs

        # Check if a staff member is selected
        if staff_id:
            staff_member = get_object_or_404(Staff, id=staff_id)
            
            # Assign the course if selected
            if course_id:
                staff_member.course = Course.objects.get(id=course_id)

            # Assign the selected subjects
            if subject_ids:
                selected_subjects = Subject.objects.filter(id__in=subject_ids)
                staff_member.subjects.set(selected_subjects)  # Set selected subjects for staff

            staff_member.save()  # Save the changes to the staff member
            return redirect('staff_list')  # Redirect to a staff list or detail page
        else:
            return render(request, 'assign_course_and_subjects.html', {
                'courses': courses,
                'subjects': subjects,
                'staffs': staffs,
                'error': 'Please select a staff member.'
            })

    return render(request, 'assign_course_and_subjects.html', {
        'courses': courses,
        'subjects': subjects,
        'staffs': staffs
    })

def add_question_and_answers(request):
    if request.method == 'POST':
        # Get data from the form
        course_id = request.POST.get('course')
        subject_id = request.POST.get('subject')
        question_text = request.POST.get('question_text')  # Corresponds to the 'text' field in the model
        answers = request.POST.getlist('answers')  # Get the list of answers
        correct_answer = request.POST.get('correct_answer')  # The index of the correct answer

        try:
            # Fetch the course and subject from the database
            course = Course.objects.get(id=course_id)
            subject = Subject.objects.get(id=subject_id)

            # Ensure that the subject belongs to the selected course
            if subject.course != course:
                raise ValueError("The subject does not belong to the selected course.")

        except (Course.DoesNotExist, Subject.DoesNotExist) as e:
            return render(request, 'add_question_and_answers.html', {'error': str(e)})

        # Create the question object
        question = Question.objects.create(
            text=question_text,  # Save the question text
            subject=subject
        )

        # Save each answer for the created question
        for idx, answer_text in enumerate(answers):
            is_correct = (idx == int(correct_answer))  # Mark the correct answer based on the index
            Answer.objects.create(
                question=question,
                text=answer_text,  # Save the answer text
                is_correct=is_correct
            )

        # Redirect to a page showing the list of questions (or another appropriate view)
        return redirect('question_list')  # Replace with the URL name of your question list view

    else:
        # For GET requests, send available courses and subjects to the template
        courses = Course.objects.all()
        subjects = Subject.objects.all()
        return render(request, 'add_question_and_answers.html', {'courses': courses, 'subjects': subjects})

def select_exam(request):
    """View for students to select course and subject."""
    courses = Course.objects.all()
    if request.method == 'POST':
        course_id = request.POST.get('course')
        subject_id = request.POST.get('subject')
        return redirect('exam_portal', course_id=course_id, subject_id=subject_id)
    
    return render(request, 'select_exam.html', {'courses': courses})

def exam_portal(request, course_id, subject_id):
    course = get_object_or_404(Course, id=course_id)
    subject = get_object_or_404(Subject, id=subject_id)
    questions = Question.objects.filter(subject=subject).order_by('id')
    total_questions = questions.count()

    if total_questions == 0:
        return HttpResponse("No questions available for this subject.")

    if 'question_index' not in request.session:
        request.session['question_index'] = 0
        request.session['score'] = 0

    question_index = request.session['question_index']

    if question_index >= total_questions:
        return redirect('submit_exam', course_id=course_id, subject_id=subject_id)

    question = questions[question_index]

    if request.method == 'POST':
        selected_answer_id = request.POST.get('answer')
        if selected_answer_id:
            try:
                selected_answer = question.answers.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    request.session['score'] += 1
            except:
                pass

        request.session['question_index'] += 1
        return redirect('exam_portal', course_id=course_id, subject_id=subject_id)

    return render(request, 'exam_portal.html', {
        'course': course,
        'subject': subject,
        'question': question,
        'question_index': question_index + 1,
        'total_questions': total_questions,
    })

def submit_exam(request, course_id, subject_id):
    course = get_object_or_404(Course, id=course_id)
    subject = get_object_or_404(Subject, id=subject_id)

    score = request.session.get('score', 0)
    total_questions = Question.objects.filter(subject=subject).count()

    # Clear session data to reset for future exams
    if 'score' in request.session:
        del request.session['score']
    if 'question_index' in request.session:
        del request.session['question_index']

    return render(request, 'submit_exam.html', {
        'course': course,
        'subject': subject,
        'score': score,
        'total_questions': total_questions,
    })
