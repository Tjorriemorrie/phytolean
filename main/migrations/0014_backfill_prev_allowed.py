from django.db import migrations


def backfill_prev_allowed(apps, schema_editor):
    Status = apps.get_model('main', 'Status')  # <-- Status model, not Psychic
    db_alias = schema_editor.connection.alias

    from django.db.models import F, Window
    from django.db.models.functions import Lag

    # annotate each Status row with the previous status for the same psychic
    qs = (
        Status.objects.using(db_alias)
        .annotate(prev_status=Window(
            expression=Lag('status'),
            partition_by=[F('psychic_id')],
            order_by=F('status_at').asc()
        ))
    )

    updates = []
    for row in qs.iterator(chunk_size=2000):
        allowed = row.prev_status in (1, 2)  # replace with your constants
        if getattr(row, 'prev_allowed', None) != allowed:
            row.prev_allowed = allowed
            updates.append(row)

    from django.db import transaction
    with transaction.atomic(using=db_alias):
        Status.objects.using(db_alias).bulk_update(updates, ['prev_allowed'], batch_size=2000)


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0013_status_prev_allowed'),  # migration that added prev_allowed to Status
    ]

    operations = [
        migrations.RunPython(backfill_prev_allowed, reverse_code=migrations.RunPython.noop),
    ]
