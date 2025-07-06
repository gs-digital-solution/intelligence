from django import forms
from django.core.exceptions import ValidationError
from .models import Exercice, TypeExercice, Matiere

class ExerciceAdminForm(forms.ModelForm):  # Notez le nom corrigé (ExerciceAdminForm avec un 'c')
    class Meta:
        model = Exercice
        fields = '__all__'
        widgets = {
            'enonce_latex': forms.Textarea(attrs={'rows': 5}),
            'corrige_latex': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrage dynamique des matières si classe est définie
        if 'matiere' in self.fields and 'classe' in self.data:
            try:
                classe_id = int(self.data.get('classe'))
                self.fields['matiere'].queryset = Matiere.objects.filter(
                    classe_id=classe_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.matiere:
            self.fields['matiere'].queryset = Matiere.objects.filter(
                classe=self.instance.matiere.classe
            )
        
        # Filtrage des types d'exercice
        if 'type_exercice' in self.fields:
            if self.instance and self.instance.pk and self.instance.matiere:
                self.fields['type_exercice'].queryset = TypeExercice.objects.filter(
                    matiere=self.instance.matiere
                )
            else:
                self.fields['type_exercice'].queryset = TypeExercice.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        matiere = cleaned_data.get('matiere')
        type_exercice = cleaned_data.get('type_exercice')
        
        if matiere and type_exercice and type_exercice.matiere != matiere:
            raise ValidationError(
                "Le type d'exercice doit correspondre à la matière sélectionnée"
            )
        
        return cleaned_data