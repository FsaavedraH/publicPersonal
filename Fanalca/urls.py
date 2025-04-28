from django.contrib import admin
from django.urls import path
from personalAPP import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('personal/', views.personal, name='personal'),
    path('personal/crear/', views.crear_personal, name='crear_personal'),
    path('personal/<int:personal_id>/', views.detalle_personal, name='detalle_personal'),
    path('personal/<int:personal_id>/editar/', views.editar_personal, name='editar_personal'),
    path('personal/<int:personal_id>/eliminar/', views.eliminar_personal, name='eliminar_personal'),
    path('personal/asistencia/<int:pk>/', views.actualizar_asistencia, name='actualizar_asistencia'),
    path('personal/guardar_asistencia/', views.guardar_asistencia, name='guardar_asistencia'),
    path('personal/generar_reporte/', views.generar_reporte_asistencia, name='generar_reporte_asistencia'),
    path('logout/', views.signout, name='logout'),

]
