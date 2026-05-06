from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pe_surveys', '0003_alter_surveyoption_options_remove_surveyoption_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='event',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='surveys',
                to='in_person_events.event',
                verbose_name='Evento'
            ),
        ),
    ]