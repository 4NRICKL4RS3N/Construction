import django
from django.forms import forms, ModelForm
from AppConstruction.models import Client, Admin, Devis, Paiement, Maison, Travaux, MaisonTravaux, Finition


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['numero']

    def clean_numero(self):
        level = self.cleaned_data['numero']
        if len(level) < 10:
            raise forms.ValidationError('trop court')
        return level

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''


class AdminForm(ModelForm):
    class Meta:
        model = Admin
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''


class DevisForm(ModelForm):
    class Meta:
        model = Devis
        fields = "__all__"
        widgets = {
            'date_devis': django.forms.DateInput(attrs={'type': 'date'}),
            'date_debut_construction': django.forms.DateInput(attrs={'type': 'date'}),
            'date_fin_construction': django.forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''


class PaiementForm(ModelForm):
    class Meta:
        model = Paiement
        fields = "__all__"
        widgets = {
            'date': django.forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, client_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''
        if client_id is not None:
            self.fields['devis'].queryset = Devis.objects.filter(client=client_id)


class MaisonForm(ModelForm):
    class Meta:
        model = Maison
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''


class TravauxForm(ModelForm):
    class Meta:
        model = Travaux
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''


class MaisonTravauxForm(ModelForm):
    class Meta:
        model = MaisonTravaux
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''


class FinitionForm(ModelForm):
    class Meta:
        model = Finition
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': 'input_' + field_name
            })
            field.label_suffix = ''

