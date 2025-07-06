from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import FileExtensionValidator

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.core.validators import FileExtensionValidator


class Utilisateur(AbstractUser):
    # 1. Résolution des conflits de groupes/permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name='groupes',
        blank=True,
        related_name="utilisateurs",
        related_query_name="utilisateur",
        help_text='Groupes auxquels appartient cet utilisateur.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions utilisateur',
        blank=True,
        related_name="utilisateurs",
        related_query_name="utilisateur",
        help_text='Permissions spécifiques pour cet utilisateur.',
    )

    # 2. Vos champs personnalisés
    TYPE_COMPTE = (
        ('ELEVE', 'Élève'),
        ('ENSEIGNANT', 'Enseignant'),
    )
    telephone = models.CharField(max_length=20, blank=True)
    type_compte = models.CharField(max_length=12, choices=TYPE_COMPTE)
    statut_abonnement = models.BooleanField(default=False)
    gmail = models.EmailField(blank=True) 
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

class Investisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    pourcentage = models.DecimalField(max_digits=5, decimal_places=2)
    date_investissement = models.DateField()
    date_cloture = models.DateField(null=True, blank=True)
    mot_de_passe = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.mot_de_passe = make_password(raw_password)
        self.save()

    def __str__(self):
        return f"{self.nom} ({self.pourcentage}%)"

class Pays(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    #code = models.CharField(max_length=3)

    def __str__(self):
         return self.nom

class SousSystemeEnseignement(models.Model):
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)

    class Meta:
        unique_together = ('pays', 'nom')  # Modification ici
        verbose_name = "Sous-système éducatif"
        verbose_name_plural = "Sous-systèmes éducatifs"

    def __str__(self):
        return f"{self.pays} - {self.nom}"  # Modification ici

class Classe(models.Model):
    sous_systeme = models.ForeignKey(SousSystemeEnseignement, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)

    class Meta:
        unique_together = ('sous_systeme', 'nom')
        ordering = ['sous_systeme', 'nom']

    def __str__(self):
        return f"{self.sous_systeme} - {self.nom}"

class Matiere(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)  # Changé de ManyToMany à ForeignKey
    #classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        unique_together = ('classe', 'nom')  # Ajout pour garantir l'unicité du nom par classe

    def __str__(self):
        return f"{self.nom} ({self.code}) - {self.classe}"  # Ajout de la classe dans l'affichage

class TypeExercice(models.Model):
    matiere = models.ForeignKey(
        'Matiere', 
        on_delete=models.CASCADE, 
        verbose_name="Matière"
    )
    nom = models.CharField(max_length=50, verbose_name="Nom du type")

    class Meta:
        unique_together = ('matiere', 'nom')
        verbose_name = "Type d'exercice"
        verbose_name_plural = "Types d'exercices"

    def __str__(self):
        return f"{self.matiere} - {self.nom}"

    @property
    def classe(self):
        """Accès à la classe via la matière (propriété calculée)"""
        return self.matiere.classe

    def clean(self):
        """Validation de la cohérence matière/classe"""
        if hasattr(self, 'matiere') and hasattr(self.matiere, 'classe'):
            if not self.matiere.classe:
                raise ValidationError("La matière doit être associée à une classe")

class Lecon(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    # Supprimez la ForeignKey 'classe' car elle est déjà accessible via 'matiere.classe'
    titre = models.CharField(max_length=200)
    contenu_latex = models.TextField()
    fichier_pdf = models.FileField(
        upload_to='lecons/pdf/',
        validators=[FileExtensionValidator(['pdf'])]  # Validation des fichiers
    )

    class Meta:
        unique_together = ('matiere', 'titre')  # Simplifié
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"

    def __str__(self):
        return f"{self.matiere} - {self.titre}"

    # Propriété pour accéder à la classe via la matière (optionnel)
    @property
    def classe(self):
        return self.matiere.classe

class Exercice(models.Model):
    DIFFICULTE = (
        ('FACILE', 'Facile'),
        ('MOYEN', 'Moyen'),
        ('DIFFICILE', 'Difficile'),
    )
    
    matiere = models.ForeignKey(
        'Matiere',
        on_delete=models.CASCADE,
        verbose_name="Matière"
    )
    type_exercice = models.ForeignKey(
        TypeExercice,
        on_delete=models.CASCADE,
        verbose_name="Type d'exercice"
    )
    lecons = models.ManyToManyField(
        'Lecon',
        blank=True,
        verbose_name="Leçons concernées"
    )
    difficulte = models.CharField(
        max_length=10,
        choices=DIFFICULTE
    )
    enonce_latex = models.TextField()
    corrige_latex = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['matiere', 'type_exercice']),
        ]

    def __str__(self):
        return f"{self.matiere} - {self.type_exercice} ({self.get_difficulte_display()})"

    @property
    def classe(self):
        """Accès à la classe via la matière (propriété calculée)"""
        return self.matiere.classe

    def clean(self):
        """Validation de la cohérence matière/type_exercice"""
        if (hasattr(self, 'matiere') and 
            hasattr(self, 'type_exercice') and 
            self.matiere != self.type_exercice.matiere):
            raise ValidationError(
                "Le type d'exercice doit correspondre à la matière sélectionnée"
            )