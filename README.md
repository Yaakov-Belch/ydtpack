# tmsgpack: Typed MessagePack-inspired pack/unpack component

The tmsgpack format expresses **typed objects**: maps and arrays (or: dicts and lists)
with an `object_type` property.

Unlike msgpack and pickle, this is not a batteries-included end-to-end serialization
solution.  It is a composable component that helps you to build end-to-end communication
solutions.

Your system solution design will make decisions on:
* What objects are serializable and what objects are not.
* What code to use (and, maybe, dynamically load) to unpack serialized object.
* How to represent objects that are unpacked but not supposed to 'live' in this process.
* How to share dynamic data between different packs/unpacks.
* How to asynchronously load and integrate shared data from different sources.
* How to map typed object meaning between different programming languages.
* Whether and how to convert persisted "old" data to current, new semantics (schemas).
* How much to attach explicit meaning and predictable schemas to your object types.
* Whether or not to use the 'expression execution' capabilities of tmsgpack.
* etc.


## Development: Environment and testing

```
# Create a virtual environment in your project directory
cd ~/git/tmsgpack
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install the required dependencies
pip install -r requirements.txt

# Now you can run the tests
make test

# Run one test
pytest -v test/test_typed_objects.py
```

