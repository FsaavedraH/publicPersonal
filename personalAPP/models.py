from django.db import models
from datetime import date
from django.contrib.auth.models import User

class Personal(models.Model):
    ESTADOS_ASISTENCIA = [
        ('Presente', 'Presente'),
        ('PP3', 'Permiso personal por tres horas'),
        ('PP4', 'Permiso personal por cuatro horas'),
        ('CC', 'Cambio de contrato'),
        ('PR', 'Permiso remunerado'),
        ('PNR', 'Permiso no remunerado'),
        ('IL', 'Incapacidad laboral'),
        ('IG', 'Incapacidad general'),
        ('PM', 'Permiso de maternidad'),
        ('PP', 'Permiso de paternidad'),
        ('LT15', 'Llegada tarde por 15 minutos'),
        ('L', 'Licencia'),
        ('FSS', 'Falta sin soporte'),
        ('CD', 'Calamidad doméstica'),
        ('SP', 'Suspendido'),
        ('SC', 'Sin contratar'),
        ('CM', 'Cita médica'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    apellido = models.CharField(max_length=100, null=False, blank=False)
    cedula = models.BigIntegerField(unique=True, null=False, blank=False)
    fecha_nacimiento = models.DateField(null=False, blank=False)
    estado_asistencia = models.CharField(
        max_length=50,
        choices=ESTADOS_ASISTENCIA,
        blank=False,
        null=False,
        default='Presente'  
    )

    @property
    def edad(self):
        """ Calcula la edad en tiempo real sin necesidad de almacenarla """
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {str(self.cedula)}"
