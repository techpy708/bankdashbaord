from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
# Create your views here.

from django.contrib.auth import logout
from django.shortcuts import redirect

@login_required
def LogoutView(request):
    logout(request)
    return redirect('login')

User = get_user_model()


from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Observation  # Replace with your actual Observation model import
from django.db.models import Q
from datetime import date

@login_required
def dashboard(request):

    user = request.user

    branch_filter = request.GET.get('branch_code', '')
    department_filter = request.GET.get('department', '')
    # Default financial year (current year - next year)
    current_year = date.today().year
    default_financial_year = f"{current_year}-{current_year+1}"

    financial_year_filter = request.GET.get('financial_year', default_financial_year)

    observations = Observation.objects.all()

    
    if branch_filter:
        observations = observations.filter(branch_code=branch_filter)
    if department_filter:
        observations = observations.filter(department=department_filter)
    if financial_year_filter:
        observations = observations.filter(financial_year=financial_year_filter)

    total_unique_branch_codes = BankMaster.objects.values_list('branch_code', flat=True).distinct().count()
    total_departments = observations.values('department').distinct().count()

    # ✅ Only count OPEN/CLOSED with approved = YES
    total_open = observations.filter(status="OPEN").count()
    total_closed = observations.filter(status="CLOSED", approved="YES").count()
    # Inside your dashboard view
    total_high_risk = observations.filter(risk_category="High").count()
    total_medium_risk = observations.filter(risk_category="Medium").count()
    total_low_risk = observations.filter(risk_category="Low").count()
    print(total_high_risk)


    # total_blank_observations = observations.filter(status='').count()

    # Filter users by branch if branch filter is selected
    if branch_filter:
        users = User.objects.filter(branch_code=branch_filter)
    else:
        users = User.objects.all()
    total_users = users.count()

    # Role-based filtering for all_branches
    if user.user_role == 'Branch Manager':
        all_branches = [user.branch_code]  # Return only the user's branch_code
    else:
        all_branches = BankMaster.objects.values_list('branch_code', flat=True).distinct().order_by('branch_code')


    if user.user_role == 'HO Manager':
        all_departments = user.departments.values_list('name', flat=True)  # Return only the user's branch_code
    else:
        all_departments = Department.objects.values_list('name', flat=True).distinct().order_by('name')

    return render(request, 'dashboard.html', {
        'total_unique_branch_codes': total_unique_branch_codes,
        'total_departments': total_departments,
        'total_open': total_open,
        'total_closed': total_closed,
        'total_high_risk': total_high_risk,
        'total_medium_risk': total_medium_risk,
        'total_low_risk': total_low_risk,
        'total_users': total_users,
        'all_branches': all_branches,
        'all_departments': all_departments,
        'branch_filter': branch_filter,
        'department_filter': department_filter,
        'financial_year_filter': financial_year_filter,
    })



import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Observation


from django.shortcuts import redirect
from django.contrib import messages

from django.contrib import messages

from django.contrib.auth import get_user_model
import pandas as pd
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Observation

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import pandas as pd
from .models import Observation

@login_required
def import_observations(request):
    if request.method == "POST":
        financial_year = request.POST.get("financial_year")
        period = request.POST.get("period")
        audit_type = request.POST.get("audit_type")  # FIXED: from corrected HTML form
        due_date = request.POST.get("due_date") or None
        email_recipients_ids = request.POST.getlist("email_recipients")
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "No file uploaded.")
            return render(request, "import_observation.html")

        try:
            df = pd.read_excel(file)
        except Exception:
            messages.error(request, "Invalid Excel file.")
            return render(request, "import_observation.html")

        observations_to_create = []
        for _, row in df.iterrows():
            obs = Observation(
            point=row.get("point", "") if pd.notna(row.get("point")) else "",
            branch_code=row.get("branch_code", "") if pd.notna(row.get("branch_code")) else "",
            category=row.get("category", "") if pd.notna(row.get("category")) else "",
            department=row.get("department", "") if pd.notna(row.get("department")) else "",
            checklist=row.get("checklist", "") if pd.notna(row.get("checklist")) else "",
            auditors_remarks=row.get("auditors_remarks", "") if pd.notna(row.get("auditors_remarks")) else "",
            risk_category=row.get("risk_category", "") if pd.notna(row.get("risk_category")) else "",
            branch_remarks=row.get("branch_remarks", "") if pd.notna(row.get("branch_remarks")) else "",
            ho_remarks=row.get("ho_remarks", "") if pd.notna(row.get("ho_remarks")) else "",
            status=row.get("status", "OPEN") if pd.notna(row.get("status")) else "OPEN",
            approved=row.get("approved", None) if pd.notna(row.get("approved")) else None,
            financial_year=financial_year,
            period=period,
            audit_type=audit_type,  # renamed from 'auditor_name' to match model field
            due_date=due_date,
            user=request.user,
        )

            observations_to_create.append(obs)

        saved_observations = Observation.objects.bulk_create(observations_to_create)

        # Many-to-many assignment (email_recipients)
        if email_recipients_ids:
            for obs in saved_observations:
                obs.email_recipients.set(email_recipients_ids)

        messages.success(request, f"✅ Successfully imported {len(saved_observations)} observations.")
        return redirect("import_observations")

    # For GET request: render form
    User = get_user_model()
    users = User.objects.all()
    return render(request, "import_observation.html", {"users": users})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Observation


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Observation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Observation

