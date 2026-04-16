from django.conf import settings
from django.db import models


class Group(models.Model):
    GROUP_TYPES = [
        ('country', 'País'),
        ('musical', 'Musical'),
        ('youth', 'Jóvenes'),
        ('study', 'Estudio'),
        ('general', 'General'),
    ]

    name = models.CharField(max_length=150)
    group_type = models.CharField(max_length=10, choices=GROUP_TYPES, default='general')
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='groups/avatars/', blank=True)
    cover = models.ImageField(upload_to='groups/covers/', blank=True)
    country = models.CharField(max_length=5, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_groups',
    )
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('mod', 'Moderador'),
        ('member', 'Miembro'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='group_memberships',
    )
    role = models.CharField(max_length=6, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user} en {self.group} ({self.role})"


class GroupJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='group_join_requests',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        ordering = ['-created_at']


class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_posts')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='group_posts',
    )
    content = models.TextField()
    image = models.ImageField(upload_to='groups/posts/%Y/%m/', blank=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.author} en {self.group}: {self.content[:50]}"


class Proposal(models.Model):
    PROPOSAL_TYPES = [
        ('fasting', 'Ayuno'),
        ('prayer', 'Cadena de Oración'),
        ('activity', 'Actividad'),
        ('band', 'Banda Musical'),
    ]

    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, blank=True,
        related_name='proposals',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='proposals',
    )
    proposal_type = models.CharField(max_length=10, choices=PROPOSAL_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_proposal_type_display()}: {self.title}"


class ProposalParticipant(models.Model):
    proposal = models.ForeignKey(
        Proposal, on_delete=models.CASCADE, related_name='participants',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='joined_proposals',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('proposal', 'user')
