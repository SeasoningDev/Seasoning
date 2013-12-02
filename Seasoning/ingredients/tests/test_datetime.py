import datetime as datetime_orig

class TestDatetime(object):
    """
    A datetime stub object to replace methods and classes from 
    the datetime module. 

    Usage:
        import models # your module with the model that uses datetime
        import test_datetime
        
        models.datetime = test_datetime.TestDateTime()
    """
    class date(datetime_orig.date):
        
        @classmethod
        def today(cls):
            """Override the datetime.now() method to return a
            datetime one year in the future
            """
            return datetime_orig.date(2013,5,5)
        
    def __getattr__(self, attr):
        """Get the default implementation for the classes and methods
        from datetime that are not replaced
        """
        return getattr(datetime_orig, attr)