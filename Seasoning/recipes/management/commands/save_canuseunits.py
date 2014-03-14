from django.core.management.base import NoArgsCommand
from ingredients.models import CanUseUnit

class Command(NoArgsCommand):
    def handle_noargs(self):
        """
        This command is only here for the transition of the old useable_units system to the new one
        
        It saves all canuseunits so that all child unit will also be added to ingredients made before
        the change
        
        """
        for canuseunit in CanUseUnit.objects.all():
            canuseunit.save()