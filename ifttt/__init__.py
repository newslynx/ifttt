from core import IfThat, linter 

def ifthat(subject, **dkwargs):
    """
    a decorator to modi listen to an email subject and endlessly emit messages 
    to the custom function.

        from ifttt import ifthat

        @ifthat('twitter', pattern = "{{UserName}}|||||{{LinkToTweet}}|||||{{Text}}|||||")
        def twitter(msg):
            import os 
            os.system('tweet from {text}'.format(**msg['body']))
            return msg

        for msg in twitter():
            print msg

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
