from django.core.management.base import NoArgsCommand
from recipes.models import Aggregate

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        Recalculate the denormalized aggregate values of all recipes.
        
        """
        Aggregate.objects.update_fp_categories()
        Aggregate.objects.update_fp_statistics()