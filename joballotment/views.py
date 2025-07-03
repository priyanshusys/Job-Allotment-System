from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Job, Report, CustomUser
from .forms import JobForm, CustomUserCreationForm, JobAllotmentForm, ReportForm
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_user(user):
    return user.is_authenticated and user.role == 'user'

def is_supervisor(user):
    return user.is_authenticated and user.role == 'supervisor'

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == role:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'user':
                return redirect('user_dashboard')
            elif user.role == 'supervisor':
                return redirect('supervisor_dashboard')
        else:
            messages.error(request, 'Invalid credentials or role.')
    return render(request, 'joballotment/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_admin)
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job created successfully!')
            return redirect('admin_dashboard')
    else:
        form = JobForm()
    return render(request, 'joballotment/job_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'joballotment/user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def job_allotment(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = JobAllotmentForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job allotted successfully!')
            return redirect('admin_dashboard')
    else:
        form = JobAllotmentForm(instance=job)
    return render(request, 'joballotment/job_allotment_form.html', {'form': form, 'job': job})

@login_required
def report_submit(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.job = job
            report.submitted_by = request.user
            report.report_type = request.user.role
            # Supervisor report should be pending until admin verifies
            # if request.user.role == 'supervisor':
            #     report.status = 'verified'
            report.save()
            messages.success(request, 'Report submitted!')
            return redirect('user_dashboard' if request.user.role == 'user' else 'supervisor_dashboard')
    else:
        form = ReportForm()
    return render(request, 'joballotment/report_form.html', {'form': form, 'job': job})

@login_required
@user_passes_test(is_admin)
def report_verify(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        report.status = request.POST.get('status')
        report.save()
        if report.status == 'verified':
            report.job.status = 'completed'
            report.job.save()
        messages.success(request, 'Report status updated!')
        return redirect('admin_dashboard')
    return render(request, 'joballotment/report_verify_form.html', {'report': report})

@never_cache
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    jobs = Job.objects.all()
    reports = Report.objects.all()
    users = CustomUser.objects.all()
    searched_user_id = request.GET.get('search_user_id')
    searched_user_name = ''
    if searched_user_id:
        try:
            # Try numeric ID first
            if searched_user_id.isdigit():
                searched_user = CustomUser.objects.get(id=int(searched_user_id))
            else:
                searched_user = CustomUser.objects.get(username=searched_user_id)
            searched_user_name = searched_user.get_full_name() or searched_user.username
        except CustomUser.DoesNotExist:
            searched_user_name = 'User not found'
    if request.method == 'POST' and 'reset_password' in request.POST:
        reset_user_id = request.POST.get('reset_user_id')
        try:
            # Try numeric ID first
            if reset_user_id.isdigit():
                reset_user = CustomUser.objects.get(id=int(reset_user_id))
            else:
                reset_user = CustomUser.objects.get(username=reset_user_id)
            reset_user.set_password('user@1234')
            reset_user.save()
            messages.success(request, f"Password for {reset_user.username} reset to 'user@1234'.")
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found for password reset.')
        return HttpResponseRedirect(reverse('admin_dashboard'))
    # Build workflow status for each job
    job_user_statuses = {}
    job_supervisor_statuses = {}
    job_final_statuses = {}
    job_statuses = {}
    job_reports = {}
    for job in jobs:
        user_report = Report.objects.filter(job=job, report_type='user').first()
        supervisor_report = Report.objects.filter(job=job, report_type='supervisor').first()
        # User status
        if not user_report:
            user_status = 'Pending'
        elif user_report.status == 'verified':
            user_status = 'Completed'
        else:
            user_status = 'Submitted'
        # Supervisor status
        if not supervisor_report:
            supervisor_status = 'Pending'
        elif supervisor_report.status == 'verified':
            supervisor_status = 'Completed'
        else:
            supervisor_status = 'Submitted'
        # Final status
        if job.status == 'completed':
            final_status = 'Approved'
        elif supervisor_report and supervisor_report.status == 'verified' and job.status != 'completed':
            final_status = 'Verified by Admin'
        else:
            final_status = 'Pending'
        # Workflow status for enabling verify button
        if user_report and user_report.status == 'verified' and supervisor_report and supervisor_report.status == 'pending' and job.status != 'completed':
            job_statuses[job.id] = 'Ready for admin verification'
        else:
            job_statuses[job.id] = ''
        job_user_statuses[job.id] = user_status
        job_supervisor_statuses[job.id] = supervisor_status
        job_final_statuses[job.id] = final_status
        job_reports[job.id] = {
            'user': user_report,
            'supervisor': supervisor_report,
        }
    return render(request, 'joballotment/admin_dashboard.html', {
        'jobs': jobs,
        'reports': job_reports,
        'users': users,
        'job_user_statuses': job_user_statuses,
        'job_supervisor_statuses': job_supervisor_statuses,
        'job_final_statuses': job_final_statuses,
        'job_statuses': job_statuses,
        'searched_user_id': searched_user_id,
        'searched_user_name': searched_user_name,
    })

@login_required
def user_dashboard(request):
    jobs = request.user.jobs.all()
    reports = Report.objects.filter(submitted_by=request.user)
    total_jobs = jobs.count()
    completed_jobs = jobs.filter(status='completed').count()
    pending_jobs = jobs.filter(status='pending').count()
    # Map job.id to report status for the current user
    job_report_statuses = {}
    for job in jobs:
        report = reports.filter(job=job, report_type='user').first()
        if report:
            if report.status == 'verified':
                job_report_statuses[job.id] = 'Verified'
            else:
                job_report_statuses[job.id] = 'Submitted'
        else:
            job_report_statuses[job.id] = 'Pending'
    return render(request, 'joballotment/user_dashboard.html', {
        'jobs': jobs,
        'reports': reports,
        'total_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'pending_jobs': pending_jobs,
        'job_report_statuses': job_report_statuses,
    })

@login_required
def supervisor_dashboard(request):
    jobs = request.user.supervised_jobs.all()
    user_reports = Report.objects.filter(job__in=jobs, report_type='user')
    user_reports_to_review = user_reports.filter(status='pending')
    jobs_with_verified_user_report = [r.job.id for r in user_reports.filter(status='verified')]
    # Jobs where user report is verified but supervisor report not yet submitted
    pending_jobs_to_supervise = 0
    for job in jobs:
        user_report_verified = user_reports.filter(job=job, status='verified').exists()
        supervisor_report_exists = Report.objects.filter(job=job, report_type='supervisor').exists()
        if user_report_verified and not supervisor_report_exists:
            pending_jobs_to_supervise += 1
    pending_user_reports = user_reports_to_review.count()
    # Map job.id to supervisor report status for the current supervisor
    supervisor_reports = Report.objects.filter(job__in=jobs, report_type='supervisor', submitted_by=request.user)
    job_supervisor_report_statuses = {}
    for job in jobs:
        report = supervisor_reports.filter(job=job).first()
        if report:
            if job.status == 'completed':
                job_supervisor_report_statuses[job.id] = 'Verified'
            else:
                job_supervisor_report_statuses[job.id] = 'Submitted'
        else:
            job_supervisor_report_statuses[job.id] = 'Pending'
    return render(request, 'joballotment/supervisor_dashboard.html', {
        'jobs': jobs,
        'user_reports': user_reports,
        'supervisor_reports': supervisor_reports,
        'user_reports_to_review': user_reports_to_review,
        'jobs_with_verified_user_report': jobs_with_verified_user_report,
        'pending_jobs_to_supervise': pending_jobs_to_supervise,
        'pending_user_reports': pending_user_reports,
        'job_supervisor_report_statuses': job_supervisor_report_statuses,
    })

@login_required
def supervisor_verify_user_report(request, report_id):
    report = get_object_or_404(Report, id=report_id, report_type='user')
    if request.method == 'POST':
        report.status = 'verified'
        report.save()
        messages.success(request, 'User report verified!')
        return redirect('supervisor_dashboard')
    return render(request, 'joballotment/supervisor_verify_user_report.html', {'report': report})

@login_required
@user_passes_test(is_admin)
def job_delete(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'joballotment/job_confirm_delete.html', {'job': job})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    # Allow admin or the user who submitted the report
    if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin') or report.submitted_by == request.user:
        user_report = Report.objects.filter(job=report.job, report_type='user').first()
        supervisor_report = Report.objects.filter(job=report.job, report_type='supervisor').first()
        return render(request, 'joballotment/report_detail.html', {
            'report': report,
            'user_report': user_report,
            'supervisor_report': supervisor_report,
        })
    else:
        raise PermissionDenied
