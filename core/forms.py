from django import forms
from .models import Exercice, Matiere, Lecon, Classe

class ExerciceAdminForm(forms.ModelForm):
    class Meta:
        model = Exercice
        fields = '__all__'  # Tous les champs du modèle

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrage initial si l'exercice existe déjà
        if self.instance.pk:
            # Filtre les matières par la classe sélectionnée
            self.fields['matiere'].queryset = Matiere.objects.filter(
                classe=self.instance.classe
            )
            # Filtre les leçons par la matière sélectionnée
            self.fields['lecons'].queryset = Lecon.objects.filter(
                matiere=self.instance.matiere
            )
        else:
            # Si nouvel exercice, on commence avec des querysets vides
            self.fields['matiere'].queryset = Matiere.objects.none()
            self.fields['lecons'].queryset = Lecon.objects.none()