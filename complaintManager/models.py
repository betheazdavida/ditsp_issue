from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm, BooleanField, TextInput, PasswordInput, Select, RadioSelect, Textarea, CheckboxSelectMultiple, DateTimeInput, CheckboxInput, NumberInput
from django.utils import timezone
from django.core.validators import validate_email, validate_integer
import re
import os

def get_upload_path_images(instance, filename):
    upload_dir = os.path.join('media', "%s" % instance.complaint.title)
    print(upload_dir)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return os.path.join(upload_dir, filename)


class Location(models.Model):
    name = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return '{}: {},{}'.format(self.name, self.lat, self.lon)

class Origin(models.Model):
    MASTER_ORIGIN = (
        ('Pimpinan', 'Pimpinan'),
        ('Unit', 'Unit ITB'),
        ('Intern', 'Intern Direktorat Sarana dan Prasarana'),
        ('Civitas', 'Civitas Akademik'),
        ('Eksternal', 'Eksternal ITB (Masyarakat, Tamu, dan Umum)')
    )
    name = models.CharField(max_length=20, choices=MASTER_ORIGIN)
    def is_selected(self, name):
        return 'selected' if name == self.name else ''
    def __str__(self):
        return dict(self.MASTER_ORIGIN)[self.name]
    

class InformerOrigin(models.Model):
    MASTER_ORIGIN = (
        ('Pimpinan', 'Pimpinan'),
        ('Unit', 'Unit ITB'),
        ('Intern', 'Intern Direktorat Sarana dan Prasarana'),
        ('Civitas', 'Civitas Akademik'),
        ('Eksternal', 'Eksternal ITB (Masyarakat, Tamu, dan Umum)')
    )
    master_origin = models.CharField(max_length=20, choices=MASTER_ORIGIN)
    specific_origin = models.CharField(max_length=20)

    def is_selected(self, master_origin):
        return 'selected' if master_origin == self.master_origin else ''

    def __str__(self):
        return '{} - {}'.format(self.master_origin, self.specific_origin)


class Informer(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    origin = models.ForeignKey(InformerOrigin, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return '{} from {}'.format(self.name, self.origin)


class Division(models.Model):
    DIVISIONS = (
        ('PU', 'Perawatan Utilitas'),
        ('PG', 'Perawatan Gedung'),
        ('OG', 'Operasional dan Kebersihan Gedung'),
        ('KS', 'Kebersihan dan Pengelolaan Sampah'),
        ('IA', 'Inventarisasi Aset'),
        ('PDA', 'Pendayagunaan Aset'),
        ('PHA', 'Penghapusan Aset'),
        ('PD', 'Penerimaan dan Distribusi'),
        ('S', 'Sekretariat'),
    )
    name = models.CharField(max_length=10, choices=DIVISIONS)

    def __str__(self):
        return dict(self.DIVISIONS)[self.name]


class Role(models.Model):
    ROLES = (
        ('PU', 'Perawatan Utilitas'),
        ('PG', 'Perawatan Gedung'),
        ('OG', 'Operasional dan Kebersihan Gedung'),
        ('KS', 'Kebersihan dan Pengelolaan Sampah'),
        ('IA', 'Inventarisasi Aset'),
        ('PDA', 'Pendayagunaan Aset'),
        ('PHA', 'Penghapusan Aset'),
        ('PD', 'Penerimaan dan Distribusi'),
        ('S', 'Sekretariat'),
        ('D', 'Direktur'),
        ('WD', 'Wakil Direktur'),
        ('KAI', 'Kepala Subdit Pendayagunaan Aset dan Inventarisasi'),
        ('KO', 'Kepala Subdit Operasional dan Kebersihan'),
        ('KPA', 'Kepala Subdit Perawatan Aset'),
        ('SA', 'Superadmin'),
    )
    name = models.CharField(max_length=10, choices=ROLES)
    divisions = models.ManyToManyField(Division)

    def __str__(self):
        return dict(self.ROLES)[self.name]


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    origin = models.ForeignKey(Origin,on_delete=models.CASCADE)
    phone = models.CharField(max_length=20,default='')
    def __str__(self):
        return self.user.username

    def isSuperadmin(self):
        return self.role.name == 'SA'

    def isLeaderOf(self, complaint):
        return complaint.leader is None or complaint.leader in self.role.divisions.all()



class Complaint(models.Model):
    STATUS = (
        ('S', 'Submitted'),
        ('P', 'On Progress'),
        ('F', 'Finished')
    )
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    status = models.CharField(max_length=5, choices=STATUS,
                              null=False, blank=False, default='S')
    priority = models.PositiveIntegerField(default=1)
    assigned_divisions = models.ManyToManyField(Division, blank=True)
    reported = models.DateTimeField(default=timezone.now)
    is_public = models.BooleanField()
    leader = models.ForeignKey(Division, blank=True, null=True, related_name='leader', on_delete=models.PROTECT)

    def __str__(self):
        return self.title

    def get_status(self):
        return dict(self.STATUS)[self.status]

    def log_change(self, user, kind, description):
        log = Log(
            complaint=self,
            creator=user,
            kind=kind,
            description=description)
        log.save()


class Log(models.Model):
    KINDS = (
        ('G', 'Umum'),
        ('C', 'Pembuatan'),
        ('MD', 'Penandaan Selesai'),
        ('MP', 'Penandaan Progress'),
        ('AW', 'Penambahan Pekerja'),
        ('AC', 'Perubahan oleh Admin'),
        ('ACRMD', 'Perubahan oleh Admin, yang Menghilangkan Penandaan Selesai'),
    )

    creator = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(max_length=500)
    kind = models.CharField(max_length=10, choices=KINDS, default='G')

    def __str__(self):
        return self.description


class ComplaintImages(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    src = models.ImageField(upload_to=get_upload_path_images)
    log = models.ForeignKey(Log, blank=True, null=True, on_delete=models.PROTECT)


class Worker(models.Model):
    name = models.CharField(max_length=50)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'username']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'password': PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        super(UserForm, self).clean()

        password = self.cleaned_data['password']
        if len(password) < 8:
            self._errors['password'] = [u'Password minimal 8 karakter']

        return self.cleaned_data

class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
        }

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['role','phone','origin']
        exclude=['user']
        widgets = {
            'role': Select(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'origin': Select(attrs={'class':'form-control'}),
        }


class ComplaintCreateForm(ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'assigned_divisions', 'leader']
        widgets = {
            'location': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'location'}),
            'title': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'title'}),
            'assigned_divisions': CheckboxSelectMultiple(
                attrs={
                    'style': 'margin-right: 10px'}),
            'description': Textarea(
                attrs={
                    'class': 'form-control'}),
            'leader': Select(
                attrs={
                    'class': 'form-control'}),
        }
    def clean(self):
        super(ComplaintCreateForm, self).clean()
        leader = self.cleaned_data['leader']
        assigned_divisions = self.cleaned_data['assigned_divisions']
        isvalid = leader is None
        if not isvalid:
            for division in assigned_divisions:
                if division.name == leader.name:
                    isvalid = True

        if not isvalid:
            self._errors['leader'] = [u'Leader harus salah satu dari divisi yang dipilih']

        return self.cleaned_data



