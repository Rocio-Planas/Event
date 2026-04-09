# virtualEvent/tests.py
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.db import models
from datetime import timedelta
from virtualEvent.models import VirtualEvent, OnlineViewer, EventAnalytics
from ve_streaming.models import StreamingRoom
from ve_chat.models import (
    ChatMessage,
    HandRaise,
    Poll,
    PollOption,
    PollVote,
    SatisfactionRating,
)
from usuarios.models import Usuario


class FullInteractionTest(TestCase):
    """Prueba integrada que simula múltiples usuarios en un evento en vivo."""

    @classmethod
    def setUpTestData(cls):
        # 1. Crear organizador y 3 espectadores
        cls.organizer = Usuario.objects.create_user(
            email="org@test.com", password="pass"
        )
        cls.viewer1 = Usuario.objects.create_user(
            email="view1@test.com", password="pass"
        )
        cls.viewer2 = Usuario.objects.create_user(
            email="view2@test.com", password="pass"
        )
        cls.viewer3 = Usuario.objects.create_user(
            email="view3@test.com", password="pass"
        )

        # Añadir atributo username ficticio para compatibilidad con vistas (solo pruebas)
        cls.organizer.username = cls.organizer.email
        cls.viewer1.username = cls.viewer1.email
        cls.viewer2.username = cls.viewer2.email
        cls.viewer3.username = cls.viewer3.email

        # 2. Crear evento (empezó hace 1 hora)
        start_time = timezone.now() - timedelta(hours=1)
        cls.event = VirtualEvent.objects.create(
            title="Evento de prueba",
            description="Descripción",
            category="Conferencia",
            start_datetime=start_time,
            duration_minutes=90,
            privacy="public",
            created_by=cls.organizer,
        )
        cls.room = StreamingRoom.objects.create(event=cls.event, is_active=True)

        # 3. Encuesta activa
        cls.poll = Poll.objects.create(
            room=cls.room, question="¿Qué te parece el evento?", is_active=True
        )
        cls.opt_bien = PollOption.objects.create(poll=cls.poll, text="Bien")
        cls.opt_mal = PollOption.objects.create(poll=cls.poll, text="Mal")

        # 4. Mensajes
        ChatMessage.objects.create(
            room=cls.room, user=cls.viewer1, content="Hola a todos"
        )
        ChatMessage.objects.create(
            room=cls.room, user=cls.viewer2, content="¿Cuándo empieza?"
        )
        ChatMessage.objects.create(
            room=cls.room, user=cls.organizer, content="Ya empezó", is_pinned=True
        )

        # 5. Votos
        PollVote.objects.create(poll=cls.poll, user=cls.viewer1, option=cls.opt_bien)
        PollVote.objects.create(poll=cls.poll, user=cls.viewer2, option=cls.opt_bien)

        # 6. Manos
        HandRaise.objects.create(room=cls.room, user=cls.viewer3, attended=False)

        # 7. Satisfacción
        SatisfactionRating.objects.create(room=cls.room, user=cls.viewer1, rating=5)
        SatisfactionRating.objects.create(room=cls.room, user=cls.viewer2, rating=4)

        # 8. Online viewers (simulamos 3 activos + 1 inactivo)
        now = timezone.now()
        for session in ["sess_a", "sess_b", "sess_c"]:
            OnlineViewer.objects.create(
                event=cls.event,
                session_key=session,
                ip_address="127.0.0.1",
                last_heartbeat=now - timedelta(seconds=30),
            )
        OnlineViewer.objects.create(
            event=cls.event,
            session_key="sess_old",
            ip_address="127.0.0.1",
            last_heartbeat=now - timedelta(minutes=5),
        )

        # 9. Analytics
        analytics, _ = EventAnalytics.objects.get_or_create(event=cls.event)
        analytics.total_messages = ChatMessage.objects.filter(room=cls.room).count()
        analytics.total_hands = HandRaise.objects.filter(room=cls.room).count()
        analytics.total_poll_votes = PollVote.objects.filter(
            poll__room=cls.room
        ).count()
        analytics.unique_viewers = OnlineViewer.objects.filter(event=cls.event).count()
        avg_rating = SatisfactionRating.objects.filter(room=cls.room).aggregate(
            models.Avg("rating")
        )["rating__avg"]
        analytics.average_satisfaction = avg_rating or 0
        analytics.save()

    # ------------------------------------------------------------
    # PRUEBAS CORREGIDAS
    # ------------------------------------------------------------
    def test_event_metrics_returns_correct_data(self):
        url = reverse("virtualEvent:event_metrics", args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # El número de activos puede variar por el cliente de pruebas, comprobamos que sea al menos 3
        self.assertGreaterEqual(data["active_viewers"], 3)
        self.assertEqual(data["total_messages"], 3)
        self.assertEqual(data["total_hands"], 1)
        self.assertEqual(data["total_poll_votes"], 2)
        self.assertEqual(data["unique_viewers"], 4)
        self.assertEqual(data["average_satisfaction"], 4.5)
        self.assertTrue(data["elapsed_time"].startswith("01:00"))
        self.assertEqual(data["participation_percent"], 50)

    def test_send_message_as_authenticated_user(self):
        self.client.force_login(self.viewer1)
        url = reverse("ve_chat:send_message", args=[self.event.unique_link])
        response = self.client.post(
            url,
            json.dumps({"content": "Mi mensaje", "anonymous": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Mi mensaje")
        msg = ChatMessage.objects.filter(
            room=self.room, user=self.viewer1, content="Mi mensaje"
        ).first()
        self.assertIsNotNone(msg)
        self.assertFalse(msg.anonymous)

    def test_send_message_anonymous(self):
        self.client.force_login(self.viewer2)
        url = reverse("ve_chat:send_message", args=[self.event.unique_link])
        response = self.client.post(
            url,
            json.dumps({"content": "Anónimo", "anonymous": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        msg = ChatMessage.objects.filter(room=self.room, content="Anónimo").first()
        self.assertTrue(msg.anonymous)

    def test_get_messages_returns_pinned_and_recent(self):
        url = reverse("ve_chat:get_messages", args=[self.event.unique_link])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        messages = response.json()["messages"]
        pinned_msgs = [m for m in messages if m["is_pinned"]]
        self.assertGreater(len(pinned_msgs), 0)
        self.assertTrue(messages[0]["is_pinned"])

    def test_raise_hand_requires_login(self):
        client = Client()  # Cliente limpio, sin sesión
        url = reverse("ve_chat:raise_hand", args=[self.event.unique_link])
        response = client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirige a login

    def test_raise_hand_success(self):
        self.client.force_login(self.viewer1)
        url = reverse("ve_chat:raise_hand", args=[self.event.unique_link])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "hand_raised")
        hand = HandRaise.objects.filter(room=self.room, user=self.viewer1).first()
        self.assertIsNotNone(hand)
        self.assertFalse(hand.attended)

    def test_get_hands_only_organizer(self):
        self.client.force_login(self.viewer1)
        url = reverse("ve_chat:get_hands", args=[self.event.unique_link])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.client.force_login(self.organizer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        hands = response.json()["hands"]
        self.assertEqual(len(hands), 1)
        self.assertEqual(hands[0]["user_id"], self.viewer3.id)
        self.assertEqual(hands[0]["username"], self.viewer3.email)

    def test_attend_hand_only_organizer(self):
        hand = HandRaise.objects.create(
            room=self.room, user=self.viewer1, attended=False
        )
        url = reverse(
            "ve_chat:attend_hand", args=[self.event.unique_link, self.viewer1.id]
        )
        self.client.force_login(self.viewer2)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.client.force_login(self.organizer)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        hand.refresh_from_db()
        self.assertTrue(hand.attended)

    def test_create_poll_only_organizer(self):
        url = reverse("ve_chat:create_poll", args=[self.event.unique_link])
        data = {"question": "¿Nueva encuesta?", "options": ["Op1", "Op2"]}
        self.client.force_login(self.viewer1)
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.client.force_login(self.organizer)
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["question"], "¿Nueva encuesta?")
        self.poll.refresh_from_db()
        self.assertFalse(self.poll.is_active)

    def test_vote_poll_requires_login(self):
        self.client.logout()
        url = reverse("ve_chat:vote_poll", args=[self.event.unique_link, self.poll.id])
        response = self.client.post(
            url,
            json.dumps({"option_id": self.opt_bien.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_vote_poll_authenticated(self):
        self.client.force_login(self.viewer3)
        url = reverse("ve_chat:vote_poll", args=[self.event.unique_link, self.poll.id])
        response = self.client.post(
            url,
            json.dumps({"option_id": self.opt_mal.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "voted")
        vote = PollVote.objects.get(poll=self.poll, user=self.viewer3)
        self.assertEqual(vote.option.id, self.opt_mal.id)

    def test_get_poll_results(self):
        url = reverse(
            "ve_chat:poll_results", args=[self.event.unique_link, self.poll.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(results["total_votes"], 2)
        for opt in results["results"]:
            if opt["option"] == "Bien":
                self.assertEqual(opt["votes"], 2)
                self.assertEqual(opt["percentage"], 100.0)
            else:
                self.assertEqual(opt["votes"], 0)

    def test_get_active_poll(self):
        url = reverse("ve_chat:active_poll", args=[self.event.unique_link])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("poll_id"))
        self.assertEqual(data["question"], self.poll.question)

    def test_satisfaction_rating_anonymous(self):
        # Usar un cliente nuevo para asegurar sesión limpia
        client = Client()
        # Hacer una petición GET para crear la sesión
        client.get("/")
        url = reverse("ve_chat:satisfaction_rating", args=[self.event.unique_link])
        response = client.post(
            url, json.dumps({"rating": 5}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        session_key = client.session.session_key
        rating = SatisfactionRating.objects.filter(
            room=self.room, session_key=session_key
        ).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.rating, 5)

    def test_satisfaction_rating_authenticated(self):
        self.client.force_login(self.viewer3)
        url = reverse("ve_chat:satisfaction_rating", args=[self.event.unique_link])
        response = self.client.post(
            url, json.dumps({"rating": 3}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        rating = SatisfactionRating.objects.filter(
            room=self.room, user=self.viewer3
        ).first()
        self.assertEqual(rating.rating, 3)

    def test_heartbeat_updates_online_viewer(self):
        client = Client()
        url = reverse("virtualEvent:update_heartbeat", args=[self.event.id])
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        session_key = client.session.session_key
        viewer = OnlineViewer.objects.filter(
            event=self.event, session_key=session_key
        ).first()
        self.assertIsNotNone(viewer)
        self.assertGreaterEqual(
            viewer.last_heartbeat, timezone.now() - timedelta(seconds=5)
        )
