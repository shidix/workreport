from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from datetime import datetime

import subprocess
import threading

from workreport.decorators import group_required_pwa
from workreport.commons import user_in_group, get_or_none, get_param, get_int
from gestion.models import Employee, Client, Report, ReportStatus, ReportImage, Note


@group_required_pwa("employees")
def index(request):
    try:
        return redirect(reverse('pwa-employee'))
    except:
        return redirect(reverse('pwa-login'))

def pin_login(request):
    CONTROL_KEY = "SZRf2QMpIfZHPEh0ib7YoDlnnDp5HtjDqbAw"
    msg = ""  
    if request.method == "POST":
        context =  {}
        msg = "Operación no permitida"
        pin = request.POST.get('pin', None)
        control_key = request.POST.get('control_key', None)
        if pin != None and control_key != None:
            if control_key == CONTROL_KEY:
                try:
                    emp = get_or_none(Employee, pin, "pin")
                    login(request, emp.user)
                    request.session['pwa_app_session'] = True
                    return redirect(reverse('pwa-employee'))
                except Exception as e:
                    msg = "Pin no válido"
                    print(e)
            else:
                msg = "Bad control"
    return render(request, "pwa-login.html", {'msg': msg})

def pin_logout(request):
    logout(request)
    return redirect(reverse('pwa-login'))

'''
    EMPLOYEES
'''
@group_required_pwa("employees")
def employee_home(request):
    #context = {"obj": request.user.employee}
    #if user_in_group(request.user, "admins"):
    #    context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/home.html", {"obj": request.user.employee})

@group_required_pwa("employees")
def employee_report(request, obj_id):
    report = get_or_none(Report, obj_id)
    return render(request, "pwa/employees/report.html", {"obj": report, "status_list": ReportStatus.objects.all()})

@group_required_pwa("employees")
def employee_report_new(request, obj_id=""):
    obj = get_or_none(Report, obj_id)
    #type_list = ServiceType.objects.all()
    status_list = ReportStatus.objects.all()
    client_list = Client.objects.all()
    employee_list = Employee.objects.all()
    context = {'obj':obj, 'status_list':status_list, 'employee_list':employee_list}
    return render(request, "pwa/employees/report_new.html", context)

@group_required_pwa("employees")
def employee_report_new_save(request):
    #s_type = get_or_none(ServiceType, get_param(request.POST, "report_type"))
    #client = get_or_none(Client, get_param(request.POST, "client"))
    #emp = get_or_none(Employee, get_param(request.POST, "employee"))
    #charged = get_param(request.GET, "charged")
    status = get_or_none(ReportStatus, get_param(request.POST, "status"))
    notes = get_param(request.POST, "notes")

    obj = get_or_none(Report, get_param(request.POST, "obj_id"))
    if obj == None:
        obj = Report.objects.create()
    #obj.report_type = s_type
    #obj.client = client
    obj.name = get_param(request.POST, "name")
    obj.phone = get_param(request.POST, "phone")
    obj.address = get_param(request.POST, "address")
    obj.status = status
    obj.employee = request.user.employee
    obj.notes = notes
    obj.save()

    if "img" in request.FILES and request.FILES["img"] != "":
        ReportImage.objects.create(report=obj, image=request.FILES["img"])
    #obj.charged = True if charged != "" else False
    return redirect(reverse("pwa-employee-report-new", kwargs={'obj_id': obj.id}))

@group_required_pwa("employees")
def employee_report_save(request):
    report = get_or_none(Report, get_param(request.POST, "report"))
    status = get_or_none(ReportStatus, get_param(request.POST, "status"))
    report.status = status
    report.emp_notes = get_param(request.POST, "emp_notes")
    report.audio_notes = get_param(request.POST, "audio_notes")
    report.save()

    if "audio" in request.FILES and request.FILES["audio"] != "":
        report.audio = request.FILES["audio"]
        report.save()
        t = threading.Thread(target=transcribe_audio, args=[report.audio.url, report.id], daemon=True)
        t.start()

    #if "img" in request.FILES and request.FILES["img"] != "":
    #    ReportImage.objects.create(report=report, image=request.FILES["img"])
    return redirect(reverse("pwa-employee"))
    #return redirect(reverse("pwa-employee-report", kwargs={'obj_id': report.id}))

@group_required_pwa("employees")
def employee_report_img_save(request):
    report = get_or_none(Report, get_param(request.POST, "obj_id"))
    if "file" in request.FILES and request.FILES["file"] != "":
        ReportImage.objects.create(report=report, image=request.FILES["file"])
    return render(request, "pwa/employees/report_images.html", {"obj": report})
    #return redirect(reverse("pwa-employee-report", kwargs={'obj_id': report.id}))
    
@group_required_pwa("employees")
def employee_report_img_remove(request):
    img = get_or_none(ReportImage, get_param(request.GET, "obj_id"))
    obj = None
    if img != None:
        obj = img.report
        img.image.delete(save=True)
        img.delete()
    return render(request, "pwa/employees/report_images.html", {"obj": obj})

@group_required_pwa("employees")
def employee_notes(request):
    context = {"obj": request.user.employee}
    if user_in_group(request.user, "admins"):
        context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/notes.html", context)

@group_required_pwa("employees")
def employee_note(request):
    return render(request, "pwa/employees/note.html", {})

def transcribe_audio(file, obj_id):
    #print("Transcribiendo...")
    #result = subprocess.run(["{}/transcribir.sh {} {}".format(settings.BASE_DIR, file, str(obj_id))])
    result = subprocess.run([settings.PYTHON_PATH, "{}/transcribir.py".format(settings.BASE_DIR), file, str(obj_id)])

@group_required_pwa("employees")
def employee_note_save(request):
    concept = get_param(request.POST, "concept")
    audio = None
    if "audio" in request.FILES and request.FILES["audio"] != "":
        audio = request.FILES["audio"]
        concept = "Esperando traducción de audio..."
    if concept != "" or audio != None:
        note = Note.objects.create(concept=concept, audio=audio)
        if "audio" in request.FILES and request.FILES["audio"] != "":
            t = threading.Thread(target=transcribe_audio, args=[note.audio.url], daemon=True)
            t.start()
    return redirect(reverse('pwa-employee'))

