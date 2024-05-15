from django.db import models


class Client(models.Model):
    numero = models.CharField(max_length=13)
    fields_to_show = ['numero']


class Admin(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=200)
    fields_to_show = ['email', 'password']

    def check_password(self, password):
        if password == self.password:
            return True
        return False

    @staticmethod
    def authenticate(email, password):
        admin = Admin.objects.filter(email=email)
        if len(admin) > 0:
            admin = admin[0]
            if admin.check_password(password):
                return admin
            return 2
        return 1


class Finition(models.Model):
    designation = models.CharField(max_length=200, null=True)
    pourcentage = models.FloatField()

    def __str__(self):
        return self.designation


class Travaux(models.Model):
    designation = models.CharField(max_length=200, null=True)
    unite = models.CharField(max_length=5, null=True)
    prix_unitaire = models.FloatField(null=True)
    code_travaux = models.CharField(max_length=5, null=True)
    fields_to_show = ['designation', 'unite', 'prix_unitaire']


class Maison(models.Model):
    designation = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)
    duree = models.FloatField(null=True)
    prix = models.FloatField(null=True)
    surface = models.FloatField(null=True)
    fields_to_show = ['designation', 'description', 'duree', 'prix']

    def __str__(self):
        return self.designation


class MaisonTravaux(models.Model):
    travaux = models.ForeignKey(Travaux, on_delete=models.SET_NULL, null=True)
    maison = models.ForeignKey(Maison, on_delete=models.SET_NULL, null=True)
    quantite = models.FloatField(null=True)
    fields_to_show = ['travaux', 'maison', 'quantite']


class Devis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    maison = models.ForeignKey(Maison, on_delete=models.SET_NULL, null=True)
    finition = models.ForeignKey(Finition, on_delete=models.SET_NULL, null=True)
    valeur_finition = models.FloatField(null=True)
    prix_total = models.FloatField(null=True)
    date_devis = models.DateField(null=True)
    date_debut_construction = models.DateField(null=True)
    date_fin_construction = models.DateField(null=True)
    ref_devis = models.CharField(max_length=10, null=True)
    lieu = models.CharField(max_length=50, null=True)
    fields_to_show = ['maison', 'finition', 'prix_total', 'date_devis']


class DetailDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.SET_NULL, null=True)
    travaux = models.ForeignKey(Travaux, on_delete=models.SET_NULL, null=True)
    designation = models.CharField(max_length=200, null=True)
    unite = models.CharField(max_length=5, null=True)
    prix_unitaire = models.FloatField(null=True)
    prix_total = models.FloatField(null=True)
    quantite = models.FloatField(null=True)


class DetailDevisView(models.Model):
    maison_id = models.BigIntegerField(blank=True, null=True)
    travaux_id = models.BigIntegerField(blank=True, null=True)
    designation = models.CharField(max_length=200, blank=True, null=True)
    unite = models.CharField(max_length=5, blank=True, null=True)
    quantite = models.FloatField(blank=True, null=True)
    prix_unitaire = models.FloatField(blank=True, null=True)
    prix_total = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detail_devis_view'


class PrixMaison(models.Model):
    maison_id = models.AutoField(primary_key=True, db_column='maison_id')
    somme = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prix_maison'


class Paiement(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    montant = models.FloatField()
    ref_paiement = models.CharField(max_length=20, null=True)
