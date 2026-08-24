"""Seed the AIProvider table from legacy .env values (idempotent).

The study coach's model is managed in the admin UI now. This command runs at
deploy time: if no provider exists yet and the old MINIMAX_* keys are present
in .env, it imports them as the active provider so the coach keeps working
across the upgrade. Skips silently otherwise.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from portal.envfile import env_value
from portal.models import AIProvider


class Command(BaseCommand):
    help = "Import .env MiniMax settings as the active AI provider (once)."

    def handle(self, *args, **options):
        if AIProvider.objects.exists():
            self.stdout.write("AI providers already configured — nothing to do.")
            return
        api_key = env_value("MINIMAX_API_KEY")
        if not api_key:
            self.stdout.write("No providers and no .env MINIMAX_API_KEY — skip.")
            return
        provider = AIProvider.objects.create(
            name="MiniMax-M3",
            api_style="openai",
            base_url=env_value("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1"),
            model_id=env_value("MINIMAX_MODEL", "MiniMax-M3"),
            api_key=api_key,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f"imported active provider: {provider}"))
