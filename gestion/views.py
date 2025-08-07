from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from io import BytesIO
import os, csv, zipfile

from workreport.decorators import group_required
from workreport.commons import get_float, get_or_none, get_param, get_session, set_session, show_exc, generate_qr, csv_export
from .models import Employee, Client, Report, ReportStatus, ReportAssociation, Note, InsuranceComp, Association

ACCESS_PATH="{}/gestion/assistances/client/".format(settings.MAIN_URL)


def init_session_date(request, key, days=0):
    #if not key in request.session:
    now = datetime.now()
    date = now + timedelta(days)
    set_session(request, key, date.strftime("%Y-%m-%d"))

def get_reports(request):
    #s_type = get_session(request, "s_type")
    #charged = get_session(request, "s_charged")
    exp = get_session(request, "s_exp")
    code = get_session(request, "s_code")
    status = get_session(request, "s_status")
    comp = get_session(request, "s_comp")
    emp = get_session(request, "s_emp")
    #value = get_session(request, "s_name")
    i_date = datetime.strptime("{} 00:00".format(get_session(request, "s_idate")), "%Y-%m-%d %H:%M")
    e_date = datetime.strptime("{} 23:59".format(get_session(request, "s_edate")), "%Y-%m-%d %H:%M")

    kwargs = {"date__gte": i_date, "date__lte": e_date}
    if exp != "":
        kwargs["exp"] = exp
    if code != "":
        kwargs["code"] = code
    #if value != "":
    #    kwargs["employee__name__icontains"] = value
    if status != "":
        kwargs["status__id"] = status
    if emp != "":
        kwargs["employee__id"] = emp
    if comp != "":
        kwargs["comp__id"] = comp
    #if s_type != "":
    #    kwargs["service_type__id"] = s_type
    #if charged == "1":
    #    kwargs["charged"] = True

    # print(kwargs)
    return Report.objects.filter(**kwargs).order_by("-date")

@group_required("admins",)
def index(request):
    init_session_date(request, "s_idate", -30)
    init_session_date(request, "s_edate")
    context = {
        "item_list": get_reports(request), 
        "notes": get_notes(request), 
        "association_list": Association.objects.all(),
        "emp_list": Employee.objects.all(),
        "comp_list": InsuranceComp.objects.all(),
        "status_list": ReportStatus.objects.all()
    }
    return render(request, "index.html", context)

@group_required("admins",)
def reports_list(request):
    return render(request, "reports-list.html", {"item_list": get_reports(request)})

@group_required("admins",)
def reports_search(request):
    set_session(request, "s_exp", get_param(request.GET, "s_exp"))
    set_session(request, "s_code", get_param(request.GET, "s_code"))
    #set_session(request, "s_name", get_param(request.GET, "s_name"))
    set_session(request, "s_emp", get_param(request.GET, "s_emp"))
    set_session(request, "s_idate", get_param(request.GET, "s_idate"))
    set_session(request, "s_edate", get_param(request.GET, "s_edate"))
    set_session(request, "s_status", get_param(request.GET, "s_status"))
    set_session(request, "s_comp", get_param(request.GET, "s_comp"))
    #set_session(request, "s_type", get_param(request.GET, "s_type"))
    #set_session(request, "s_charged", get_param(request.GET, "s_charged"))
    return render(request, "reports-list.html", {"item_list": get_reports(request)})

@group_required("admins",)
def reports_form(request):
    obj = get_or_none(Report, get_param(request.GET, "obj_id"))
    context = {
        'obj': obj, 
        'status_list': ReportStatus.objects.all(), 
        'association_list': Association.objects.all(), 
        'comp_list': InsuranceComp.objects.all(), 
        'emp_list': Employee.objects.all(), 
    }
    return render(request, "reports-form.html", context)

