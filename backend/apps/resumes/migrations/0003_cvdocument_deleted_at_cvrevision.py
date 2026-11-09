from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("resumes", "0002_cvdocument_content_alter_cvdocument_design")]

    operations = [
        migrations.AddField(
            model_name="cvdocument",
            name="deleted_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.CreateModel(
            name="CVRevision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=160)),
                ("template", models.CharField(max_length=40)),
                ("design", models.JSONField(default=dict)),
                ("content", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="resumes.cvdocument")),
            ],
            options={
                "verbose_name": "CV revision",
                "verbose_name_plural": "CV revisions",
                "ordering": ["-version", "-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="cvrevision",
            constraint=models.UniqueConstraint(fields=("document", "version"), name="unique_cv_revision_version"),
        ),
    ]
