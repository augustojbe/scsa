from django.db import models

from base.models import BaseTenantModel


class ChatSession(BaseTenantModel):
    user = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='chat_sessions',
    )
    title = models.CharField(max_length=255, default='Nova conversa')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ChatMessage(BaseTenantModel):
    session = models.ForeignKey(
        'ai.ChatSession',
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=20)  # 'user' | 'assistant'
    content = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:40]}'