@login_required
def view_observations(request):

    user = request.user

    # Get filters
    branch_code = request.GET.get("branch_code", "").strip()
    department = request.GET.get("department", "").strip()
    financial_year = request.GET.get("financial_year", "").strip()
    period = request.GET.get("period", "").strip()
    risk_category = request.GET.get('risk_category', '').strip()
    status = request.GET.get('status', '').strip()


    # Start with empty queryset
    observations = Observation.objects.none()

    # Apply filters ONLY if any filter is used
    if branch_code or department or financial_year or period or risk_category or status:
        observations = Observation.objects.all()

        # 🔐 Apply role-based filtering
        if user.user_role != 'Admin':
            # Branch filtering
            if user.branch_code:
                observations = observations.filter(branch_code=user.branch_code)

            # Department filtering
            if user.departments.exists():
                dept_names = user.departments.values_list('name', flat=True)
                observations = observations.filter(department__in=dept_names)
            else:
                observations = observations.none()  # No departments, no access


        if branch_code:
            observations = observations.filter(branch_code=branch_code)

        if department:
            observations = observations.filter(department=department)

        if financial_year:
            observations = observations.filter(financial_year=financial_year)

        if period and period != "ALL":
            observations = observations.filter(period=period)

        if status:
            observations = observations.filter(status=status)

        if risk_category:
            observations = observations.filter(risk_category=risk_category)

    if user.user_role == 'Admin':
        branches = BankMaster.objects.all().order_by('branch_code')
        departments = Department.objects.all().order_by('name')
    else:
        branches = BankMaster.objects.filter(branch_code=user.branch_code)
        departments = user.departments.all().order_by('name')

    

    return render(request, "view_observation.html", {
        "observations": observations,
        "branch_code": branch_code,
        "department": department,
        "financial_year": financial_year,
        "period": period,
        "risk_category": risk_category,
        'all_branches': branches,
        'all_departments': departments,
        'status' : status,
        "user_role": request.user.user_role,
    })




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Observation  # adjust if your model is elsewhere
import json


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Observation  # Replace with your actual model import
import json

