import json
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Personal
from django.utils.text import slugify

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm()})

    if request.POST.get("password1") == request.POST.get("password2"):
        try:
            user = User.objects.create_user(
                request.POST["username"], password=request.POST["password1"]
            )
            user.save()
            login(request, user)
            return redirect(reverse('personal'))
        except IntegrityError:
            return render(request, 'signup.html', {
                "form": UserCreationForm(),
                "error": "El usuario ya existe."
            })
    
    return render(request, 'signup.html', {
        "form": UserCreationForm(),
        "error": "Las contraseñas no coinciden."
    })

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm()})

    user = authenticate(
        request,
        username=request.POST.get("username"),
        password=request.POST.get("password")
    )
    if user is None:
        return render(request, 'signin.html', {
            "form": AuthenticationForm(),
            "error": "Usuario o contraseña incorrectos."
        })
    
    login(request, user)
    return redirect(reverse('personal'))

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def personal(request):
    query = request.GET.get("q", "").strip()
    personal = Personal.objects.filter(user=request.user)

    if query:
        personal = personal.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(cedula__icontains=query)
        )

    total = personal.count()
    presentes = personal.filter(estado_asistencia__iexact='presente').count()
    ausentes = total - presentes

    context = {
        "personal": personal,
        "total": total,
        "presentes": presentes,
        "ausentes": ausentes,
        "query": query,
    }

    return render(request, 'personal.html', context)



@login_required
def detalle_personal(request, personal_id):
    persona = get_object_or_404(Personal, id=personal_id)
    return render(request, 'detalle_personal.html', {"persona": persona})

@login_required
def crear_personal(request):
    if request.method == 'POST':
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        cedula = request.POST.get("cedula", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()

        if not all([nombre, apellido, cedula, fecha_nacimiento]):
            return render(request, 'crear_personal.html', {
                "error": "Todos los campos son obligatorios."
            })

        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        except ValueError:
            return render(request, 'crear_personal.html', {
                "error": "Formato de fecha incorrecto. Use YYYY-MM-DD."
            })

        try:
            Personal.objects.create(
                user=request.user,
                nombre=nombre,
                apellido=apellido,
                cedula=cedula,
                fecha_nacimiento=fecha_nacimiento,
                estado_asistencia="Presente"
            )
            return redirect(reverse('personal'))
        except Exception as e:
            return render(request, 'crear_personal.html', {
                "error": f"Error al guardar el empleado: {str(e)}"
            })

    return render(request, 'crear_personal.html')

@login_required
def editar_personal(request, personal_id):
    persona = get_object_or_404(Personal, id=personal_id, user=request.user)  

    if request.method == 'POST':
        persona.nombre = request.POST.get("nombre")
        persona.apellido = request.POST.get("apellido")
        persona.cedula = request.POST.get("cedula")
        persona.fecha_nacimiento = datetime.strptime(request.POST.get("fecha_nacimiento"), "%Y-%m-%d").date()
        persona.estado_asistencia = request.POST.get("estado_asistencia", persona.estado_asistencia)

        persona.save()
        messages.success(request, "Datos actualizados correctamente.")
        return redirect(reverse('personal'))

    return render(request, 'editar_personal.html', {"persona": persona})

@login_required
def eliminar_personal(request, personal_id):
    persona = get_object_or_404(Personal, id=personal_id)
    
    if request.method == 'POST':
        persona.delete()
        return redirect(reverse('personal'))

    return render(request, 'eliminar_personal.html', {"persona": persona})

@csrf_exempt
def actualizar_asistencia(request, pk):
    if request.method == "POST":
        persona = get_object_or_404(Personal, pk=pk)
        nuevo_estado = request.POST.get("estado_asistencia", "Presente").strip()
        persona.estado_asistencia = nuevo_estado
        persona.save()
        return JsonResponse({"success": True, "estado_asistencia": persona.estado_asistencia})
    return JsonResponse({"success": False}, status=400)

@login_required
def generar_reporte_asistencia(request):
    usuario = request.user.username  
    fecha = datetime.now().strftime("%Y-%m-%d")  
    nombre_archivo = f"reporteAsistencia_{slugify(usuario)}_{fecha}.json"  

    ausentes = Personal.objects.filter(user=request.user).exclude(estado_asistencia__iexact='presente')

    reporte_ausentes = [
        {
            "id": persona.id,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "cedula": persona.cedula,
            "edad": persona.edad,  # Usar la propiedad directamente
            "estado_asistencia": persona.estado_asistencia
        }
        for persona in ausentes
    ]

    reporte = {
        "usuario": usuario,
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_ausentes": len(reporte_ausentes),
        "ausentes": reporte_ausentes,
    }

    response = HttpResponse(json.dumps(reporte, indent=4), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    return response

@login_required
def guardar_asistencia(request):
    if request.method == "POST":
        for persona in Personal.objects.all():
            estado_key = f"estado_asistencia_{persona.pk}"
            estado_nuevo = request.POST.get(estado_key, persona.estado_asistencia).strip()
            if estado_nuevo:
                persona.estado_asistencia = estado_nuevo
                persona.save()
        messages.success(request, "Asistencia guardada correctamente.")
    
    return redirect("personal")

def calcular_edad(fecha_nacimiento):
    """Función para calcular la edad con base en la fecha de nacimiento"""
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))