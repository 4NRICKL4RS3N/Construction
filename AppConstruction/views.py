import base64
import csv
import io
from datetime import timedelta, datetime

from django.db import connection, models
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
import pdfkit

from AppConstruction.forms import ClientForm, AdminForm, DevisForm, PaiementForm, MaisonForm, TravauxForm, \
    MaisonTravauxForm, FinitionForm
from AppConstruction.models import Client, Admin, Maison, Finition, PrixMaison, Devis, MaisonTravaux, DetailDevis, \
    DetailDevisView, Travaux, Paiement


class FirstRedirect(View):
    def get(self, request):
        return redirect(reverse('login_user'))


class ConnectionUserView(View):
    template_name = 'pages/login_user.html'

    def get(self, request):
        form = ClientForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        print(request.POST)
        form = ClientForm(request.POST)

        if form.is_valid():
            client, created = Client.objects.get_or_create(numero=request.POST['numero'])
            if created:
                client.save()
            request.session['client_id'] = client.id

            return JsonResponse({'success': True, 'redirect_url': reverse('construction')})

        errors = dict([(k, [str(e) for e in v]) for k, v in form.errors.items()])
        print(errors)
        return JsonResponse({'success': False, 'errors': errors})


class ClientView(View):
    template_name = 'pages/client.html'

    def get(self, request):
        client_id = request.session.get('client_id')
        if client_id:
            client = Client.objects.get(pk=client_id)
            if client is None:
                return redirect(reverse('login_user'))
            devis = Devis.objects.filter(client=client_id)
            devis_form = DevisForm()
            paiement_form = PaiementForm(client_id)
            # maisons = Maison.objects.all()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM maison_view")
                maisons = dictfetchall(cursor)
            finitions = Finition.objects.all()
            return render(request, self.template_name,
                          {'client': client, 'devis_form': devis_form, 'maisons': maisons, 'finitions': finitions,
                           'devis': devis, "paiement_form": paiement_form})

        return redirect(reverse('login_user'))

    def post(self, request):
        print(request.GET)
        if request.GET['form'] == "devis":
            post_data = request.POST.copy()
            post_data['maison'] = request.POST['maison']
            post_data['date_fin_construction'] = add_days_to_date(post_data['date_debut_construction'],
                                                                  Maison.objects.get(id=post_data['maison']).duree)
            post_data['valeur_finition'] = Finition.objects.get(pk=request.POST['finition']).pourcentage
            prix = PrixMaison.objects.get(maison_id=post_data['maison']).somme
            post_data['prix_total'] = prix + (prix * post_data['valeur_finition'] / 100)
            post_data['client'] = request.session.get('client_id')
            post_data['ref_devis'] = "D" + str(get_next_pk(Devis))
            print(post_data)
            devis_form = DevisForm(post_data)
            if devis_form.is_valid():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM detail_devis_view where maison_id = %s", [post_data['maison']])
                    travaux = cursor.fetchall()
                devis = devis_form.save()
                for trav in travaux:
                    detail_devis = DetailDevis(devis=devis, travaux=Travaux.objects.get(id=trav[1]),
                                               designation=trav[2], unite=trav[3], quantite=trav[4],
                                               prix_unitaire=trav[5], prix_total=trav[6])
                    detail_devis.save()
                return redirect(reverse('construction'))
            print(devis_form.errors)
            return redirect(reverse('construction'))

        if request.GET['form'] == "paiement":
            paiement_form = PaiementForm(data=request.POST)
            if paiement_form.is_valid():
                paiement_form.save()
                return redirect(reverse('construction'))

            errors = dict([(k, [str(e) for e in v]) for k, v in paiement_form.errors.items()])
            print("not valid")
            print(errors)
            return JsonResponse({'success': False, 'errors': errors})


class ConnectionAdminView(View):
    template_name = 'pages/login_admin.html'

    def get(self, request):
        form = AdminForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        admin = Admin.authenticate(email, password)
        if admin == 1:
            return JsonResponse({'success': False, 'errors': "email introuvable"})
        elif admin == 2:
            return JsonResponse({'success': False, 'errors': "mot de passe incorecte"})

        request.session['admin_id'] = admin.id

        return JsonResponse({'success': True, 'redirect_url': reverse('devis-admin')})


