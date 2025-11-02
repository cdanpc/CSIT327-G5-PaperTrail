from django.conf import settings
from django.db import models


class Deck(models.Model):
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="decks",
	)
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-updated_at", "-created_at"]

	def __str__(self) -> str:
		return self.title

	@property
	def cards_count(self) -> int:
		return self.cards.count()


class Card(models.Model):
	deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
	front_text = models.TextField()
	back_text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["id"]

	def __str__(self) -> str:
		return f"Card #{self.pk} in {self.deck.title}"

