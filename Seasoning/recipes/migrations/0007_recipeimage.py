# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import general
import recipes.models
import imagekit.models.fields
from django.conf import settings

def create_image_models(apps, schema_editor):
    """
    Create a default RecipeImage model for each recipe before deleting the image
    fields from the recipe models
    
    """
    all_recipes = recipes.models.Recipe.objects.all()
    for recipe in all_recipes:
        default_image = recipes.models.RecipeImage(recipe=recipe,
                                                   image=recipe.image,
                                                   added_by=recipe.author)
        default_image.save()

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_auto_20141007_2138'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', imagekit.models.fields.ProcessedImageField(default=b'images/no_image.jpg', help_text='An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.', upload_to=recipes.models.get_image_filename, validators=[general.validate_image_size])),
                ('added_by', models.ForeignKey(related_name=b'recipe_images', to=settings.AUTH_USER_MODEL)),
                ('recipe', models.ForeignKey(related_name=b'images', to='recipes.Recipe')),
                ('incomplete_recipe', models.ForeignKey(related_name=b'images', to='recipes.IncompleteRecipe')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(create_image_models)
    ]