def dictfetchall(cursor):
    """
    Returns all rows from a cursor as a dict
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class AdminView(View):
    template_name = 'pages/admin.html'

    def get(self, request):
        admin_id = request.session.get('admin_id')
        if admin_id:
            admin = Admin.objects.get(pk=admin_id)
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM devis_paiement")
                devis = dictfetchall(cursor)
            for row in devis:
                row["pourcentage"] = 100 * row['paiement_total'] / row['prix_total']
            return render(request, self.template_name, {'admin': admin, 'devis': devis})
        return redirect(reverse('login_admin'))


class DevisDetailView(View):
    template_name = 'pages/devis.html'

    def get(self, request, pk):
        admin_id = request.session.get('admin_id')
        if admin_id:
            devis_detail = DetailDevis.objects.filter(devis_id=pk)
            return render(request, self.template_name, {'devis_detail': devis_detail, 'devis_id': pk})
        return redirect(reverse('login_admin'))


class DashboardView(View):
    template_name = 'pages/dashboard.html'

    def get(self, request):
        admin_id = request.session.get('admin_id')
        if admin_id:
            montant_total_devis = 0
            annee = 2024
            if request.GET.get("annee"):
                annee = request.GET['annee']
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM montant_total_devis")
                montant_total_devis = cursor.fetchone()[0]

                cursor.execute("select * from montant_total_paye")
                montant_total_paye = cursor.fetchone()[0]

                cursor.execute(f"""
                    SELECT to_char(month_series.month, 'YYYY-MM') AS month,COALESCE(SUM("AppConstruction_devis".prix_total), 0) AS total_price
                    FROM ( SELECT generate_series('{annee}-01-01'::date, '{annee}-12-31'::date, '1 month') AS month ) AS month_series
                    LEFT JOIN "AppConstruction_devis" ON to_char("AppConstruction_devis".date_devis, 'YYYY-MM') = to_char(month_series.month, 'YYYY-MM')
                    GROUP BY to_char(month_series.month, 'YYYY-MM')
                    ORDER BY month;
                """)
                montant_devis_mois = dictfetchall(cursor)

                cursor.execute("""
                    SELECT to_char(year_series.year, 'YYYY') AS year,
                           COALESCE(SUM("AppConstruction_devis".prix_total), 0) AS total_price
                    FROM (
                        SELECT generate_series('2020-01-01'::date, '2024-12-31'::date, '1 year') AS year
                    ) AS year_series
                    LEFT JOIN "AppConstruction_devis" ON EXTRACT(YEAR FROM "AppConstruction_devis".date_devis) = EXTRACT(YEAR FROM year_series.year)
                    GROUP BY to_char(year_series.year, 'YYYY')
                    ORDER BY year;
                """)
                montant_devis_year = dictfetchall(cursor)
            return render(request, self.template_name,
                          {'montant_total_devis': montant_total_devis, 'montant_devis_mois': montant_devis_mois,
                           'montant_devis_year': montant_devis_year, 'montant_total_paye': montant_total_paye})
        return redirect(reverse('login_admin'))


class ImportData(View):
    def post(self, request):
        if request.FILES.get('maison_travaux'):
            # initialisation donner
            header, rows = init_csv_data(request, 'maison_travaux')

            error_row = []
            success_row_number = 0
            fail_row_number = 0

            # mampiditra maison sy travaux
            for row in rows:
                print(row)
                maison = Maison.objects.filter(designation=row[0])
                travaux = Travaux.objects.filter(code_travaux=row[3])
                if len(maison) == 0:
                    dict_maison = {}
                    dict_maison["designation"] = row[0]
                    dict_maison["description"] = row[1]
                    dict_maison["surface"] = float(row[2].replace(',', '.'))
                    dict_maison["duree"] = float(row[8].replace(',', '.'))
                    dict_maison["prix"] = 0.0
                    maison_form = MaisonForm(dict_maison)
                    if maison_form.is_valid():
                        maison_form.save()
                    else:
                        print(maison_form.errors)
                if len(travaux) == 0:
                    dict_travaux = {}
                    dict_travaux["designation"] = row[4]
                    dict_travaux["unite"] = row[5]
                    dict_travaux["prix_unitaire"] = float(row[6].replace(',', '.'))
                    dict_travaux["code_travaux"] = row[3]
                    travaux_form = TravauxForm(dict_travaux)
                    if travaux_form.is_valid():
                        travaux_form.save()
                    else:
                        print(travaux_form.errors)

            print("avant boucle")
            for row in rows:
                print("mi boucle")
                maison = Maison.objects.filter(designation=row[0])
                travaux = Travaux.objects.filter(code_travaux=row[3])
                if len(maison) > 0 and len(travaux) > 0:
                    print("misy le maison sy travaux")
                    maison = maison[0]
                    travaux = travaux[0]
                    maison_travaux = MaisonTravaux.objects.filter(maison=maison, travaux=travaux)
                    if len(maison_travaux) == 0:
                        print("mbola tsy misy le maison_travaux")
                        maison_travaux_dict = {}
                        maison_travaux_dict["travaux"] = travaux
                        maison_travaux_dict["maison"] = maison
                        maison_travaux_dict["quantite"] = float(row[7].replace(',', '.'))
                        maison_travaux_form = MaisonTravauxForm(maison_travaux_dict)
                        if maison_travaux_form.is_valid():
                            print("tafiditra le maison_travaux")
                            maison_travaux_form.save()
                        else:
                            print("tsy tafiditra le maison_travaux")
                            print(maison_travaux_form.errors)

        if request.FILES.get('devis'):
            # initialisation donner
            header, rows = init_csv_data(request, 'devis')

            # mampiditra finition sy client
            for row in rows:
                finition = Finition.objects.filter(designation=row[3])
                client = Client.objects.filter(numero=row[0])
                if len(finition) == 0:
                    dict_finition = {}
                    dict_finition["designation"] = row[3]
                    dict_finition["pourcentage"] = float(row[4].rstrip('%').replace(',', '.'))
                    finition_form = FinitionForm(dict_finition)
                    if finition_form.is_valid():
                        finition_form.save()
                    else:
                        print(finition_form.errors)
                if len(client) == 0:
                    dict_client = {}
                    dict_client["numero"] = row[0]
                    client_form = ClientForm(dict_client)
                    if client_form.is_valid():
                        client_form.save()
                    else:
                        print(client_form.errors)

            # mampiditra devis
            for row in rows:
                print("mi boucle")
                finition = Finition.objects.filter(designation=row[3])
                client = Client.objects.filter(numero=row[0])
                maison = Maison.objects.filter(designation=row[2])
                if len(finition) > 0 and len(client) > 0 and len(maison) > 0:
                    print("misy le finition sy client")
                    finition = finition[0]
                    client = client[0]
                    maison = maison[0]
                    devis = Devis.objects.filter(ref_devis=row[1])
                    if len(devis) == 0:
                        print("mbola tsy misy le devis")
                        devis_dict = {}
                        devis_dict["client"] = client
                        devis_dict["maison"] = maison
                        devis_dict["finition"] = finition
                        devis_dict["valeur_finition"] = float(row[4].rstrip('%').replace(',', '.'))
                        prix = PrixMaison.objects.get(maison_id=maison.id).somme
                        devis_dict['prix_total'] = prix + (prix * devis_dict['valeur_finition'] / 100)
                        devis_dict['date_devis'] = format_date(row[5])
                        devis_dict['date_debut_construction'] = format_date(row[6])
                        devis_dict['date_fin_construction'] = add_days_to_date(devis_dict['date_debut_construction'],
                                                                               maison.duree)
                        devis_dict['ref_devis'] = row[1]
                        devis_dict['lieu'] = row[7]
                        devis_form = DevisForm(devis_dict)
                        if devis_form.is_valid():
                            print("tafiditra le devis")
                            with connection.cursor() as cursor:
                                cursor.execute("SELECT * FROM detail_devis_view where maison_id = %s",
                                               [devis_dict['maison'].id])
                                travaux = cursor.fetchall()
                            devis = devis_form.save()
                            for trav in travaux:
                                detail_devis = DetailDevis(devis=devis, travaux=Travaux.objects.get(id=trav[1]),
                                                           designation=trav[2], unite=trav[3], quantite=trav[4],
                                                           prix_unitaire=trav[5], prix_total=trav[6])
                                detail_devis.save()
                        else:
                            print("tsy tafiditra le devis")
                            print(devis_form.errors)

        return redirect(reverse('dashboard'))


class ImportPaiement(View):
    def post(self, request):
        if request.FILES.get('paiement'):
            # initialisation donner
            header, rows = init_csv_data(request, 'paiement')

            error_row = []
            success_row_number = 0
            fail_row_number = 0

            print("mi boucle import paiement")
            form_paiement = PaiementForm()
            for row in rows:
                devis = Devis.objects.filter(ref_devis=row[0])
                if len(devis) > 0:
                    print("misy le devis anle paiement")
                    devis = devis[0]
                    dict_paiement = {}
                    dict_paiement['devis'] = devis.id
                    dict_paiement['date'] = format_date(row[2])
                    dict_paiement['montant'] = float(row[3].replace(',', '.'))
                    dict_paiement['ref_paiement'] = row[1]
                    form_paiement = PaiementForm(data=dict_paiement)
                    if form_paiement.is_valid():
                        print("valide le paiement")
                        form_paiement.save()
                    else:
                        print(form_paiement.errors)

            return redirect(reverse('dashboard'))


class TravauxView(View):
    template_name = 'pages/travaux.html'

    def get(self, request):
        admin_id = request.session.get('admin_id')
        if admin_id:
            travaux = Travaux.objects.all()
            return render(request, self.template_name, {'travaux': travaux})
        return redirect(reverse('login_admin'))


class TravauxUpdateView(View):
    template_name = 'pages/travaux_update.html'

    def get(self, request, pk):
        admin_id = request.session.get('admin_id')
        if admin_id:
            travaux = Travaux.objects.get(id=pk)
            form_travaux = TravauxForm(instance=travaux)
            return render(request, self.template_name, {'form_travaux': form_travaux, "travaux": travaux})
        return redirect(reverse('login_admin'))

    def post(self, request, pk):
        print(request.POST)
        instance = Travaux.objects.get(id=pk)
        form_travaux = TravauxForm(request.POST, instance=instance)
        if form_travaux.is_valid():
            form_travaux.save()
        return redirect(reverse('travaux-admin'))


class FinitionView(View):
    template_name = 'pages/finition.html'

    def get(self, request):
        admin_id = request.session.get('admin_id')
        if admin_id:
            finition = Finition.objects.all()
            return render(request, self.template_name, {'finition': finition})
        return redirect(reverse('login_admin'))


class FinitionUpdateView(View):
    template_name = 'pages/finition_update.html'

    def get(self, request, pk):
        admin_id = request.session.get('admin_id')
        if admin_id:
            finition = Finition.objects.get(id=pk)
            form_finition = FinitionForm(instance=finition)
            return render(request, self.template_name, {'form_finition': form_finition, "finition": finition})
        return redirect(reverse('login_admin'))

    def post(self, request, pk):
        print(request.POST)
        instance = Finition.objects.get(id=pk)
        form_finition = FinitionForm(request.POST, instance=instance)
        if form_finition.is_valid():
            form_finition.save()
        return redirect(reverse('finition-admin'))


def generate_pdf(devis, objects_list, paiement, paiement_total):
    context = {
        'data': objects_list,
        'devis': devis,
        'paiement': paiement,
        'paiement_total': paiement_total,
    }
    html_content = render_to_string('pages/table-data-pdf.html', context)
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        # 'disable-local-file-access': None,
        # 'enable-local-file-access': "",
    }
    pdf_file = pdfkit.from_string(html_content, False, options=options)
    buffer = io.BytesIO(pdf_file)
    return buffer


class ExportDevisPDF(View):

    def get(self, request):
        if request.GET.get('id_devis'):
            devis = Devis.objects.get(id=request.GET.get('id_devis'))
            objects_list = DetailDevis.objects.filter(devis=devis)
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT * FROM "AppConstruction_paiement" where devis_id = {devis.id}')
                paiement = dictfetchall(cursor)
            print(paiement)
            paiement_total = 0
            for paie in paiement:
                paiement_total += paie['montant']
            buffer = generate_pdf(devis, objects_list, paiement, paiement_total)
            pdf_content = buffer.getvalue()
            encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')
            embedded_pdf = f'<embed src="data:application/pdf;base64,{encoded_pdf}" type="application/pdf" width="100%" height="600px" />'
            return HttpResponse(embedded_pdf)


def get_next_pk(model):
    max_primary_key = model.objects.aggregate(max_pk=models.Max('pk'))['max_pk']
    next_primary_key = max_primary_key + 1 if max_primary_key is not None else 1
    return next_primary_key


def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    return formatted_date


def add_days_to_date(date_str, days):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    delta = timedelta(days=days)
    new_date = date_obj + delta
    new_date_str = new_date.strftime("%Y-%m-%d")
    return new_date_str


def init_csv_data(request, file_name):
    csv_file = request.FILES[file_name]
    csv_data = csv_file.read().decode('utf-8').splitlines()
    if csv_data and csv_data[0].startswith('\ufeff'):
        csv_data[0] = csv_data[0][1:]
    csv_reader = csv.reader(csv_data, delimiter=',')
    header = next(csv_reader)
    rows = list(csv_reader)
    return header, rows


class Logout(View):
    def get(self, request):
        request.session.flush()
        return redirect(reverse('login_admin'))


class ResetDatabase(View):
    tables_to_reset = [Travaux, Client, Maison, Finition, Devis, MaisonTravaux, DetailDevis, Devis, Paiement]

    def get(self, request):
        for table in self.tables_to_reset:
            table.objects.all().delete()
        return redirect(reverse('dashboard'))