@login_required
@csrf_exempt
def update_observation(request, pk):
    if request.method == "POST":
        try:
            observation = Observation.objects.get(pk=pk)
            data = json.loads(request.body)

            new_status = data.get("status")
            new_approved = data.get("approved")
            new_branch_remarks = data.get("branch_remarks", "")
            new_ho_remarks = data.get("ho_remarks", "")

            if new_status not in ["OPEN", "CLOSED"]:
                return JsonResponse({"success": False, "error": "Invalid status"})

            if new_approved == "YES":
                observation.status = new_status
                observation.approved = "YES"
            elif new_approved == "DISCARD":
                # Force OPEN and clear approval
                observation.status = "OPEN"
                observation.approved = None
            else:
                # No approval, but still update status
                observation.status = new_status
                observation.approved = None

            # Update the new remarks fields
            observation.branch_remarks = new_branch_remarks
            observation.ho_remarks = new_ho_remarks

            observation.updated_by_user = request.user
            observation.save()

            return JsonResponse({"success": True})
        except Observation.DoesNotExist:
            return JsonResponse({"success": False, "error": "Observation not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})




from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse,HttpResponseBadRequest
from .models import Observation, ObservationFile

@login_required
def upload_files(request, observation_id):
    if request.method == "POST":
        observation = get_object_or_404(Observation, pk=observation_id)
        files = request.FILES.getlist('files')
        
        for f in files:
            file_data = f.read()  # binary content
            ObservationFile.objects.create(
                observation=observation,
                uploaded_by=request.user,
                file_name=f.name,
                file_data=file_data
            )
        return redirect(request.META.get('HTTP_REFERER', 'view_observations'))

    return HttpResponseBadRequest("Invalid request")


from django.http import HttpResponse

@login_required
def download_observation_file(request, file_id):
    obs_file = get_object_or_404(ObservationFile, pk=file_id)

    response = HttpResponse(obs_file.file_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{obs_file.file_name}"'
    return response


from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Observation, AnnexureFile

@login_required
def upload_annexure_files(request, observation_id):
    if request.method == "POST":
        observation = get_object_or_404(Observation, pk=observation_id)
        files = request.FILES.getlist('files')

        for f in files:
            file_data = f.read()  # binary content
            AnnexureFile.objects.create(
                observation=observation,
                uploaded_by=request.user,
                file_name=f.name,
                file_data=file_data
            )
        return redirect(request.META.get('HTTP_REFERER', 'view_observations'))
    return HttpResponseBadRequest("Invalid request")


from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import AnnexureFile
from django.shortcuts import get_object_or_404

@login_required
def download_annexure_file(request, file_id):
    annex_file = get_object_or_404(AnnexureFile, pk=file_id)

    response = HttpResponse(annex_file.file_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{annex_file.file_name}"'
    return response



@login_required
@csrf_exempt
def delete_observation(request, pk):
    if request.method == "POST":
        user = request.user
        # Check user role permission
        if user.user_role not in ['Admin', 'HO Audit']:
            return redirect('/dashboard/login/')
        
        try:
            obs = Observation.objects.get(pk=pk)
            obs.delete()
            return JsonResponse({"success": True})
        except Observation.DoesNotExist:
            return JsonResponse({"success": False, "error": "Observation not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)



from .forms import CustomUserSimpleForm,CustomPasswordChangeForm


User = get_user_model()


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department
from .forms import CustomUserSimpleForm  # your user form



from .models import BankMaster

@login_required
def add_user(request):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    


    edit_user = None
    all_departments = Department.objects.all().order_by('name')
    bank_branches = BankMaster.objects.all().order_by('branch_code')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        selected_departments = request.POST.getlist('departments')
        selected_departments_filtered = [d for d in selected_departments if d != "all"]
        selected_branch_code = request.POST.get('branch_code')

        # Get branch_name from BankMaster
        try:
            branch = BankMaster.objects.get(branch_code=selected_branch_code)
            selected_branch_name = branch.branch_name
        except BankMaster.DoesNotExist:
            selected_branch_name = ''

        if user_id:  # Editing
            edit_user = get_object_or_404(CustomUser, id=user_id)
            form = CustomUserSimpleForm(request.POST, instance=edit_user)
            if form.is_valid():
                user = form.save(commit=False)
                user.branch_code = selected_branch_code
                user.branch_name = selected_branch_name
                user.save()
                if "all" in selected_departments:
                    user.departments.set(all_departments)
                else:
                    user.departments.set(selected_departments_filtered)
                messages.success(request, 'User updated successfully.')
                return redirect('add_user')
        else:  # Adding new user
            form = CustomUserSimpleForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password('password123')
                user.branch_code = selected_branch_code
                user.branch_name = selected_branch_name
                user.save()
                if "all" in selected_departments:
                    user.departments.set(all_departments)
                else:
                    user.departments.set(selected_departments_filtered)
                messages.success(request, 'New user added successfully.')
                return redirect('add_user')
    else:
        user_id = request.GET.get('edit')
        if user_id:
            edit_user = get_object_or_404(CustomUser, id=user_id)
            form = CustomUserSimpleForm(instance=edit_user)
        else:
            form = CustomUserSimpleForm()

    users = CustomUser.objects.all()

    return render(request, 'add_user.html', {
        'form': form,
        'users': users,
        'edit_user': edit_user,
        'all_departments': all_departments,
        'bank_branches': bank_branches,   # pass branches to template
    })



from .models import CustomUser
from .models import CustomUser

@login_required
def delete_user(request, user_id):
    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')

    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')

    return redirect('add_user')



@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, 'Your password was updated successfully.')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'change_password.html', {'form': form})





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Department
from .forms import DepartmentForm, DepartmentUploadForm

from .forms import DepartmentForm, DepartmentUploadForm

@login_required
def manage_departments(request):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    
    edit_department = None
    if "edit" in request.GET:
        edit_department = get_object_or_404(Department, id=request.GET.get("edit"))

    if request.method == "POST":
        if request.POST.get("dept_id"):  # Editing
            dept = get_object_or_404(Department, id=request.POST.get("dept_id"))
            form = DepartmentForm(request.POST, instance=dept)
        else:  # Adding
            form = DepartmentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Department saved successfully!")
            return redirect("manage_departments")
    else:
        form = DepartmentForm(instance=edit_department) if edit_department else DepartmentForm()

    departments = Department.objects.all().order_by('name')
    upload_form = DepartmentUploadForm()  # <-- Add this

    return render(request, "department.html", {
        "form": form,
        "departments": departments,
        "edit_department": edit_department,
        "upload_form": upload_form,  # <-- pass it
    })



def delete_department(request, dept_id):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    
    department = get_object_or_404(Department, id=dept_id)
    department.delete()
    messages.success(request, "Department deleted successfully!")
    return redirect("manage_departments")

import csv
import chardet  # optional but recommended
import csv
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .forms import DepartmentUploadForm
from .models import Department
import csv
from django.shortcuts import redirect
from django.contrib import messages
from .forms import DepartmentUploadForm
from .models import Department


@login_required
def upload_departments(request):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    
    if request.method == "POST":
        upload_form = DepartmentUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file = request.FILES['file']
            raw_data = file.read()

            # Decode CSV safely
            try:
                decoded_file = raw_data.decode('utf-8').splitlines()
            except UnicodeDecodeError:
                decoded_file = raw_data.decode('latin-1').splitlines()

            reader = csv.reader(decoded_file)
            count = 0

            # Skip the first row (header)
            next(reader, None)

            for row in reader:
                if not row:
                    continue
                department_name = row[0].strip().replace('\x00', '')  # remove null bytes
                if department_name:
                    Department.objects.update_or_create(name=department_name)
                    count += 1

            messages.success(request, f"{count} departments imported successfully!")
        else:
            messages.error(request, "Invalid file upload.")

    return redirect("manage_departments")







import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BankMaster
from .forms import BankMasterForm, BankUploadForm

@login_required
def manage_banks(request):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    
    """Add, edit, list banks"""
    edit_bank = None
    if "edit" in request.GET:
        edit_bank = get_object_or_404(BankMaster, id=request.GET.get("edit"))

    if request.method == "POST":
        # Edit
        if request.POST.get("bank_id"):
            bank = get_object_or_404(BankMaster, id=request.POST.get("bank_id"))
            form = BankMasterForm(request.POST, instance=bank)
        else:  # Add
            form = BankMasterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Bank saved successfully!")
            return redirect("manage_banks")  # ✅ must match urls.py
    else:
        form = BankMasterForm(instance=edit_bank) if edit_bank else BankMasterForm()

    banks = BankMaster.objects.all().order_by('branch_code')
    upload_form = BankUploadForm()

    return render(request, "bank_master.html", {
        "form": form,
        "banks": banks,
        "edit_bank": edit_bank,
        "upload_form": upload_form,
    })

@login_required
def delete_bank(request, bank_id):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    
    """Delete a bank"""
    bank = get_object_or_404(BankMaster, id=bank_id)
    bank.delete()
    messages.success(request, "Bank deleted successfully!")
    return redirect("manage_banks")  # ✅ consistent

@login_required
def upload_banks(request):

    if request.user.user_role != 'Admin':
        return redirect('/dashboard/login/')
    
    """Bulk upload banks from CSV"""
    if request.method == "POST":
        upload_form = BankUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file = request.FILES['file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)

            count = 0
            next(reader, None)  # skips the first row
            for row in reader:
                if len(row) < 2:  # Expect branch_code, branch_name
                    continue
                branch_code, branch_name = row[0].strip(), row[1].strip()
                BankMaster.objects.update_or_create(
                    branch_code=branch_code,
                    defaults={'branch_name': branch_name}
                )
                count += 1

            messages.success(request, f"{count} banks imported successfully!")
        else:
            messages.error(request, "Invalid file upload.")

    return redirect("manage_banks")  # ✅ consistent






from django.shortcuts import render
from .models import Notification

from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def rbi_notifications(request):
    notifications_list = Notification.objects.all().order_by('-published_at')
    paginator = Paginator(notifications_list, 20)  # 20 per page

    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)

    return render(request, 'rbi_notifications.html', {'notifications': notifications})
