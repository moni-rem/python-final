from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE courses_course SET price = 0.00;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