@group_required("admins",)
def reports_form_save(request):
    try:
        obj = get_or_none(Report, get_param(request.GET, "obj_id"))
        isNew = False
        if obj == None:
            obj = Report.objects.create()
            isNew = True
        comp_val = get_param(request.GET, "comp")
        comp = get_or_none(InsuranceComp, comp_val)
        if comp == None and not comp_val.isdigit():
            comp = InsuranceComp.objects.create(name=comp_val)
        association = get_or_none(Association, get_param(request.GET, "association"))
        status = get_or_none(ReportStatus, get_param(request.GET, "status"))
        emp = get_or_none(Employee, get_param(request.GET, "employee"))

        obj.code = get_param(request.GET, "code")
        obj.exp = get_param(request.GET, "exp")
        obj.name = get_param(request.GET, "name")
        obj.phone = get_param(request.GET, "phone")
        obj.address = get_param(request.GET, "address")
        obj.association = association
        obj.comp = comp
        obj.status = status
        obj.employee = emp
        obj.notes = get_param(request.GET, "notes")
        emp_date = get_param(request.GET, "emp_date")
        emp_time = get_param(request.GET, "emp_time")
        obj.emp_date = datetime.strptime("{} {}".format(emp_date, emp_time), "%Y-%m-%d %H:%M")
        if isNew:
            obj.date = datetime.now()
        obj.save()

        for key in request.GET.keys():
            if "association_" in key:
                association = get_or_none(Association, key.split("_")[1])
                ReportAssociation.objects.get_or_create(association=association, report=obj)
    except Exception as e:
        print (show_exc(e))
    return render(request, "reports-list.html", {"item_list": get_reports(request)})

@group_required("admins",)
def reports_remove(request):
    obj = get_or_none(Report, request.GET["obj_id"])
    if obj != None:
        obj.audio.delete(save=True)
        obj.delete()
    return render(request, "reports-list.html", {"item_list": get_reports(request)})

@group_required("admins",)
def reports_imgs_download(request, obj_id):
    rep = get_or_none(Report, obj_id)

    zip_buffer = BytesIO()
    # Crear el archivo ZIP
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for obj in rep.images.all():
            if obj.image:  
                image_path = obj.image.path  # Ruta absoluta del archivo
                if default_storage.exists(image_path):
                    # Leer la imagen y añadirla al ZIP con un nombre único
                    with default_storage.open(image_path, 'rb') as image_file:
                        zip_file.writestr(
                            os.path.basename(image_path),  # Nombre del archivo en el ZIP
                            image_file.read()
                        )
    # Preparar la respuesta HTTP con el ZIP
    zip_buffer.seek(0)  
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="images.zip"'
    return response
 
'''
    NOTES
'''
def get_notes(request, deleted=False):
    return Note.objects.filter(deleted=deleted)

@group_required("admins",)
def notes_list(request):
    deleted = True if get_param(request.GET, "deleted") == "True" else False
    return render(request, "notes/notes-list.html", {"notes": get_notes(request, deleted)})

@group_required("admins",)
def notes_search(request):
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})

@group_required("admins",)
def notes_form(request):
    obj = get_or_none(Note, get_param(request.GET, "obj_id"))
    return render(request, "notes/notes-form.html", {'obj': obj})

@group_required("admins",)
def notes_form_save(request):
    obj = get_or_none(Note, get_param(request.GET, "obj_id"))
    if obj == None:
        obj = Note.objects.create()
    obj.concept = get_param(request.GET, "concept")
    obj.save()
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})

@group_required("admins",)
def notes_remove(request):
    obj = get_or_none(Note, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.delete()
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})

@group_required("admins",)
def notes_remove_soft(request):
    obj = get_or_none(Note, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.deleted = True
        obj.save()
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})


'''
    EMPLOYEES
'''
def get_employees(request):
    search_value = get_session(request, "s_emp_name")
    filters_to_search = ["name__icontains",]
    full_query = Q()
    if search_value != "":
        for myfilter in filters_to_search:
            full_query |= Q(**{myfilter: search_value})
    return Employee.objects.filter(full_query)

