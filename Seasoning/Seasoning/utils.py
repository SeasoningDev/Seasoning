# Used for testing with dynamic fixtures
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import SequentialDataFixture

class UserNamesOverwriter(SequentialDataFixture):
    def charfield_config(self, field, key):
        if field.name == 'surname':
            return 'test'
        if field.name == 'givenname':
            return 'user'
        return super(UserNamesOverwriter, self).charfield_config(field, key)