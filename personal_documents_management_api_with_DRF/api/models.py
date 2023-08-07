from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError

# Create your models here.

#=================================Custom user for Role base User
class CustomUser(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission,blank=True, related_name='custom_users', help_text='Specific permissions for this user.', verbose_name='user permissions')

    def __str__(self):
        return self.username
    


#================================ Document Model
def validate_file_size(value):
    max_size = 20 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError('Allowed Limitation of File size 20 MB')

def validate_file_format(value):
    allowed_formats = ['pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx', 'jpeg','jpg', 'png', 'mp4'] # can be added more 
    ext = value.name.split('.')[-1]
    if ext.lower() not in allowed_formats:
        raise ValidationError('Unsupported file format.')


class Documents(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creator_document')
    created_at = models.DateTimeField(auto_now_add=True)
    share_with = models.ManyToManyField(CustomUser, related_name='shared_documents')
    format = models.CharField(max_length=10, blank=True)
    file = models.FileField(upload_to='documents/', validators=[validate_file_size, validate_file_format])

    class Meta:
        verbose_name = "Documents Model"
        verbose_name_plural = "Documents Model"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DocAcess(models.Model):
    document = models.ForeignKey(Documents, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    editable = models.BooleanField(default=False)