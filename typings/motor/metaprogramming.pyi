"""
This type stub file was generated by pyright.
"""

"""Dynamic class-creation for Motor."""
_class_cache = ...
def asynchronize(framework, sync_method, doc=..., wrap_class=..., unwrap_class=...): # -> (self: Unknown, *args: Unknown, **kwargs: Unknown) -> Unknown:
    """Decorate `sync_method` so it returns a Future.

    The method runs on a thread and resolves the Future when it completes.

    :Parameters:
     - `motor_class`:       Motor class being created, e.g. MotorClient.
     - `framework`:         An asynchronous framework
     - `sync_method`:       Unbound method of pymongo Collection, Database,
                            MongoClient, etc.
     - `doc`:               Optionally override sync_method's docstring
     - `wrap_class`:        Optional PyMongo class, wrap a returned object of
                            this PyMongo class in the equivalent Motor class
     - `unwrap_class`       Optional Motor class name, unwrap an argument with
                            this Motor class name and pass the wrapped PyMongo
                            object instead
    """
    ...

def unwrap_args_session(args): # -> Generator[Unknown, None, None]:
    ...

def unwrap_kwargs_session(kwargs): # -> dict[Unknown, Unknown]:
    ...

_coro_token = ...
def coroutine_annotation(f):
    """In docs, annotate a function that returns a Future with 'coroutine'.

    This doesn't affect behavior.
    """
    ...

class MotorAttributeFactory:
    """Used by Motor classes to mark attributes that delegate in some way to
    PyMongo. At module import time, create_class_with_framework calls
    create_attribute() for each attr to create the final class attribute.
    """
    def __init__(self, doc=...) -> None:
        ...
    
    def create_attribute(self, cls, attr_name):
        ...
    


class Async(MotorAttributeFactory):
    def __init__(self, attr_name, doc=...) -> None:
        """A descriptor that wraps a PyMongo method, such as insert_one,
        and returns an asynchronous version of the method that returns a Future.

        :Parameters:
         - `attr_name`: The name of the attribute on the PyMongo class, if
           different from attribute on the Motor class
        """
        ...
    
    def create_attribute(self, cls, attr_name): # -> (self: Unknown, *args: Unknown, **kwargs: Unknown) -> Unknown:
        ...
    
    def wrap(self, original_class): # -> Self@Async:
        ...
    
    def unwrap(self, class_name): # -> Self@Async:
        ...
    


class AsyncRead(Async):
    def __init__(self, attr_name=..., doc=...) -> None:
        """A descriptor that wraps a PyMongo read method like find_one() that
        returns a Future.
        """
        ...
    


class AsyncWrite(Async):
    def __init__(self, attr_name=..., doc=...) -> None:
        """A descriptor that wraps a PyMongo write method like update_one() that
        accepts getLastError options and returns a Future.
        """
        ...
    


class AsyncCommand(Async):
    def __init__(self, attr_name=..., doc=...) -> None:
        """A descriptor that wraps a PyMongo command like copy_database() that
        returns a Future and does not accept getLastError options.
        """
        ...
    


class ReadOnlyProperty(MotorAttributeFactory):
    """Creates a readonly attribute on the wrapped PyMongo object."""
    def create_attribute(self, cls, attr_name): # -> property:
        ...
    


class DelegateMethod(ReadOnlyProperty):
    """A method on the wrapped PyMongo object that does no I/O and can be called
    synchronously"""
    def __init__(self, doc=...) -> None:
        ...
    
    def wrap(self, original_class): # -> Self@DelegateMethod:
        ...
    
    def create_attribute(self, cls, attr_name): # -> property | ((self_: Unknown, *args: Unknown, **kwargs: Unknown) -> (Unknown | Any)):
        ...
    


class MotorCursorChainingMethod(MotorAttributeFactory):
    def create_attribute(self, cls, attr_name): # -> (self: Unknown, *args: Unknown, **kwargs: Unknown) -> Unknown:
        ...
    


def create_class_with_framework(cls, framework, module_name): # -> Type[_]:
    ...