class ComplaintCreatePublicForm(ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description']
        widgets = {
            'location': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'location'}),
            'title': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'title'}),
            'assigned_divisions': CheckboxSelectMultiple(
                attrs={
                    'style': 'margin-right: 10px'}),
            'description': Textarea(
                attrs={
                    'class': 'form-control'}),
            'informer': TextInput(
                attrs={
                    'class': 'form-control'}),
            'leader': Select(
                attrs={
                    'class': 'form-control'}),
        }


class ComplaintEditForm(ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'title',
            'description',
            'assigned_divisions',
            'status',
            'reported',
            'priority',
            'leader']
        widgets = {
            'location': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'location'}),
            'title': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'title'}),
            'assigned_divisions': CheckboxSelectMultiple(
                attrs={
                    'style': 'margin-right: 10px'}),
            'description': Textarea(
                attrs={
                    'class': 'form-control'}),
            'informer': TextInput(
                attrs={
                    'class': 'form-control'}),
            'status': RadioSelect(
                attrs={
                    'style': 'margin-right: 10px'}),
            'priority': NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0}),
            'reported': DateTimeInput(
                attrs={
                    'class': 'form-control'}),
            'leader' : Select(
                attrs={
                    'class': 'form-control'})
        }
    def clean(self):
        super(ComplaintEditForm, self).clean()
        leader = self.cleaned_data['leader']
        assigned_divisions = self.cleaned_data['assigned_divisions']
        isvalid = leader is None
        if not isvalid:
            for division in assigned_divisions:
                if division.name == leader.name:
                    isvalid = True

        if not isvalid:
            self._errors['leader'] = [u'Leader harus salah satu dari divisi yang dipilih']

        return self.cleaned_data


class InformerForm(ModelForm):
    class Meta:
        model = Informer
        fields = ['name', 'email', 'phone_number', 'origin']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'phone_number': TextInput(attrs={'class': 'form-control'}),
            'origin': Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        super(InformerForm, self).clean()

        phone_number = self.cleaned_data['phone_number']
        try:
            validate_integer(phone_number)
        except BaseException:
            self._errors['phone_number'] = [
                u'Nomor telepon harus berupa angka']

        email = self.cleaned_data['email']
        try:
            validate_email(email)
        except BaseException:
            self._errors['email'] = [u'Email tidak valid']

        return self.cleaned_data


class InformerOriginForm(ModelForm):
    class Meta:
        model = InformerOrigin
        fields = ['master_origin', 'specific_origin']
        widgets = {
            'master_origin': Select(attrs={'class': 'form-control'}),
            'specific_origin': TextInput(attrs={'class': 'form-control'})
        }


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'lat', 'lon']
        widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control',
                    'id': 'location'}),
            'lat': NumberInput(attrs={'hidden': True, 'id': 'lat'}),
            'lon': NumberInput(attrs={'hidden': True, 'id': 'lng'}),
        }