@group_required("admins",)
def employees(request):
    init_session_date(request, "s_emp_idate")
    init_session_date(request, "s_emp_edate")
    return render(request, "employees/employees.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_list(request):
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_search(request):
    set_session(request, "s_emp_name", get_param(request.GET, "s_emp_name"))
    set_session(request, "s_emp_idate", get_param(request.GET, "s_emp_idate"))
    set_session(request, "s_emp_edate", get_param(request.GET, "s_emp_edate"))
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Employee, obj_id)
    if obj == None:
        obj = Employee.objects.create()
    return render(request, "employees/employees-form.html", {'obj': obj})

@group_required("admins",)
def employees_remove(request):
    obj = get_or_none(Employee, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        if obj.user != None:
            obj.user.delete()
        obj.delete()
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_save_email(request):
    try:
        obj = get_or_none(Employee, get_param(request.GET, "obj_id"))
        obj.email = get_param(request.GET, "value")
        obj.save()
        obj.save_user()
        return HttpResponse("Saved!")
    except Exception as e:
        return HttpResponse("Error: {}".format(e))

@group_required("admins",)
def employees_export(request):
    header = ['Nombre', 'Teléfono', 'Email', 'PIN', 'DNI', 'Horas trabajadas', 'Minutos trabajados']
    values = []
    items = get_employees(request)
    for item in items:
        hours, minutes = item.worked_time(request.session["s_emp_idate"], request.session["s_emp_edate"])
        row = [item.name, item.phone, item.email, item.pin, item.dni, hours, minutes]
        values.append(row)
    return csv_export(header, values, "empleados")

@group_required("admins",)
def employees_import(request):
    f = request.FILES["file"]
    lines = f.read().decode('latin-1').splitlines()
    i = 0
    for line in lines:
        if i > 0:
            l = line.split(";")
            #print(l)
            name = "{} {}".format(l[1], l[0])
            phone = l[2]
            email = l[7]
            dni = l[6]
            obj, created = Employee.objects.get_or_create(pin=dni, dni=dni, name=name, phone=phone, email=email)
            obj.save_user()
        i += 1
    return redirect("employees")

'''
    CLIENTS
'''
def get_clients(request):
    search_value = get_session(request, "s_cli_name")
    filters_to_search = ["name__icontains",]
    full_query = Q()
    if search_value != "":
        for myfilter in filters_to_search:
            full_query |= Q(**{myfilter: search_value})
    return Client.objects.filter(full_query).order_by("-id")[:50]

@group_required("admins",)
def clients(request):
    return render(request, "clients/clients.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_list(request):
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_search(request):
    set_session(request, "s_cli_name", get_param(request.GET, "s_cli_name"))
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Client, obj_id)
    new = False
    if obj == None:
        obj = Client.objects.create()
        url = "{}{}".format(ACCESS_PATH, obj.id)
        path = os.path.join(settings.BASE_DIR, "static", "images", "logo-asistencia-canaria.jpg")
        img_data = ContentFile(generate_qr(url, path))
        obj.qr.save('qr_{}.png'.format(obj.id), img_data, save=True)
        new = True
    return render(request, "clients/clients-form.html", {'obj': obj, 'new': new})

@group_required("admins",)
def clients_remove(request):
    obj = get_or_none(Client, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.qr.delete(save=True)
        obj.delete()
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_print_all_qr(request):
    return render(request, "clients/clients-print-all-qr.html", {"item_list": Client.objects.filter(inactive=False)})

@group_required("admins",)
def clients_print_qr(request, obj_id):
    return render(request, "clients/clients-print-qr.html", {"obj": get_or_none(Client, obj_id)})

@group_required("admins",)
def clients_reports(request, obj_id):
    return render(request, "clients/clients-reports.html", {"obj": get_or_none(Client, obj_id)})

'''
    Speech to text
'''
@csrf_exempt
def set_note_concept(request):
    #print("-- Guardando texto desde audio")
    #print(request.POST)
    token = get_param(request.POST, "token")
    text = get_param(request.POST, "text")
    report = get_or_none(Report, get_param(request.POST, "report"))
    note = get_or_none(Note, get_param(request.POST, "note"))
    if token == "1234":
        #print(text)
        report.audio_notes = text
        report.save()
    return HttpResponse("")

