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
	# Simple taxonomy for grouping decks; optional for backward compatibility
	CATEGORY_CHOICES = [
		("general", "General"),
		("definitions", "Definitions"),
		("formulas", "Formulas"),
		("concepts", "Concepts"),
		("language", "Language"),
	]
	category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="general")
	tags = models.CharField(max_length=255, blank=True, help_text="Comma separated tags e.g. Math, Science")
	VISIBILITY_CHOICES = [("public", "Public"), ("private", "Private")]
	visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")
	VERIFICATION_CHOICES = [("pending", "Pending"), ("verified", "Verified")]
	verification_status = models.CharField(max_length=10, choices=VERIFICATION_CHOICES, default="pending")
	# Moderation tracking
	verification_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="verified_decks",
		help_text="Professor/staff user who verified this deck"
	)
	verified_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when deck was verified")
	is_bookmarked = models.BooleanField(default=False)
	last_studied_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-updated_at", "-created_at"]

	def __str__(self) -> str:
		return self.title

	@property
	def cards_count(self) -> int:
		return self.cards.count()

	def mark_studied(self):
		"""Update last studied timestamp. Caller should save the instance."""
		from django.utils import timezone
		self.last_studied_at = timezone.now()

	def get_average_rating(self):
		"""Return average rating (float) or 0 if none."""
		ratings = self.ratings.all()
		if not ratings:
			return 0
		return round(sum(r.stars for r in ratings) / len(ratings), 1)

	def get_rating_count(self):
		return self.ratings.count()


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


class DeckRating(models.Model):
	"""User ratings for public decks"""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deck_ratings")
	deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="ratings")
	stars = models.PositiveSmallIntegerField(choices=[(1,"1 Star"),(2,"2 Stars"),(3,"3 Stars"),(4,"4 Stars"),(5,"5 Stars")])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ["user","deck"]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} rated {self.deck} {self.stars}"


class DeckComment(models.Model):
	"""User comments on public decks"""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deck_comments")
	deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="comments")
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} on {self.deck}: {self.text[:30]}"

