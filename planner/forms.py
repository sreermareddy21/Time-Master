# forms.py
from django import forms
from planner.models import Task, Category
from django.utils import timezone

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'category', 'priority', 'status', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input min-h-[150px] resize-y',
                'rows': 3,
                'placeholder': 'Enter task description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-input form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input form-select'
            }),
            'deadline': forms.TextInput(attrs={
                'class': 'form-input datetimepicker',
                'placeholder': 'Select deadline'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Extract the request object from kwargs
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Add empty options
        self.fields['category'].empty_label = "Select category"
        self.fields['priority'].empty_label = "Select priority"
        self.fields['status'].empty_label = "Select status"
        
        # Set initial status
        self.initial['status'] = 'pending'

        # Filter the category queryset by the logged-in user
        if request:
            self.fields['category'].queryset = Category.objects.filter(user=request.user)



class CategoryForm(forms.ModelForm):
    ICON_CHOICES = [
        ('fas fa-briefcase', 'Work'),
        ('fas fa-home', 'Personal'),
        ('fas fa-shopping-cart', 'Shopping'),
        ('fas fa-heartbeat', 'Health'),
        ('fas fa-graduation-cap', 'Education'),
        ('fas fa-plane', 'Travel'),
    ]

    COLOR_CHOICES = [
        ('#EF4444', 'red'),    # red-500
        ('#3B82F6', 'blue'),   # blue-500
        ('#22C55E', 'green'),  # green-500
        ('#EAB308', 'yellow'), # yellow-500
        ('#A855F7', 'purple'), # purple-500
        ('#EC4899', 'pink'),   # pink-500
    ]

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter category name'
        })
    )
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        widget=forms.RadioSelect()  # Remove the attrs here
    )
    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    class Meta:
        model = Category
        fields = ['name', 'color']
