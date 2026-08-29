from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Partner(models.Model):
    CATEGORY_CHOICES = [
        ('government', 'Government'),
        ('institutional', 'Institutional'),
        ('corporate', 'Corporate'),
        ('academic', 'Academic'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='institutional')
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Story(models.Model):
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=200, blank=True)
    author_role = models.CharField(max_length=200, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='stories/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('yvf', 'Youth Volunteers Forum'),
        ('leadership_training', 'Leadership Training'),
        ('community_outreach', 'Community Outreach'),
        ('digital_literacy', 'Digital Literacy'),
        ('strategy', 'Strategy'),
        ('networking', 'Networking'),
    ]
    title = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='yvf')
    image = models.ImageField(upload_to='gallery/')
    caption = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or self.caption[:60]


class FAQ(models.Model):
    topic = models.CharField(max_length=100, blank=True)
    keywords = models.CharField(max_length=500, blank=True, help_text='Comma-separated trigger words')
    question_example = models.TextField(blank=True)
    question = models.TextField(blank=True)
    answer = models.TextField()
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']

    @property
    def keyword_list(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()]

    def __str__(self):
        return (self.question_example or self.question or '')[ :80]


class OrgStat(models.Model):
    label = models.CharField(max_length=200)
    value = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}"


class SiteContent(models.Model):
    """Single JSON store for all admin CMS data (hero, mission, etc.) that has no dedicated model.
    Stored under key 'zcm_admin_data_v1' to match localStorage key."""
    key = models.CharField(max_length=100, unique=True, default='zcm_admin_data_v1')
    data = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='site_content_updates'
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"SiteContent {self.key} ({self.updated_at:%Y-%m-%d})"
