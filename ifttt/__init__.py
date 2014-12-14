from core import IfThat

def ifthat(subject, **dkwargs):
    """
    a decorator for
    listen to an email subject and emit messages 
    to a callback via decorator
    """
    # wrapper
    def wrapper(f):

    	from functools import wraps 

        @wraps(f)
        def wrapped_func():

            class _T(IfThat):

                def __init__(self):
                    IfThat.__init__(self, subject, **dkwargs)

                def thenthis(self, message):
                    return f(message)

            return _T().run()

        return wrapped_func

    return wrapper
