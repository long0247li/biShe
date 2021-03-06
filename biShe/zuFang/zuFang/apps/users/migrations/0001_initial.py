# Generated by Django 2.2.5 on 2020-12-07 05:10

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('mobile', models.CharField(max_length=11, unique=True, verbose_name='?????????')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='', verbose_name='????????????')),
                ('real_name', models.CharField(max_length=32, null=True, verbose_name='????????????')),
                ('id_card', models.CharField(max_length=20, null=True, verbose_name='????????????')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'tb_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='????????????')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='????????????')),
                ('name', models.CharField(max_length=32, verbose_name='????????????')),
            ],
            options={
                'db_table': 'tb_area',
            },
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='????????????')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='????????????')),
                ('name', models.CharField(max_length=32, verbose_name='????????????')),
            ],
            options={
                'db_table': 'tb_facility',
            },
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='????????????')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='????????????')),
                ('title', models.CharField(max_length=64, verbose_name='??????')),
                ('price', models.IntegerField(default=0)),
                ('address', models.CharField(default='', max_length=512)),
                ('room_count', models.IntegerField(default=1)),
                ('acreage', models.IntegerField(default=0)),
                ('unit', models.CharField(default='', max_length=32)),
                ('capacity', models.IntegerField(default=1)),
                ('beds', models.CharField(default='', max_length=64)),
                ('deposit', models.IntegerField(default=0)),
                ('min_days', models.IntegerField(default=1)),
                ('max_days', models.IntegerField(default=0)),
                ('order_count', models.IntegerField(default=0)),
                ('index_image_url', models.CharField(default='', max_length=256)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Area', verbose_name='????????????????????????')),
                ('facility', models.ManyToManyField(to='users.Facility', verbose_name='?????????????????????????????????')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='houses', to=settings.AUTH_USER_MODEL, verbose_name='???????????????????????????')),
            ],
            options={
                'db_table': 'tb_house',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='????????????')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='????????????')),
                ('begin_date', models.DateField(verbose_name='?????????????????????')),
                ('end_date', models.DateField(verbose_name='????????????')),
                ('days', models.IntegerField(verbose_name='??????????????????')),
                ('house_price', models.IntegerField(verbose_name='????????????')),
                ('amount', models.IntegerField(verbose_name='???????????????')),
                ('status', models.SmallIntegerField(choices=[(0, 'WAIT_ACCEPT'), (1, 'WAIT_PAYMENT'), (2, 'PAID'), (3, 'WAIT_COMMENT'), (4, 'COMPLETE'), (5, 'CANCELED'), (6, 'REJECTED')], db_index=True, default=0, verbose_name='????????????')),
                ('comment', models.TextField(null=True, verbose_name='???????????????????????????????????????')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.House', verbose_name='?????????????????????')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='????????????????????????')),
            ],
            options={
                'db_table': 'tb_order',
            },
        ),
        migrations.CreateModel(
            name='HouseImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='????????????')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='????????????')),
                ('url', models.CharField(max_length=256)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.House')),
            ],
            options={
                'db_table': 'tb_house_image',
            },
        ),
    ]
