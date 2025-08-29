API reference
=============

.. module:: ydtpack

.. autofunction:: pack

:func:`dump` is alias for :func:`pack`

.. autofunction:: packb

:func:`dumps` is alias for :func:`packb`

.. autofunction:: unpack

:func:`load` is alias for :func:`unpack`

.. autofunction:: unpackb

:func:`loads` is alias for :func:`unpackb`

.. autoclass:: Packer
    :members:

.. autoclass:: Unpacker
    :members:

.. autoclass:: ExtType

.. autoclass:: Timestamp
    :members:
    :special-members: __init__

exceptions
----------

These exceptions are accessible via `ydtpack` package.
(For example, `ydtpack.OutOfData` is shortcut
for `ydtpack.exceptions.OutOfData`)

.. automodule:: ydtpack.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
