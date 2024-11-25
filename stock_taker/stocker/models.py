from django.db import models

class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    storage = models.ForeignKey('Storage', models.DO_NOTHING, blank=True, null=True)
    quantity_activity = models.IntegerField(blank=True, null=True)
    date_used = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)



class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Icategory(models.Model):
    icategory_id = models.AutoField(primary_key=True)
    icategory_name = models.CharField(unique=True, max_length=100)
    icategory_des = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'icategory'


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(unique=True, max_length=100)
    icategory = models.ForeignKey(Icategory, models.DO_NOTHING, blank=True, null=True)
    item_quantity = models.IntegerField(blank=True, null=True)
    notifibool = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item'


class Lcategory(models.Model):
    lcategory_id = models.AutoField(primary_key=True)
    lcategory_name = models.CharField(unique=True, max_length=100)
    lcategory_des = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lcategory'


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(unique=True, max_length=100)
    x = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    y = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    z = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lcategory = models.ForeignKey(Lcategory, models.DO_NOTHING, blank=True, null=True)
    e_n_h = models.CharField(db_column='E_N_H', max_length=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'location'


class Storage(models.Model):
    storage_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=4, blank=True, null=True)
    quantity_stored = models.IntegerField(blank=True, null=True)
    stored_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'storage'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    role = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'