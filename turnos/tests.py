from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import ConfiguracionClinica, Paciente, Tratamiento, Turno


class SistemaTurnosOdontologiaTests(TestCase):
    def test_landing_page_y_datos_demo_iniciales(self):
        response = self.client.get(reverse("landing_cliente"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dra. Mariana Sánchez de Bustamante")
        self.assertContains(response, "Calle Belgrano")
        self.assertTrue(Tratamiento.objects.count() >= 6)
        self.assertTrue(Turno.objects.count() >= 5)

    def test_api_horarios_disponibles(self):
        self.client.get(reverse("landing_cliente"))
        manana = timezone.localdate() + timedelta(days=2)
        if manana.weekday() == 6:
            manana += timedelta(days=1)

        resp = self.client.get(reverse("api_horarios_disponibles"), {"fecha": manana.isoformat()})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["fecha"], manana.isoformat())
        self.assertFalse(data["es_domingo"])
        self.assertTrue(len(data["slots"]) > 0)

    def test_reserva_turno_web_cliente_y_comprobante(self):
        self.client.get(reverse("landing_cliente"))
        trat = Tratamiento.objects.first()
        fecha_futura = timezone.localdate() + timedelta(days=4)
        if fecha_futura.weekday() == 6:
            fecha_futura += timedelta(days=1)

        resp = self.client.post(
            reverse("reservar_turno_cliente"),
            {
                "nombre_completo": "Carolina Alvear",
                "dni": "40112233",
                "telefono": "11 6000-1234",
                "email": "carolina@test.com",
                "obra_social": "OSDE",
                "numero_afiliado": "123456",
                "tratamiento_id": trat.id,
                "fecha": fecha_futura.isoformat(),
                "hora": "11:00",
                "motivo_notas": "Control general",
            },
        )
        turno = Turno.objects.get(paciente__dni="40112233")
        self.assertRedirects(resp, reverse("comprobante_turno", kwargs={"codigo": turno.codigo}))

        comp_resp = self.client.get(reverse("comprobante_turno", kwargs={"codigo": turno.codigo}))
        self.assertEqual(comp_resp.status_code, 200)
        self.assertContains(comp_resp, turno.codigo)
        self.assertContains(comp_resp, "Carolina Alvear")

    def test_login_y_dashboard_secretaria_cargar_turno(self):
        self.client.get(reverse("landing_cliente"))
        # Login rápido como secretaria
        login_resp = self.client.post(reverse("login_secretaria"), {"acceso_rapido": "secretaria"})
        self.assertRedirects(login_resp, reverse("dashboard_secretaria"))

        dash_resp = self.client.get(reverse("dashboard_secretaria"))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Registrar Turno en Servidor")

        trat = Tratamiento.objects.first()
        fecha_futura = timezone.localdate() + timedelta(days=5)
        if fecha_futura.weekday() == 6:
            fecha_futura += timedelta(days=1)

        crear_resp = self.client.post(
            reverse("crear_turno_secretaria"),
            {
                "nombre_completo": "Federico Bustos",
                "dni": "35998877",
                "telefono": "11 4444-5555",
                "obra_social": "Swiss Medical",
                "tratamiento_id": trat.id,
                "fecha": fecha_futura.isoformat(),
                "hora": "16:00",
                "estado": "CONFIRMADO",
                "origen": "SECRETARIA",
                "notas_secretaria": "Agendado por teléfono por Laura",
            },
        )
        self.assertEqual(crear_resp.status_code, 302)
        self.assertTrue(Turno.objects.filter(paciente__dni="35998877", estado="CONFIRMADO").exists())
