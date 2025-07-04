from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class Utilisateur(AbstractUser):
    # 1. Résolution des conflits de groupes/permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groupes'),
        blank=True,
        related_name="utilisateurs",  # Nom unique
        related_query_name="utilisateur",
        help_text=_('Groupes auxquels appartient cet utilisateur.'),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions utilisateur'),
        blank=True,
        related_name="utilisateurs",  # Nom unique 
        related_query_name="utilisateur",
        help_text=_('Permissions spécifiques pour cet utilisateur.'),
    )

    # 2. Vos champs personnalisés (inchangés)
    TYPE_COMPTE = (
        ('ELEVE', 'Élève'),
        ('ENSEIGNANT', 'Enseignant'),
    )
    telephone = models.CharField(max_length=20, blank=True)
    type_compte = models.CharField(max_length=12, choices=TYPE_COMPTE)
    statut_abonnement = models.BooleanField(default=False)
    
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
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.nom

class SousSystemeEnseignement(models.Model):
    TYPE_SYSTEME = (
        ('PRIMAIRE_FR', 'Primaire francophone'),
        ('PRIMAIRE_EN', 'Primaire anglophone'),
        ('SECONDAIRE_FR', 'Secondaire francophone'),
        ('SECONDAIRE_EN', 'Secondaire anglophone'),
        ('SUPERIEUR', 'Enseignement supérieur'),
    )
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)
    type_systeme = models.CharField(max_length=13, choices=TYPE_SYSTEME)
    nom = models.CharField(max_length=50)

    class Meta:
        unique_together = ('pays', 'type_systeme', 'nom')
        verbose_name = "Sous-système éducatif"
        verbose_name_plural = "Sous-systèmes éducatifs"

    def __str__(self):
        return f"{self.pays} - {self.get_type_systeme_display()}"

class Classe(models.Model):
    sous_systeme = models.ForeignKey(SousSystemeEnseignement, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)

    class Meta:
        unique_together = ('sous_systeme', 'nom')
        ordering = ['sous_systeme', 'nom']

    def __str__(self):
        return f"{self.sous_systeme} - {self.nom}"

class Matiere(models.Model):
    classes = models.ManyToManyField(Classe)
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nom} ({self.code})"

class TypeExercice(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('matiere', 'nom')
        verbose_name = "Type d'exercice"
        verbose_name_plural = "Types d'exercices"

    def __str__(self):
        return f"{self.matiere} - {self.nom}"

class Lecon(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    contenu_latex = models.TextField()
    fichier_pdf = models.FileField(upload_to='lecons/pdf/')

    class Meta:
        unique_together = ('matiere', 'classe', 'titre')
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"

    def __str__(self):
        return f"{self.matiere} - {self.titre}"

class Exercice(models.Model):
    DIFFICULTE = (
        ('FACILE', 'Facile'),
        ('MOYEN', 'Moyen'),
        ('DIFFICILE', 'Difficile'),
    )
    lecons = models.ManyToManyField(Lecon)  # Relation many-to-many
    type_exercice = models.ForeignKey(TypeExercice, on_delete=models.CASCADE)
    difficulte = models.CharField(max_length=10, choices=DIFFICULTE)
    enonce_latex = models.TextField()
    corrige_latex = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"

    def __str__(self):
        return f"{self.type_exercice} ({self.get_difficulte_display()})"