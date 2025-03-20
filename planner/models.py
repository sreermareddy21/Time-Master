from django.db import models


class Category(models.Model):
    user = models.ForeignKey('users.Account', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, default='fas fa-folder')  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        

class Task(models.Model):
    STATUSES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
    )
    
    PRIORITIES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    user = models.ForeignKey('users.Account', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='medium')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']